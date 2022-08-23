import glob
import os
import tables as tb
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import ipywidgets as widgets
from IPython.display import clear_output
from ast import literal_eval

from scipy.fftpack import fftn, ifftn, fftshift, fftfreq
from scipy.ndimage import center_of_mass

from bcdi.postprocessing.postprocessing_runner import run as run_postprocessing
from bcdi.utils.parser import ConfigParser

# from pynx.utils import phase_retrieval_transfer_function

from gwaihir import plot
from gwaihir.controller.control_preprocess import create_yaml_file


def init_postprocess_tab(
    interface,
    unused_label_averaging,
    sort_method,
    correlation_threshold,
    unused_label_FFT,
    phasing_binning,
    original_size,
    preprocessing_binning,
    output_size,
    keep_size,
    fix_voxel,
    unused_label_disp_strain,
    data_frame,
    save_frame,
    ref_axis_q,
    isosurface_strain,
    skip_unwrap,
    strain_method,
    phase_offset,
    phase_offset_origin,
    offset_method,
    centering_method_direct_space,
    unused_label_refraction,
    correct_refraction,
    optical_path_method,
    dispersion,
    absorption,
    threshold_unwrap_refraction,
    unused_label_options,
    simulation,
    invert_phase,
    flip_reconstruction,
    phase_ramp_removal,
    threshold_gradient,
    save_raw,
    save_support,
    save,
    debug,
    roll_modes,
    unused_label_data_vis,
    align_axis,
    ref_axis,
    axis_to_align,
    strain_range,
    phase_range,
    grey_background,
    tick_spacing,
    tick_direction,
    tick_length,
    tick_width,
    unused_label_average,
    averaging_space,
    threshold_avg,
    unused_label_apodize,
    apodize,
    apodization_window,
    half_width_avg_phase,
    apodization_mu,
    apodization_sigma,
    apodization_alpha,
    unused_label_strain,
    strain_folder,
    reconstruction_file,
    init_postprocess_parameters,
):
    """
    Interpolate the output of the phase retrieval into an orthonormal frame,
    and calculate the strain component along the direction of the
    experimental diffusion vector q.

    Input: complex amplitude array, output from a phase retrieval program.
    Output: data in an orthonormal frame (laboratory or crystal frame),
    amp_disp_strain array.The disp array should be divided by q to get the
    displacement (disp = -1*phase here).

    Laboratory frame: z downstream, y vertical, x outboard (CXI convention)
    Crystal reciprocal frame: qx downstream, qz vertical, qy outboard
    Detector convention: when out_of_plane angle=0   Y=-y , when in_plane
    angle=0   X=x

    In arrays, when plotting the first parameter is the row (vertical axis),
    and the second the column (horizontal axis). Therefore the data
    structure is data[qx, qz, qy] for reciprocal space, or data[z, y, x]
    for real space.

    Loading argument from strain tab widgets but also values of
    parameters used in preprocessing that are common.

    Parameters used when averaging several reconstruction:

    :param sort_method: e.g. "variance/mean"
     'mean_amplitude' or 'variance' or 'variance/mean' or 'volume',
     metric for averaging
    :param averaging_space: e.g. "reciprocal_space" TODO
     in which space to average, 'direct_space' or 'reciprocal_space'
    :param correlation_threshold: e.g. 0.90
     minimum correlation between two arrays to average them

    Parameters related to centering:

    :param centering_method_direct_space: e.g. "max_com"
    'com' (center of mass), 'max', 'max_com' (max then com), 'do_nothing'
    :param roll_modes: e.g. [0, 0, 0]
    correct a roll of few pixels after the decomposition into modes in PyNX
    axis=(0, 1, 2)

    Parameters relative to the FFT window and voxel sizes:

    :param original_size: e.g. [150, 256, 500]
     size of the FFT array before binning. It will be modified to take
     into account binning during phasing automatically. Leave it to None
     if the shape did not change.
    :param phasing_binning: e.g. [1, 1, 1]
     binning factor applied during phase retrieval
    :param preprocessing_binning: e.g. [1, 2, 2]
     binning factors in each dimension used in preprocessing (not phase
     retrieval)
    :param output_size: e.g. [100, 100, 100]
     (z, y, x) Fix the size of the output array, leave None to use the
     object size
    :param keep_size: e.g. False
     True to keep the initial array size for orthogonalization (slower),
     it will be cropped otherwise
    :param fix_voxel: e.g. 10
     voxel size in nm for the interpolation during the geometrical
     transformation. If a single value is provided, the voxel size will be
     identical in all 3 directions. Set it to None to use the default voxel
     size (calculated from q values, it will be different in each
     dimension).

    Parameters related to the strain calculation:

    :param data_frame: e.g. "detector"
     in which frame is defined the input data, available options:

     - 'crystal' if the data was interpolated into the crystal frame using
       xrayutilities or (transformation matrix + align_q=True)
     - 'laboratory' if the data was interpolated into the laboratory frame
       using the transformation matrix (align_q: False)
     - 'detector' if the data is still in the detector frame

    :param ref_axis_q: e.g. "y"
     axis along which q will be aligned (data_frame= 'detector' or
     'laboratory') or is already aligned (data_frame='crystal')
    :param save_frame: e.g. "laboratory"
     in which frame should be saved the data, available options:

     - 'crystal' to save the data with q aligned along ref_axis_q
     - 'laboratory' to save the data in the laboratory frame (experimental
       geometry)
     - 'lab_flat_sample' to save the data in the laboratory frame, with
       all sample angles rotated back to 0. The rotations for 'laboratory'
       and 'lab_flat_sample' are realized after the strain calculation
       (which is always done in the crystal frame along ref_axis_q)

    :param isosurface_strain: e.g. 0.2
     threshold use for removing the outer layer (the strain is undefined
     at the exact surface voxel)
    :param skip_unwrap: e.g. False
     If 'skip_unwrap', it will not unwrap the phase. It can be used when there is a
     defect and phase unwrapping does not work well.
    :param strain_method: e.g. "default"
     how to calculate the strain, available options:

     - 'default': use the single value calculated from the gradient of
       the phase
     - 'defect': it will offset the phase in a loop and keep the smallest
       magnitude value for the strain.
       See: F. Hofmann et al. PhysRevMaterials 4, 013801 (2020)

    Parameters related to the refraction correction:

    :param correct_refraction: e.g. True
     True for correcting the phase shift due to refraction
    :param optical_path_method: e.g. "threshold"
     'threshold' or 'defect', if 'threshold' it uses isosurface_strain to
     define the support  for the optical path calculation, if 'defect'
     (holes) it tries to remove only outer layers even if the amplitude is
     lower than isosurface_strain inside the crystal
    :param dispersion: e.g. 5.0328e-05
     delta value used for refraction correction, for Pt:
     3.0761E-05 @ 10300eV, 5.0328E-05 @ 8170eV, 3.2880E-05 @ 9994eV,
     4.1184E-05 @ 8994eV, 5.2647E-05 @ 7994eV, 4.6353E-05 @ 8500eV
     Ge 1.4718E-05 @ 8keV
    :param absorption: e.g. 4.1969e-06
     beta value, for Pt:  2.0982E-06 @ 10300eV, 4.8341E-06 @ 8170eV,
     2.3486E-06 @ 9994eV, 3.4298E-06 @ 8994eV, 5.2245E-06 @ 7994eV,
     4.1969E-06 @ 8500eV
    :param threshold_unwrap_refraction: e.g. 0.05
     threshold used to calculate the optical path. The threshold for
     refraction correction should be low, to correct for an object larger
     than the real one, otherwise it messes up the phase

    Parameters related to the phase:

    :param simulation: e.g. False
     True if it is a simulation, the parameter invert_phase will be set
     to 0 (see below)
    :param invert_phase: e.g. True
    True for the displacement to have the right sign (FFT convention),
    it is False only for simulations
    :param flip_reconstruction: e.g. True
     True if you want to get the conjugate object
    :param phase_ramp_removal: e.g. "gradient"
     'gradient' or 'upsampling', 'gradient' is much faster
    :param threshold_gradient: e.g. 1.0
     upper threshold of the gradient of the phase, use for ramp removal
    :param phase_offset: e.g. 0
     manual offset to add to the phase, should be 0 in most cases
    :param phase_offset_origin: e.g. [12, 32, 65]
     the phase at this voxel will be set to phase_offset, leave None to
     use the default position computed using offset_method (see below)
    :param offset_method: e.g. "mean"
     'com' (center of mass) or 'mean', method for determining the phase
     offset origin

    Parameters related to data visualization:

    :param debug: e.g. False
     True to show all plots for debugging
    :param align_axis: e.g. False
     True to rotate the crystal to align axis_to_align along ref_axis for
     visualization. This is done after the calculation of the strain and
     has no effect on it.
    :param ref_axis: e.g. "y"
     it will align axis_to_align to that axis if align_axis is True
    :param axis_to_align: e.g. [-0.01166, 0.9573, -0.2887]
     axis to align with ref_axis in the order x y z (axis 2, axis 1,
     axis 0)
    :param strain_range: e.g. 0.001
     range of the colorbar for strain plots
    :param phase_range: e.g. 0.4
     range of the colorbar for phase plots
    :param grey_background: e.g. True
     True to set the background to grey in phase and strain plots
    :param tick_spacing: e.g. 50
     spacing between axis ticks in plots, in nm
    :param tick_direction: e.g. "inout"
     direction of the ticks in plots: 'out', 'in', 'inout'
    :param tick_length: e.g. 3
     length of the ticks in plots
    :param tick_width: e.g. 1
     width of the ticks in plots

    Parameters for averaging several reconstructed objects:

    :param averaging_space: e.g. "reciprocal_space"
     in which space to average, 'direct_space' or 'reciprocal_space'
    :param threshold_avg: e.g. 0.90
     minimum correlation between arrays for averaging

    Parameters for phase averaging or apodization:

    :param half_width_avg_phase: e.g. 0
     (width-1)/2 of the averaging window for the phase, 0 means no phase
     averaging
    :param apodize: e.g. False
     True to multiply the diffraction pattern by a filtering window
    :param apodization_window: e.g. "blackman"
     filtering window, multivariate 'normal' or 'tukey' or 'blackman'
    :param apodization_mu: e.g. [0.0, 0.0, 0.0]
     mu of the gaussian window
    :param apodization_sigma: e.g. [0.30, 0.30, 0.30]
     sigma of the gaussian window
    :param apodization_alpha: e.g. [1.0, 1.0, 1.0]
     shape parameter of the tukey window

    Parameters related to saving:

    :param save_rawdata: e.g. False
     True to save the amp-phase.vti before orthogonalization
    :param save_support: e.g. False
     True to save the non-orthogonal support for later phase retrieval
    :param save: e.g. True
     True to save amp.npz, phase.npz, strain.npz and vtk files
    """
    # Save parameter values
    # parameters used when averaging several reconstruction #
    interface.Dataset.sort_method = sort_method
    interface.Dataset.correlation_threshold = correlation_threshold
    # parameters relative to the FFT window and voxel sizes #
    interface.Dataset.phasing_binning = phasing_binning
    interface.Dataset.original_size = original_size
    interface.Dataset.preprocessing_binning = preprocessing_binning
    interface.Dataset.output_size = output_size
    interface.Dataset.keep_size = keep_size
    interface.Dataset.fix_voxel = fix_voxel
    # parameters related to displacement and strain calculation #
    interface.Dataset.data_frame = data_frame
    interface.Dataset.save_frame = save_frame
    interface.Dataset.ref_axis_q = ref_axis_q
    interface.Dataset.isosurface_strain = isosurface_strain
    interface.Dataset.skip_unwrap = skip_unwrap
    interface.Dataset.strain_method = strain_method
    interface.Dataset.phase_offset = phase_offset
    interface.Dataset.phase_offset_origin = phase_offset_origin
    interface.Dataset.offset_method = offset_method
    interface.Dataset.centering_method_direct_space = centering_method_direct_space
    # parameters related to the refraction correction
    interface.Dataset.correct_refraction = correct_refraction
    interface.Dataset.optical_path_method = optical_path_method
    interface.Dataset.dispersion = dispersion
    interface.Dataset.absorption = absorption
    interface.Dataset.threshold_unwrap_refraction\
        = threshold_unwrap_refraction
    # options #
    interface.Dataset.simulation = simulation
    interface.Dataset.invert_phase = invert_phase
    interface.Dataset.flip_reconstruction = flip_reconstruction
    interface.Dataset.phase_ramp_removal = phase_ramp_removal
    interface.Dataset.threshold_gradient = threshold_gradient
    interface.Dataset.save_raw = save_raw
    interface.Dataset.save_support = save_support
    interface.Dataset.save = save
    interface.Dataset.debug = debug
    interface.Dataset.roll_modes = roll_modes
    # parameters related to data visualization #
    interface.Dataset.align_axis = align_axis
    interface.Dataset.ref_axis = ref_axis
    interface.Dataset.axis_to_align = axis_to_align
    interface.Dataset.strain_range = strain_range
    interface.Dataset.phase_range = phase_range
    interface.Dataset.grey_background = grey_background
    interface.Dataset.tick_spacing = tick_spacing
    interface.Dataset.tick_direction = tick_direction
    interface.Dataset.tick_length = tick_length
    interface.Dataset.tick_width = tick_width
    # parameters for averaging several reconstructed objects #
    interface.Dataset.averaging_space = averaging_space
    interface.Dataset.threshold_avg = threshold_avg
    # setup for phase averaging or apodization
    interface.Dataset.half_width_avg_phase = half_width_avg_phase
    interface.Dataset.apodize = apodize
    interface.Dataset.apodization_window = apodization_window
    interface.Dataset.apodization_mu = apodization_mu
    interface.Dataset.apodization_sigma = apodization_sigma
    interface.Dataset.apodization_alpha = apodization_alpha
    interface.Dataset.reconstruction_file = strain_folder + reconstruction_file
    if os.path.isfile(str(interface.Dataset.reconstruction_file)):
        print(
            "\n###########################################"
            "#############################################"
            "\nReconstruction file used to save phase "
            "retrieval results in the final .cxi file:"
            f"\n\t{os.path.split(interface.Dataset.reconstruction_file)[0]}"
            f"\n\t{os.path.split(interface.Dataset.reconstruction_file)[1]}"
            "\n###########################################"
            "#############################################"
        )

    if init_postprocess_parameters == "run_strain":
        # Save directory
        save_dir = f"{interface.postprocessing_folder}/" + \
            f"result_{interface.Dataset.save_frame}/"

        # Disable all widgets until the end of the program
        for w in interface.TabPostprocess.children[:-1]:
            if isinstance(w, widgets.VBox) or isinstance(w, widgets.HBox):
                for wc in w.children:
                    wc.disabled = True
            elif isinstance(w, widgets.HTML):
                pass
            else:
                w.disabled = True

        for w in interface.TabPreprocess.children[:-1]:
            if isinstance(w, widgets.VBox) or isinstance(w, widgets.HBox):
                for wc in w.children:
                    wc.disabled = True
            elif isinstance(w, widgets.HTML):
                pass
            else:
                w.disabled = True

        # Extract dict, list and tuple from strings
        list_parameters = [
            "original_size", "output_size", "axis_to_align",
            "apodization_mu", "apodization_sigma", "apodization_alpha"]

        tuple_parameters = [
            "phasing_binning", "preprocessing_binning",
            "phase_offset_origin", "roll_modes"]

        try:
            for p in list_parameters:
                if getattr(interface.Dataset, p) == "":
                    setattr(interface.Dataset, p, [])
                else:
                    setattr(interface.Dataset, p, literal_eval(
                        getattr(interface.Dataset, p)))
        except ValueError:
            print(f"Wrong list syntax for {p}")

        try:
            for p in tuple_parameters:
                if getattr(interface.Dataset, p) == "":
                    setattr(interface.Dataset, p, ())
                else:
                    setattr(interface.Dataset, p, literal_eval(
                        getattr(interface.Dataset, p)))
        except ValueError:
            print(f"Wrong tuple syntax for {p}")

        # Empty parameters are set to None (bcdi syntax)
        if interface.Dataset.output_size == []:
            interface.Dataset.output_size = None

        if interface.Dataset.fix_voxel == 0:
            interface.Dataset.fix_voxel = None

        if interface.Dataset.phase_offset_origin == ():
            interface.Dataset.phase_offset_origin = (None)

        # Change data_dir and root folder depending on beamline
        if interface.Dataset.beamline == "SIXS_2019":
            root_folder = interface.Dataset.root_folder
            data_dir = interface.Dataset.data_dir

        elif interface.Dataset.beamline == "P10":
            root_folder = interface.Dataset.data_dir
            data_dir = None

        else:
            root_folder = interface.Dataset.root_folder
            data_dir = interface.Dataset.data_dir

        # Create centering_method dict
        centering_method = {
            "direct_space": interface.Dataset.centering_method_direct_space,
            "reciprocal_space": interface.Dataset.centering_method_reciprocal_space,
        }

        try:
            create_yaml_file(
                fname=f"{interface.postprocessing_folder}/config_postprocessing.yml",
                scans=interface.Dataset.scan,
                root_folder=root_folder,
                save_dir=save_dir,
                data_dir=data_dir,
                sample_name=interface.Dataset.sample_name,
                comment=interface.Dataset.comment,
                reconstruction_files=interface.Dataset.reconstruction_file,  # keep s here
                backend=interface.matplotlib_backend,
                # parameters used when averaging several reconstruction #
                sort_method=interface.Dataset.sort_method,
                averaging_space=interface.Dataset.averaging_space,
                correlation_threshold=interface.Dataset.correlation_threshold,
                # parameters related to centering #
                centering_method=centering_method,
                roll_modes=interface.Dataset.roll_modes,
                # parameters relative to the FFT window and voxel sizes #
                original_size=interface.Dataset.original_size,
                phasing_binning=interface.Dataset.phasing_binning,
                preprocessing_binning=interface.Dataset.preprocessing_binning,
                output_size=interface.Dataset.output_size,
                keep_size=interface.Dataset.keep_size,
                fix_voxel=interface.Dataset.fix_voxel,
                # parameters related to the strain calculation #
                data_frame=interface.Dataset.data_frame,
                ref_axis_q=interface.Dataset.ref_axis_q,
                save_frame=interface.Dataset.save_frame,
                isosurface_strain=interface.Dataset.isosurface_strain,
                skip_unwrap=interface.Dataset.skip_unwrap,
                strain_method=interface.Dataset.strain_method,
                # define beamline related parameters #
                beamline=interface.Dataset.beamline,
                is_series=interface.Dataset.is_series,
                actuators=interface.Dataset.actuators,
                # setup for custom scans #
                custom_scan=interface.Dataset.custom_scan,
                custom_images=interface.Dataset.custom_images,
                custom_monitor=interface.Dataset.custom_monitor,
                rocking_angle=interface.Dataset.rocking_angle,
                detector_distance=interface.Dataset.detector_distance,
                energy=interface.Dataset.energy,
                beam_direction=interface.Dataset.beam_direction,
                sample_offsets=interface.Dataset.sample_offsets,
                tilt_angle=interface.Dataset.tilt_angle,
                direct_beam=interface.Dataset.direct_beam,
                dirbeam_detector_angles=interface.Dataset.dirbeam_detector_angles,
                bragg_peak=interface.Dataset.bragg_peak,
                outofplane_angle=interface.Dataset.outofplane_angle,
                inplane_angle=interface.Dataset.inplane_angle,
                specfile_name=interface.Dataset.specfile_name,
                # detector related parameters #
                detector=interface.Dataset.detector,
                roi_detector=interface.Dataset.roi_detector,
                template_imagefile=interface.Dataset.template_imagefile,
                # parameters related to the refraction correction #
                correct_refraction=interface.Dataset.correct_refraction,
                optical_path_method=interface.Dataset.optical_path_method,
                dispersion=interface.Dataset.dispersion,
                absorption=interface.Dataset.absorption,
                threshold_unwrap_refraction=interface.Dataset.threshold_unwrap_refraction,
                # parameters related to the phase #
                simulation=interface.Dataset.simulation,
                invert_phase=interface.Dataset.invert_phase,
                flip_reconstruction=interface.Dataset.flip_reconstruction,
                phase_ramp_removal=interface.Dataset.phase_ramp_removal,
                threshold_gradient=interface.Dataset.threshold_gradient,
                phase_offset=interface.Dataset.phase_offset,
                phase_offset_origin=interface.Dataset.phase_offset_origin,
                offset_method=interface.Dataset.offset_method,
                # parameters related to data visualization #
                debug=interface.Dataset.debug,
                align_axis=interface.Dataset.align_axis,
                ref_axis=interface.Dataset.ref_axis,
                axis_to_align=interface.Dataset.axis_to_align,
                strain_range=interface.Dataset.strain_range,
                phase_range=interface.Dataset.phase_range,
                grey_background=interface.Dataset.grey_background,
                tick_spacing=interface.Dataset.tick_spacing,
                tick_direction=interface.Dataset.tick_direction,
                tick_length=interface.Dataset.tick_length,
                tick_width=interface.Dataset.tick_width,
                # parameters for temperature estimation #
                # get_temperature=interface.Dataset.get_temperature,
                # reflection=interface.Dataset.reflection,
                # reference_spacing=interface.Dataset.reference_spacing,
                # reference_temperature=interface.Dataset.reference_temperature,
                # parameters for phase averaging or apodization #
                half_width_avg_phase=interface.Dataset.half_width_avg_phase,
                apodize=interface.Dataset.apodize,
                apodization_window=interface.Dataset.apodization_window,
                apodization_mu=interface.Dataset.apodization_mu,
                apodization_sigma=interface.Dataset.apodization_sigma,
                apodization_alpha=interface.Dataset.apodization_alpha,
                # parameters related to saving #
                save_rawdata=interface.Dataset.save_rawdata,
                save_support=interface.Dataset.save_support,
                save=interface.Dataset.save,
            )
            # Run bcdi_postprocessing
            print(
                "\n###########################################"
                "#############################################"
            )
            print(f"Running: $ {interface.path_scripts}/bcdi_strain.py")
            print(
                f"Config file: {interface.postprocessing_folder}/config_postprocessing.yml")
            print(
                "\n###########################################"
                "#############################################"
            )

            # Load the config file
            config_file = interface.postprocessing_folder + "/config_postprocessing.yml"
            parser = ConfigParser(config_file)
            args = parser.load_arguments()
            args["time"] = f"{datetime.now()}"

            # Run function
            run_postprocessing(prm=args)
            print("End of script")

            # Get data from saved file
            phase_fieldname = "disp" if interface.Dataset.invert_phase else "phase"

            files = sorted(
                glob.glob(
                    f"{interface.postprocessing_folder}/**/"
                    f"{interface.Dataset.scan_name}_amp{phase_fieldname}"
                    f"strain*{interface.Dataset.comment}.h5",
                    recursive=True),
                key=os.path.getmtime)
            interface.Dataset.postprocessing_output_file = files[0]

            creation_time = datetime.fromtimestamp(
                os.path.getmtime(interface.Dataset.postprocessing_output_file)
            ).strftime('%Y-%m-%d %H:%M:%S')

            print(
                "\n###########################################"
                "#############################################"
                f"\nResult file used to extract results saved in the .cxi file:"
                f"\n{interface.Dataset.postprocessing_output_file}"
                f"\n\tCreated: {creation_time}"
                "\nMake sure it is the latest one!!"
                "\n###########################################"
                "#############################################"
            )

        except KeyboardInterrupt:
            print("Strain analysis stopped by user ...")

        finally:
            # Refresh folders
            interface.root_folder_handler(
                change=interface.Dataset.scan_folder
            )

            # PyNX folder
            interface.TabPhaseRetrieval.parent_folder.value\
                = interface.preprocessing_folder
            interface.TabPhaseRetrieval.pynx_folder_handler(
                change=interface.preprocessing_folder
            )

            # Plot folder
            interface.TabPlotData.parent_folder.value = interface.preprocessing_folder
            interface.TabPlotData.plot_folder_handler(
                change=interface.preprocessing_folder
            )

    # elif init_postprocess_parameters == "run_prtf":
    #     compute_prtf(
    #         iobs=interface.Dataset.iobs,
    #         mask=interface.Dataset.mask,
    #         obj=interface.reconstruction_file,
    #     )

    elif not init_postprocess_parameters:
        # Disable all widgets until the end of the program
        for w in interface.TabPostprocess.children[:-1]:
            if isinstance(w, widgets.VBox) or isinstance(w, widgets.HBox):
                for wc in w.children:
                    wc.disabled = False
            elif isinstance(w, widgets.HTML):
                pass
            else:
                w.disabled = False

        if interface.TabPreprocess.run_preprocess.value == False:
            for w in interface.TabPreprocess.children[:-1]:
                if isinstance(w, widgets.VBox) or isinstance(w, widgets.HBox):
                    for wc in w.children:
                        wc.disabled = False
                elif isinstance(w, widgets.HTML):
                    pass
                else:
                    w.disabled = False

        # Refresh folders
        interface.root_folder_handler(
            change=interface.Dataset.scan_folder
        )

        # Plot folder
        interface.TabPlotData.parent_folder.value = interface.preprocessing_folder
        interface.TabPlotData.plot_folder_handler(
            change=interface.preprocessing_folder
        )

        # Find latest .h5 file, output from postprocessing
        h5_files = sorted(
            glob.glob(
                f"{interface.postprocessing_folder}/**/"
                f"{interface.Dataset.scan_name}_amp*"
                f"strain*{interface.Dataset.comment}.h5",
                recursive=True),
            key=os.path.getmtime)
        try:
            interface.Dataset.postprocessing_output_file = h5_files[0]

            creation_time = datetime.fromtimestamp(
                os.path.getmtime(interface.Dataset.postprocessing_output_file)
            ).strftime('%Y-%m-%d %H:%M:%S')

            print(
                "\n###########################################"
                "#############################################"
                "\nResult file used to save postprocessing "
                "results in the final .cxi file:"
                f"\n\t{os.path.split(interface.Dataset.postprocessing_output_file)[0]}"
                f"\n\t{os.path.split(interface.Dataset.postprocessing_output_file)[1]}"
                f"\n\tCreated: {creation_time}"
                "\n###########################################"
                "#############################################"
            )
        except KeyError:
            pass
        clear_output(True)
    else:
        print("Not yet supported.")
        clear_output(True)


