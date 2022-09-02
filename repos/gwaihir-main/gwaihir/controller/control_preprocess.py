import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
from datetime import datetime
import tables as tb
from IPython.display import display, clear_output
import ipywidgets as widgets
from ipywidgets import interact
from ast import literal_eval
import gwaihir

from bcdi.preprocessing import ReadNxs3 as rd
from bcdi.preprocessing.preprocessing_runner import run as run_preprocessing
from bcdi.utils.parser import ConfigParser


def init_preprocess_tab(
    interface,
    unused_label_beamline,
    beamline,
    actuators,
    is_series,
    custom_scan,
    custom_images,
    custom_monitor,
    specfile_name,
    rocking_angle,
    unused_label_masking,
    flag_interact,
    background_plot,
    unused_label_centering,
    centering_method_reciprocal_space,
    bragg_peak,
    fix_size,
    center_fft,
    pad_size,
    normalize_flux,
    unused_label_filtering,
    mask_zero_event,
    median_filter,
    median_filter_order,
    phasing_binning,
    unused_label_reload,
    reload_previous,
    reload_orthogonal,
    preprocessing_binning,
    unused_label_saving,
    save_rawdata,
    save_to_npz,
    save_to_mat,
    save_to_vti,
    save_as_int,
    unused_label_detector,
    detector,
    # phasing_binning,
    # linearity_func
    # center_roi_x
    # center_roi_y
    roi_detector,
    # normalize_flux
    photon_threshold,
    photon_filter,
    # bin_during_loading TODO
    # frames_pattern TODO
    background_file,
    hotpixels_file,
    flatfield_file,
    template_imagefile,
    unused_label_ortho,
    use_rawdata,
    interpolation_method,
    fill_value_mask,
    beam_direction,
    sample_offsets,
    detector_distance,
    energy,
    custom_motors,
    unused_label_xru,
    align_q,
    ref_axis_q,
    direct_beam,
    dirbeam_detector_angles,
    # bragg_peak
    outofplane_angle,
    inplane_angle,
    tilt_angle,
    sample_inplane,
    sample_outofplane,
    offset_inplane,
    cch1,
    cch2,
    detrot,
    tiltazimuth,
    tilt_detector,
    unused_label_preprocess,
    run_preprocess,
):
    """
    Initialize the parameters used in bcdi_preprocess.py.
    Necessary for preprocessing and postprocessing.

    All the parameters values are then saved in a yaml configuration file.

    Parameters used in the interactive masking GUI:

    :param flag_interact: e.g. True
     True to interact with plots, False to close it automatically
    :param background_plot: e.g. "0.5"
     background color for the GUI in level of grey in [0,1], 0 being dark.
     For visual comfort during interactive masking.
    :param backend: e.g. "Qt5Agg"
     Backend used in script, change to "Agg" to make sure the figures are
     saved, not compaticle with interactive masking. Other possibilities
     are 'module://matplotlib_inline.backend_inline'
     default value is "Qt5Agg"

    Parameters related to data cropping/padding/centering #

    :param centering_method_reciprocal_space: e.g. "max"
     Bragg peak determination: 'max' or 'com', 'max' is better usually.
     It will be overridden by 'fix_bragg' if not empty
    :param fix_size: e.g. [0, 256, 10, 240, 50, 350]
     crop the array to that predefined size considering the full detector.
     [zstart, zstop, ystart, ystop, xstart, xstop], ROI will be defaulted
     to [] if fix_size is provided. Leave None otherwise
    :param center_fft: e.g. "skip"
     how to crop/pad/center the data, available options: 'crop_sym_ZYX',
     'crop_asym_ZYX', 'pad_asym_Z_crop_sym_YX', 'pad_sym_Z_crop_asym_YX',
     'pad_sym_Z', 'pad_asym_Z', 'pad_sym_ZYX','pad_asym_ZYX' or 'skip'
    :param pad_size: e.g. [256, 512, 512]
     Use this to pad the array. Used in 'pad_sym_Z_crop_sym_YX',
     'pad_sym_Z' and 'pad_sym_ZYX'. Leave None otherwise.

    Parameters for data filtering

    :param mask_zero_event: e.g. False
     mask pixels where the sum along the rocking curve is zero may be dead
     pixels
    :param median_filter: e.g. "skip"
     which filter to apply, available filters:

     - 'median': to apply a med2filter [3,3]
     - 'interp_isolated': to interpolate isolated empty pixels based
        on 'medfilt_order' parameter
     - 'mask_isolated': mask isolated empty pixels
     - 'skip': skip filtering

    :param median_filter_order: e.g. 7
     minimum number of non-zero neighboring pixels to apply filtering

    Parameters used when reloading processed data

    :param reload_previous: e.g. False
     True to resume a previous masking (load data and mask)
    :param reload_orthogonal: e.g. False
     True if the reloaded data is already intepolated in an orthonormal
     frame
    :param preprocessing_binning: e.g. [1, 1, 1]
     binning factors in each dimension of the binned data to be reloaded

    Options for saving:

    :param save_rawdata: e.g. False
     True to save also the raw data when use_rawdata is False
    :param save_to_npz: e.g. True
     True to save the processed data in npz format
    :param save_to_mat: e.g. False
     True to save also in .mat format
    :param save_to_vti: e.g. False
     True to save the orthogonalized diffraction pattern to VTK file
    :param save_as_int: e.g. False
     True to save the result as an array of integers (save space)

    Parameters for the beamline:

    :param beamline: e.g. "ID01"
     name of the beamline, used for data loading and normalization by
     monitor
    :param actuators: e.g. {'rocking_angle': 'actuator_1_1'}
     optional dictionary that can be used to define the entries
     corresponding to actuators in data files (useful at CRISTAL where the
     location of data keeps changing, or to declare a non-standard monitor)
    :param is_series: e.g. True
     specific to series measurement at P10
    :param rocking_angle: e.g. "outofplane"
     "outofplane" for a sample rotation around x outboard, "inplane" for a
     sample rotation around y vertical up, "energy"
    :param specfile_name: e.g. "l5.spec"
     beamline-dependent parameter, use the following template:

     - template for ID01 and 34ID: name of the spec file if it is at the
     default location (in root_folder) or full path to the spec file
     - template for SIXS: full path of the alias dictionnary or None to use
      the one in the package folder
     - for P10, either None (if you are using the same directory structure
     as the beamline) or the full path to the .fio file
     - template for all other beamlines: None

    Parameters for custom scans:

    :param custom_scan: e.g. False
     True for a stack of images acquired without scan, e.g. with ct in a
     macro, or when there is no spec/log file available
    :param custom_images: list of image numbers for the custom_scan, None
     otherwise
    :param custom_monitor: list of monitor values for normalization for the
     custom_scan, None otherwise

    Parameters for the detector:

    :param detector: e.g. "Maxipix"
     name of the detector
    :param phasing_binning: e.g. [1, 2, 2]
     binning to apply to the data (stacking dimension, detector vertical
     axis, detector horizontal axis)
    :param linearity_func: name of the linearity correction for the
     detector, leave None otherwise.
    :param center_roi_x: e.g. 1577
     horizontal pixel number of the center of the ROI for data loading.
     Leave None to use the full detector.
    :param center_roi_y: e.g. 833
     vertical pixel number of the center of the ROI for data loading.
     Leave None to use the full detector.
    :param roi_detector: e.g.[0, 250, 10, 210]
     region of interest of the detector to load. If "x_bragg" or "y_bragg"
     are not None, it will consider that the current values in roi_detector
     define a window around the Bragg peak position and the final output
     will be: [y_bragg - roi_detector[0], y_bragg + roi_detector[1],
     x_bragg - roi_detector[2], x_bragg + roi_detector[3]]. Leave None to
     use the full detector. Use with center_fft='skip' if you want this
     exact size for the output.
    :param normalize_flux: e.g. "monitor"
     'monitor' to normalize the intensity by the default monitor values,
     'skip' to do nothing
    :param photon_threshold: e.g. 0
     voxels with a smaller intensity will be set to 0.
    :param photon_filter: e.g. "loading"
     'loading' or 'postprocessing', when the photon threshold should be
     applied. If 'loading', it is applied before binning;
     if 'postprocessing', it is applied at the end of the script before
     saving
    :param bin_during_loading: e.g. False
     True to bin during loading, faster
    :param frames_pattern:  list of int, of length data.shape[0].
     If frames_pattern is 0 at index, the frame at data[index] will be
     skipped, if 1 the frame will be added to the stack. Use this if you
     need to remove some frames and you know it in advance.
    :param background_file: non-empty file path or None
    :param hotpixels_file: non-empty file path or None
    :param flatfield_file: non-empty file path or None
    :param template_imagefile: e.g. "data_mpx4_%05d.edf.gz"
     use one of the following template:

     - template for ID01: 'data_mpx4_%05d.edf.gz' or
      'align_eiger2M_%05d.edf.gz'
     - template for SIXS_2018: 'align.spec_ascan_mu_%05d.nxs'
     - template for SIXS_2019: 'spare_ascan_mu_%05d.nxs'
     - template for Cristal: 'S%d.nxs'
     - template for P10: '_master.h5'
     - template for NANOMAX: '%06d.h5'
     - template for 34ID: 'Sample%dC_ES_data_51_256_256.npz'

    Parameters below if you want to orthogonalize the data before phasing:

    :param use_rawdata: e.g. True
     False for using data gridded in laboratory frame, True for using data
     in detector frame
    :param interpolation_method: e.g. "xrayutilities"
     'xrayutilities' or 'linearization'
    :param fill_value_mask: e.g. 0
     0 (not masked) or 1 (masked). It will define how the pixels outside of
     the data range are processed during the interpolation. Because of the
     large number of masked pixels, phase retrieval converges better if the
     pixels are not masked (0 intensity imposed). The data is by default set
     to 0 outside of the defined range.
    :param beam_direction: e.g. [1, 0, 0]
     beam direction in the laboratory frame (downstream, vertical up,
     outboard)
    :param sample_offsets: e.g. None
     tuple of offsets in degrees of the sample for each sample circle
     (outer first).
     convention: the sample offsets will be subtracted to the motor values.
     Leave None if there is no offset.
    :param detector_distance: e.g. 0.50678
     in m, sample to detector distance in m
    :param energy: e.g. 9000
     X-ray energy in eV, it can be a number or a list in case of
     energy scans.
    :param custom_motors: e.g. {"mu": 0, "phi": -15.98, "chi": 90,
     "theta": 0, "delta": -0.5685, "gamma": 33.3147}
     use this to declare motor positions if there is not log file,
     None otherwise

    Parameters when orthogonalizing the data before phasing  using the
    linearized transformation matrix:

    :param align_q: e.g. True
     if True it rotates the crystal to align q, along one axis of the
     array. It is used only when interp_method is 'linearization'
    :param ref_axis_q: e.g. "y"  # q will be aligned along that axis
    :param direct_beam: e.g. [125, 362]
     [vertical, horizontal], direct beam position on the unbinned, full detector
     measured with detector angles given by `dirbeam_detector_angles`. It will be used
     to calculate the real detector angles for the measured Bragg peak. Leave None for
     no correction.
    :param dirbeam_detector_angles: e.g. [1, 25]
     [outofplane, inplane] detector angles in degrees for the direct beam measurement.
     Leave None for no correction
    :param bragg_peak: e.g. [121, 321, 256]
     Bragg peak position [z_bragg, y_bragg, x_bragg] considering the unbinned full
     detector. If 'outofplane_angle' and 'inplane_angle' are None and the direct beam
     position is provided, it will be used to calculate the correct detector angles.
     It is useful if there are hotpixels or intense aliens. Leave None otherwise.
    :param outofplane_angle: e.g. 42.6093
     detector angle in deg (rotation around x outboard, typically delta),
     corrected for the direct beam position. Leave None to use the
     uncorrected position.
    :param inplane_angle: e.g. -0.5783
     detector angle in deg(rotation around y vertical up, typically gamma),
     corrected for the direct beam position. Leave None to use the
     uncorrected position.

    Parameters when orthogonalizing the data before phasing using
    xrayutilities. xrayutilities uses the xyz crystal frame (for zero
    incident angle x is downstream, y outboard, and z vertical up):

    :param sample_inplane: e.g. [1, 0, 0]
     sample inplane reference direction along the beam at 0 angles in
     xrayutilities frame
    :param sample_outofplane: e.g. [0, 0, 1]
     surface normal of the sample at 0 angles in xrayutilities frame
    :param offset_inplane: e.g. 0
     outer detector angle offset as determined by xrayutilities area
     detector initialization
    :param cch1: e.g. 208
     direct beam vertical position in the full unbinned detector for
     xrayutilities 2D detector calibration
    :param cch2: e.g. 154
     direct beam horizontal position in the full unbinned detector for
     xrayutilities 2D detector calibration
    :param detrot: e.g. 0
     detrot parameter from xrayutilities 2D detector calibration
    :param tiltazimuth: e.g. 360
     tiltazimuth parameter from xrayutilities 2D detector calibration
    :param tilt_detector: e.g. 0
     tilt parameter from xrayutilities 2D detector calibration
    """
    # Save parameter values as attributes
    interface.Dataset.beamline = beamline
    interface.Dataset.actuators = actuators
    interface.Dataset.is_series = is_series
    interface.Dataset.custom_scan = custom_scan
    interface.Dataset.custom_images = custom_images
    interface.Dataset.custom_monitor = custom_monitor
    interface.Dataset.specfile_name = specfile_name
    interface.Dataset.rocking_angle = rocking_angle
    interface.Dataset.flag_interact = flag_interact
    interface.Dataset.background_plot = str(background_plot)
    interface.Dataset.centering_method_reciprocal_space = centering_method_reciprocal_space
    interface.Dataset.bragg_peak = bragg_peak
    interface.Dataset.fix_size = fix_size
    interface.Dataset.center_fft = center_fft
    interface.Dataset.pad_size = pad_size
    interface.Dataset.mask_zero_event = mask_zero_event
    interface.Dataset.median_filter = median_filter
    interface.Dataset.median_filter_order = median_filter_order
    interface.Dataset.reload_previous = reload_previous
    interface.Dataset.reload_orthogonal = reload_orthogonal
    interface.Dataset.preprocessing_binning = preprocessing_binning
    interface.Dataset.save_rawdata = save_rawdata
    interface.Dataset.save_to_npz = save_to_npz
    interface.Dataset.save_to_mat = save_to_mat
    interface.Dataset.save_to_vti = save_to_vti
    interface.Dataset.save_as_int = save_as_int
    interface.Dataset.detector = detector
    interface.Dataset.phasing_binning = phasing_binning
    interface.Dataset.linearity_func = None  # TODO
    interface.Dataset.roi_detector = roi_detector
    interface.Dataset.normalize_flux = normalize_flux
    interface.Dataset.photon_threshold = photon_threshold
    interface.Dataset.photon_filter = photon_filter
    interface.Dataset.bin_during_loading = True  # TODO
    interface.Dataset.frames_pattern = None  # TODO
    interface.Dataset.background_file = background_file
    interface.Dataset.hotpixels_file = hotpixels_file
    interface.Dataset.flatfield_file = flatfield_file
    interface.Dataset.template_imagefile = template_imagefile
    interface.Dataset.use_rawdata = not use_rawdata
    interface.Dataset.interpolation_method = interpolation_method
    interface.Dataset.fill_value_mask = fill_value_mask
    interface.Dataset.beam_direction = beam_direction
    interface.Dataset.sample_offsets = sample_offsets
    interface.Dataset.detector_distance = detector_distance
    interface.Dataset.energy = energy
    interface.Dataset.custom_motors = custom_motors
    interface.Dataset.align_q = align_q
    interface.Dataset.ref_axis_q = ref_axis_q
    interface.Dataset.direct_beam = direct_beam
    interface.Dataset.dirbeam_detector_angles = dirbeam_detector_angles
    interface.Dataset.outofplane_angle = outofplane_angle
    interface.Dataset.inplane_angle = inplane_angle
    interface.Dataset.tilt_angle = tilt_angle
    interface.Dataset.sample_inplane = sample_inplane
    interface.Dataset.sample_outofplane = sample_outofplane
    interface.Dataset.offset_inplane = offset_inplane
    interface.Dataset.cch1 = cch1
    interface.Dataset.cch2 = cch2
    interface.Dataset.detrot = detrot
    interface.Dataset.tiltazimuth = tiltazimuth
    interface.Dataset.tilt_detector = tilt_detector

    # Extract dict, list and tuple from strings
    list_parameters = ["bragg_peak", "custom_images",
                       "fix_size", "pad_size", "roi_detector",
                       "direct_beam", "dirbeam_detector_angles"]

    tuple_parameters = [
        "phasing_binning", "preprocessing_binning",  "beam_direction",
        "sample_offsets", "sample_inplane", "sample_outofplane"]

    dict_parameters = ["actuators", "custom_motors"]

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

    try:
        for p in dict_parameters:
            if getattr(interface.Dataset, p) == "":
                setattr(interface.Dataset, p, None)  # or {}
            else:
                if literal_eval(getattr(interface.Dataset, p)) == {}:
                    setattr(interface.Dataset, p, None)
                else:
                    setattr(interface.Dataset, p, literal_eval(
                        getattr(interface.Dataset, p)))
    except ValueError:
        print(f"Wrong dict syntax for {p}")

    # Set None if we are not using custom scans
    if not interface.Dataset.custom_scan:
        interface.Dataset.custom_images = None
        interface.Dataset.custom_monitor = None

    # Empty parameters are set to None (bcdi syntax)
    if interface.Dataset.background_file == "":
        interface.Dataset.background_file = None

    if interface.Dataset.hotpixels_file == "":
        interface.Dataset.hotpixels_file = None

    if interface.Dataset.flatfield_file == "":
        interface.Dataset.flatfield_file = None

    if interface.Dataset.specfile_name == "":
        interface.Dataset.specfile_name = None

    if run_preprocess in ("GUI", "terminal"):
        # Disable all widgets until the end of the program
        for w in interface.TabPreprocess.children[:-2]:
            if isinstance(w, widgets.VBox) or isinstance(w, widgets.HBox):
                for wc in w.children:
                    wc.disabled = True
            elif isinstance(w, widgets.HTML):
                pass
            else:
                w.disabled = True

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

        backend = interface.matplotlib_backend if run_preprocess == "GUI" else "Qt5Agg"

        # Create centering_method dict
        centering_method = {
            "direct_space": interface.Dataset.centering_method_direct_space,
            "reciprocal_space": interface.Dataset.centering_method_reciprocal_space,
        }

        # Create config file
        create_yaml_file(
            fname=f"{interface.preprocessing_folder}config_preprocessing.yml",
            scans=interface.Dataset.scan,
            root_folder=root_folder,
            save_dir=interface.preprocessing_folder,
            data_dir=data_dir,
            sample_name=interface.Dataset.sample_name,
            comment=interface.Dataset.comment,
            debug=interface.Dataset.debug,
            # parameters used in masking
            flag_interact=interface.Dataset.flag_interact,
            background_plot=interface.Dataset.background_plot,
            backend=backend,
            # parameters related to data cropping/padding/centering
            centering_method=centering_method,
            fix_size=interface.Dataset.fix_size,
            center_fft=interface.Dataset.center_fft,
            pad_size=interface.Dataset.pad_size,
            # parameters for data filtering
            mask_zero_event=interface.Dataset.mask_zero_event,
            median_filter=interface.Dataset.median_filter,
            median_filter_order=interface.Dataset.median_filter_order,
            # parameters used when reloading processed data
            reload_previous=interface.Dataset.reload_previous,
            reload_orthogonal=interface.Dataset.reload_orthogonal,
            preprocessing_binning=interface.Dataset.preprocessing_binning,
            # saving options
            save_rawdata=interface.Dataset.save_rawdata,
            save_to_npz=interface.Dataset.save_to_npz,
            save_to_mat=interface.Dataset.save_to_mat,
            save_to_vti=interface.Dataset.save_to_vti,
            save_as_int=interface.Dataset.save_as_int,
            # define beamline related parameters
            beamline=interface.Dataset.beamline,
            actuators=interface.Dataset.actuators,
            is_series=interface.Dataset.is_series,
            rocking_angle=interface.Dataset.rocking_angle,
            specfile_name=interface.Dataset.specfile_name,
            # parameters for custom scans
            custom_scan=interface.Dataset.custom_scan,
            custom_images=interface.Dataset.custom_images,
            custom_monitor=interface.Dataset.custom_monitor,
            # detector related parameters
            detector=interface.Dataset.detector,
            phasing_binning=interface.Dataset.phasing_binning,
            linearity_func=interface.Dataset.linearity_func,
            # center_roi_x
            # center_roi_y
            roi_detector=interface.Dataset.roi_detector,
            normalize_flux=interface.Dataset.normalize_flux,
            photon_threshold=interface.Dataset.photon_threshold,
            photon_filter=interface.Dataset.photon_filter,
            bin_during_loading=interface.Dataset.bin_during_loading,
            frames_pattern=interface.Dataset.frames_pattern,
            background_file=interface.Dataset.background_file,
            hotpixels_file=interface.Dataset.hotpixels_file,
            flatfield_file=interface.Dataset.flatfield_file,
            template_imagefile=interface.Dataset.template_imagefile,
            # define parameters below if you want to orthogonalize the
            # data before phasing
            use_rawdata=interface.Dataset.use_rawdata,
            interpolation_method=interface.Dataset.interpolation_method,
            fill_value_mask=interface.Dataset.fill_value_mask,
            beam_direction=interface.Dataset.beam_direction,
            sample_offsets=interface.Dataset.sample_offsets,
            detector_distance=interface.Dataset.detector_distance,
            energy=interface.Dataset.energy,
            custom_motors=interface.Dataset.custom_motors,
            # parameters when orthogonalizing the data before
            # phasing  using the linearized transformation matrix
            align_q=interface.Dataset.align_q,
            ref_axis_q=interface.Dataset.ref_axis_q,
            direct_beam=interface.Dataset.direct_beam,
            dirbeam_detector_angles=interface.Dataset.dirbeam_detector_angles,
            bragg_peak=interface.Dataset.bragg_peak,
            outofplane_angle=interface.Dataset.outofplane_angle,
            inplane_angle=interface.Dataset.inplane_angle,
            tilt_angle=interface.Dataset.tilt_angle,
            # parameters when orthogonalizing the data before phasing
            # using xrayutilities
            sample_inplane=interface.Dataset.sample_inplane,
            sample_outofplane=interface.Dataset.sample_outofplane,
            offset_inplane=interface.Dataset.offset_inplane,
            cch1=interface.Dataset.cch1,
            cch2=interface.Dataset.cch2,
            detrot=interface.Dataset.detrot,
            tiltazimuth=interface.Dataset.tiltazimuth,
            tilt_detector=interface.Dataset.tilt_detector,
        )

        if run_preprocess == "GUI":
            # Run bcdi_preprocess in GUI
            print(
                "\n###########################################"
                "#############################################"
                f"\nRunning: $ {interface.path_scripts}/bcdi_preprocess.py"
                f"\nConfig file: {interface.preprocessing_folder}config_preprocessing.yml"
                "\n###########################################"
                "#############################################"
            )

            # Load the config file
            config_file = interface.preprocessing_folder + "/config_preprocessing.yml"
            parser = ConfigParser(config_file)
            args = parser.load_arguments()
            args["time"] = f"{datetime.now()}"

            # Run function
            run_preprocessing(prm=args)
            print("End of script")

        elif run_preprocess == "terminal":
            # Run bcdi_preprocess in the terminal
            print(
                "\n###########################################"
                "#############################################"
                f"\nRunning: $ {interface.path_scripts}/bcdi_preprocess.py"
                f"\nConfig file: {interface.preprocessing_folder}config_preprocessing.yml"
                "\n###########################################"
                "#############################################"
            )

            # Run function
            print(
                f"cd {interface.preprocessing_folder}; "
                f"{interface.path_scripts}/bcdi_preprocess.py "
                "-c config_preprocessing.yml"
            )
            os.system(
                f"cd {interface.preprocessing_folder}; "
                f"{interface.path_scripts}/bcdi_preprocess.py "
                "-c config_preprocessing.yml"
            )

        # Button to save metadata
        button_save_metadata = widgets.Button(
            description="Save metadata",
            continuous_update=False,
            button_style='',
            layout=widgets.Layout(width='40%'),
            style={'description_width': 'initial'},
            icon='fast-forward')

        @ button_save_metadata.on_click
        def action_button_save_metadata(selfbutton):
            try:
                # Get latest file
                metadata_file = sorted(
                    glob.glob(
                        f"{interface.preprocessing_folder}*preprocessing*.h5"),
                    key=os.path.getmtime)[-1]

                extract_metadata(
                    scan_nb=interface.Dataset.scan,
                    metadata_file=metadata_file,
                    gwaihir_dataset=interface.Dataset,
                    metadata_csv_file=os.getcwd() + "/metadata.csv"
                )
            except (IndexError, TypeError):
                print(
                    f"Could not find any .h5 file in {interface.preprocessing_folder}")

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

        display(button_save_metadata)

    else:
        # Disable all widgets until the end of the program
        for w in interface.TabPreprocess.children[:-2]:
            if isinstance(w, widgets.VBox) or isinstance(w, widgets.HBox):
                for wc in w.children:
                    wc.disabled = False
            elif isinstance(w, widgets.HTML):
                pass
            else:
                w.disabled = False
        plt.close()
        clear_output(True)
        print("Cleared window.")


def create_yaml_file(
    fname,
    **kwargs
):
    """
    Create yaml file storing all keywords arguments given in input.
    Used for bcdi scripts.

    :param fname: path to created yaml file
    :param kwargs: kwargs to store in file
    """
    config_file = []

    for k, v in kwargs.items():
        if isinstance(v, str):
            config_file.append(f"{k}: \"{v}\"")
        elif isinstance(v, tuple):
            if v:
                config_file.append(f"{k}: {list(v)}")
            else:
                config_file.append(f"{k}: None")
        elif isinstance(v, np.ndarray):
            config_file.append(f"{k}: {list(v)}")
        elif isinstance(v, list):
            if v:
                config_file.append(f"{k}: {v}")
            else:
                config_file.append(f"{k}: None")
        elif isinstance(v, dict):
            config_file.append(f"{k}:")
            for kc, vc in v.items():
                config_file.append(f"    {kc}: \"{vc}\"")
        else:
            config_file.append(f"{k}: {v}")

    file = os.path.basename(fname)
    directory = fname.strip(file)

    # Create directory
    if not os.path.isdir(directory):
        full_path = ""
        for d in directory.split("/"):
            full_path += d + "/"
            try:
                os.mkdir(full_path)
            except (FileExistsError, PermissionError):
                pass

    # Save in file
    if fname.endswith('.yaml') or fname.endswith('.yml'):
        with open(fname, "w") as v:
            for line in config_file:
                v.write(line + "\n")
    else:
        raise FileError("Parameter fname must end with .yaml or .yml")