def center_array(data, mask=None, center=None, method="com"):
    """
    Center 3D volume data such that the center of mass of data is at
    the very center of the 3D matrix.

    :param data: volume data (np.array). 3D numpy array which will be
        centered.
    :param mask: volume mask (np.array). 3D numpy array of same size
        as data which will be centered based on data
    :param center: center of mass coordinates(list, np.array). If no center
        is provided, center of the given data is computed (default: None).
    :param method: what region to place at the center (str), either
        com or max.

    Adapted from @Clatlan

    :returns: centered data, centered mask
    """
    shape = data.shape

    if center is None:
        if method == "com":
            xcenter, ycenter, zcenter = (
                int(round(c)) for c in center_of_mass(data)
            )
        elif method == "max":
            xcenter, ycenter, zcenter = np.where(data == np.max(data))
        else:
            print("method unknown, please choose between ['com', 'max']")
            return data, None
    else:
        xcenter, ycenter, zcenter = center

    centered_data = np.roll(data, shape[0] // 2 - xcenter, axis=0)
    centered_data = np.roll(centered_data, shape[1] // 2 - ycenter, axis=1)
    centered_data = np.roll(centered_data, shape[2] // 2 - zcenter, axis=2)

    if isinstance(mask, np.ndarray):
        centered_mask = np.roll(mask, shape[0] // 2 - xcenter, axis=0)
        centered_mask = np.roll(centered_mask, shape[1] // 2 - ycenter, axis=1)
        centered_mask = np.roll(centered_mask, shape[2] // 2 - zcenter, axis=2)

        return centered_data, centered_mask

    else:
        return centered_data, None


def crop_at_center(data, mask=None, final_shape=None):
    """
    Crop 3D array data to match the final_shape. Center of the input
    data remains the center of cropped data.

    :param data: volume data (np.array). 3D numpy array which will be
        centered.
    :param mask: volume mask (np.array). 3D numpy array of same size
        as data which will be centered based on data
    :param final_shape: the targetted shape (list). If None, nothing
    happens.

    Adapted from @Clatlan

    :returns: cropped 3D array (np.array).
    """
    if final_shape is None:
        print("No final shape specified, did not proceed to cropping")
        return data

    shape = data.shape
    final_shape = np.array(final_shape)

    if not (final_shape <= data.shape).all():
        print(
            "One of the axis of the final shape is larger than "
            "the initial axis (initial shape: {}, final shape: {}).\n"
            "Did not proceed to cropping.".format(shape, tuple(final_shape))
        )
        return data, mask

    # Crop data
    c = np.array(shape) // 2  # coordinates of the center
    to_crop = final_shape // 2  # indices to crop at both sides
    plus_one = np.where((final_shape % 2 == 0), 0, 1)

    cropped_data = data[c[0] - to_crop[0]: c[0] + to_crop[0] + plus_one[0],
                        c[1] - to_crop[1]: c[1] + to_crop[1] + plus_one[1],
                        c[2] - to_crop[2]: c[2] + to_crop[2] + plus_one[2]]

    # Crop mask
    if isinstance(mask, np.ndarray):
        cropped_mask = mask[c[0] - to_crop[0]: c[0] + to_crop[0] + plus_one[0],
                            c[1] - to_crop[1]: c[1] + to_crop[1] + plus_one[1],
                            c[2] - to_crop[2]: c[2] + to_crop[2] + plus_one[2]]

        return cropped_data, cropped_mask

    else:
        return cropped_data, mask


def center_and_crop(
    data,
    mask=None,
    center=None,
    method="com",
    final_shape=None,
):
    print("Original shape:", data.shape)
    # Determine center if not given with `method`
    if center is None:
        if method == "com":
            center = [
                int(round(c)) for c in center_of_mass(data)
            ]
        elif method == "max":
            center = np.where(data == np.max(data))
        else:
            print("method unknown, please choose between ['com', 'max']")
            return data, None
    print("Center of array:", center)

    # Determine the final shape if not given
    if final_shape is None:
        final_shape = []
        for s, c in zip(data.shape, center):
            if c > s/2:
                final_shape.append(int(np.rint(s-c)*2))
            else:
                final_shape.append(int(np.rint(c)*2))
    print("Final shape after centering and cropping:", final_shape)

    if isinstance(mask, np.ndarray):
        # Plot before
        plot.Plotter(data, log=True)
        plot.Plotter(mask, log=True)

        # Crop and center
        centered_data, centered_mask = center_array(
            data=data, mask=mask, center=center, method=method)
        cropped_data, cropped_mask = crop_at_center(
            data=centered_data, mask=centered_mask, final_shape=final_shape)

        # Plot after
        plot.Plotter(cropped_data, log=True)
        plot.Plotter(cropped_mask, log=True)

        return cropped_data, cropped_mask

    else:
        # Plot before
        plot.Plotter(data, log=True)

        # Crop and center
        centered_data, __ = center_array(
            data=data, center=center, method=method)
        cropped_data, __ = crop_at_center(
            data=centered_data, final_shape=final_shape)

        # Plot after
        plot.Plotter(cropped_data, log=True)
        return cropped_data, None

# Resolution


def compute_prtf(
    iobs,
    obj,
    mask=None,
    log_in_plots=True,
):
    """
    """
    # Get arrays
    iobs = plot.Plotter(iobs, plot=False).data_array
    mask = plot.Plotter(mask, plot=False).data_array

    # Center and plot the observed data and mask
    iobs, mask = center_array(data=iobs, mask=mask)

    plot.plot_3d_slices(iobs, log=log_in_plots)
    plt.show()
    if isinstance(mask, np.ndarray):
        plot.plot_3d_slices(mask, log=log_in_plots)
        plt.show()

    # Get data array from cxi or h5 file:
    obj = plot.Plotter(obj, plot=False).data_array

    # IFFT and FFT shift
    fft_obj = fftshift(ifftn(obj))
    plt.show()

    # square of the modulus, center
    icalc = np.abs(fft_obj)**2
    icalc, _ = center(icalc)

    # flip data (not all the time ?)
    icalc = np.flip(icalc)

    plot.plot_3d_slices(icalc, log=True)
    plt.show()

    frequency, frequency_nyquist, prtf, iobs = phase_retrieval_transfer_function.prtf(
        icalc=icalc,
        iobs=iobs,
        mask=mask,
    )

    phase_retrieval_transfer_function.plot_prtf(
        frequency, frequency_nyquist, prtf, iobs)
    plt.show()

    return frequency, frequency_nyquist, prtf, iobs