def extract_metadata(
    scan_nb,
    metadata_file,
    gwaihir_dataset=None,
    metadata_csv_file=None,
):
    """
    Extract meaningful data from bcdi script output files and saves them
    in a csv file as well as in the Dataset object to allow comparison.

    :param scan_nb: int, nb of scan, used for indexing in csv file.
    :param metadata_file: absolute path to metadata file (.h5) created by
     bcdi.preprocessing.py script
    :param gwaihir_dataset: Dataset object in which the metadata is saved,
     optionnal
    :param metadata_csv_file: csv file in which the metadata is saved.
     If None, defaulted to os.getcwd() + "/metadata.csv"
    """
    # Open file
    with tb.open_file(metadata_file, "r") as f:

        # Save metadata in a pd.DataFrame
        temp_df = pd.DataFrame([[
            scan_nb,
            f.root.output.q_bragg[...][0],
            f.root.output.q_bragg[...][1],
            f.root.output.q_bragg[...][2],
            f.root.output.qnorm[...],
            f.root.output.planar_distance[...],
            f.root.output.bragg_inplane[...],
            f.root.output.bragg_outofplane[...],
            f.root.output.bragg_peak[...],
        ]],
            columns=[
                "scan",
                "qx",
                "qy",
                "qz",
                "q_norm",
                "d_hkl",
                "inplane_angle",
                "out_of_plane_angle",
                "bragg_peak",
        ])

        # Extra metadata that is not always computed
        try:
            temp_df["COM_rocking_curve"] = f.root.output.COM_rocking_curve[...]
            temp_df["interp_fwhm"] = f.root.output.interp_fwhm[...]

            tilt_angle = np.round(
                np.mean(f.root.output.tilt_values[...][1:]
                        - f.root.output.tilt_values[...][:-1]),
                4)
            temp_df["tilt_angle"] = tilt_angle

        except tb.NoSuchNodeError:
            # No angle correction during preprocess
            pass

        # Save metadata in the Dataset object
        if isinstance(gwaihir_dataset, gwaihir.dataset.Dataset):

            gwaihir_dataset.q = f.root.output.q_bragg[...]
            gwaihir_dataset.qnorm = f.root.output.qnorm[...]
            gwaihir_dataset.dist_plane = f.root.output.planar_distance[...]
            gwaihir_dataset.bragg_inplane = f.root.output.bragg_inplane[...]
            gwaihir_dataset.bragg_outofplane = f.root.output.bragg_outofplane[...]
            gwaihir_dataset.bragg_peak = f.root.output.bragg_peak[...]

            # Extra metadata that is not always computed
            try:
                gwaihir_dataset.tilt_values = f.root.output.tilt_values[...]
                gwaihir_dataset.rocking_curve = f.root.output.rocking_curve[...]
                gwaihir_dataset.interp_tilt = f.root.output.interp_tilt[...]
                gwaihir_dataset.interp_curve = f.root.output.interp_curve[...]
                gwaihir_dataset.detector_data_COM = f.root.output.detector_data_COM[...]
                gwaihir_dataset.COM_rocking_curve = f.root.output.COM_rocking_curve[...]
                gwaihir_dataset.interp_fwhm = f.root.output.interp_fwhm[...]
                gwaihir_dataset.tilt_angle = tilt_angle

            except tb.NoSuchNodeError:
                # No angle correction during preprocess
                pass

            # Extra metadata for SixS to save in df
            if gwaihir_dataset.beamline is "SIXS_2019":
                data = rd.DataSet(gwaihir_dataset.path_to_nxs_data)
                try:
                    temp_df["x"] = data.x[0]
                    temp_df["y"] = data.y[0]
                    temp_df["z"] = data.z[0]
                    temp_df["mu"] = data.mu[0]
                    temp_df["delta"] = data.delta[0]
                    temp_df["omega"] = data.omega[0]
                    temp_df["gamma"] = data.gamma[0]
                    temp_df["gamma-mu"] = data.gamma[0] - data.mu[0]
                    temp_df["step_size"] = (
                        data.mu[-1] - data.mu[-0]) / len(data.mu)
                    temp_df["integration_time"] = data.integration_time[0]
                    temp_df["steps"] = len(data.integration_time)
                except AttributeError:
                    print("Could not extract metadata from SixS file")

    # Save in a csv file
    try:
        # Load old file
        df = pd.read_csv(metadata_csv_file)

        # Replace old data linked to this scan
        indices = df[df['scan'] == scan_nb].index
        df.drop(indices, inplace=True)
        result = pd.concat([df, temp_df])

        # Save
        display(result.head())
        result.to_csv(metadata_csv_file, index=False)
        print(f"Saved logs in {metadata_csv_file}")

    except (FileNotFoundError, ValueError):
        # Create file
        metadata_csv_file = os.getcwd() + "/metadata.csv"

        # Save
        display(temp_df.head())
        temp_df.to_csv(metadata_csv_file, index=False)
        print(f"Saved logs in {metadata_csv_file}")
