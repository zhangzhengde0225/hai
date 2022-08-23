import os
import inspect
import getpass
import gwaihir

import ipywidgets as widgets
from ipywidgets import interactive, fixed, Tab
from IPython.display import display

from gwaihir.view.tab_data_frame import TabDataFrame
from gwaihir.view.tab_detector import TabDetector
from gwaihir.view.tab_facet import TabFacet
from gwaihir.view.tab_instrument import TabInstrument
from gwaihir.view.tab_plot_data import TabPlotData
from gwaihir.view.tab_postprocess import TabPostprocess
from gwaihir.view.tab_preprocess import TabPreprocess
from gwaihir.view.tab_readme import TabReadme
from gwaihir.view.tab_startup import TabStartup

from gwaihir.controller.control_data_frame import init_data_frame_tab
from gwaihir.controller.control_facet import init_facet_tab
from gwaihir.controller.control_plot_data import init_plot_data_tab
from gwaihir.controller.control_postprocess import init_postprocess_tab
from gwaihir.controller.control_preprocess import init_preprocess_tab
from gwaihir.controller.control_readme import init_readme_tab
from gwaihir.controller.control_startup import init_startup_tab

try:
    from gwaihir.view.tab_phase_retrieval import TabPhaseRetrieval
    from gwaihir.controller.control_phase_retrieval import init_phase_retrieval_tab
    pynx_import_success = True
except ModuleNotFoundError:
    pynx_import_success = False
    print(
        "Could not load PyNX."
        "\nThe phase retrieval tab will be disabled."
    )


class Interface:
    """
    This class is a Graphical User Interface (GUI).

    It makes extensive use of the ipywidgets and is thus meant to be
    used with a jupyter notebook. Additional informations are provided
    in the "README" tab of the GUI.
    """

    def __init__(self, plot_tab_only=False):
        """
        The different tabs of the GUI are loaded from the submodule view.
        They are then laid out side by side by using the ipywidgets.Tabs()
         method.
        The currently supported tabs are:
            - TabStartup
            - TabDetector
            - TabInstrument
            - TabPreprocess
            - TabDataFrame
            - TabPhaseRetrieval
            - TabPostprocess
            - TabPlotData
            - TabFacet
            - TabReadme

        Here is also defined:
            path_scripts: path to folder in which bcdi and pynx scripts are
                stored
            user_name: user_name used to login to slurm if working on the ESRF
                cluster

        :param plot_tab_only: True to only work with the plotting tab
        """
        super(Interface, self).__init__()

        # Initialize future attributes
        self.Dataset = None
        self.text_file = None
        self.params = None
        self.preprocessing_folder = None
        self.postprocessing_folder = None

        # Init tabs
        self.TabStartup = TabStartup()
        self.TabDetector = TabDetector()
        self.TabInstrument = TabInstrument()
        self.TabPreprocess = TabPreprocess()
        self.TabDataFrame = TabDataFrame()
        self.TabPhaseRetrieval = TabPhaseRetrieval()
        self.TabPostprocess = TabPostprocess()
        self.TabPlotData = TabPlotData()
        self.TabFacet = TabFacet()
        self.TabReadme = TabReadme()

        # Get path to scripts folder
        path_package = inspect.getfile(gwaihir).split("__")[0]
        self.path_scripts = path_package.split(
            "/lib/python")[0] + "/bin"
        print(
            f"Using scripts contained in '{self.path_scripts}'"
        )

        # Get user name
        try:
            self.user_name = getpass.getuser()

            print(
                f"Login used for batch jobs: {self.user_name}"
            )
        except Exception as e:
            self.user_name = None

            print(
                "Could not get user name."
                "\nPlease create self.user_name attribute for jobs"
            )
            raise e

        # Display only the plot tab
        if plot_tab_only:
            self.window = Tab(children=(
                interactive(
                    init_plot_data_tab,
                    interface=fixed(self),
                    unused_label_plot=self.TabPlotData.unused_label_plot,
                    parent_folder=self.TabPlotData.parent_folder,
                    filename=self.TabPlotData.filename,
                    cmap=self.TabPlotData.cmap,
                    data_use=self.TabPlotData.data_use,
                ),
            ))

            self.window.set_title(0, "Plot data")

        else:
            # Initialize functions
            self.init_startup_tab_gui = interactive(
                init_startup_tab,
                interface=fixed(self),
                unused_label_scan=self.TabStartup.unused_label_scan,
                sample_name=self.TabStartup.sample_name,
                scan=self.TabStartup.scan,
                data_dir=self.TabStartup.data_dir,
                root_folder=self.TabStartup.root_folder,
                comment=self.TabStartup.comment,
                debug=self.TabStartup.debug,
                matplotlib_backend=self.TabStartup.matplotlib_backend,
                run_dir_init=self.TabStartup.run_dir_init,
            )

            self.init_preprocess_tab_gui = interactive(
                init_preprocess_tab,
                interface=fixed(self),
                unused_label_detector=self.TabDetector.unused_label_detector,
                detector=self.TabDetector.detector,
                # phasing_binning = self.TabPreprocess.phasing_binning,
                # linearity_func = self.TabPreprocess.linearity_func
                roi_detector=self.TabDetector.roi_detector,
                # normalize_flux = self.TabPreprocess.normalize_flux
                photon_threshold=self.TabDetector.photon_threshold,
                photon_filter=self.TabDetector.photon_filter,
                # bin_during_loading TODO = self.TabPreprocess.TODO
                # frames_pattern TODO = self.TabPreprocess.TODO
                background_file=self.TabDetector.background_file,
                hotpixels_file=self.TabDetector.hotpixels_file,
                flatfield_file=self.TabDetector.flatfield_file,
                template_imagefile=self.TabDetector.template_imagefile,
                unused_label_ortho=self.TabInstrument.unused_label_ortho,
                use_rawdata=self.TabInstrument.use_rawdata,
                interpolation_method=self.TabInstrument.interpolation_method,
                fill_value_mask=self.TabInstrument.fill_value_mask,
                beam_direction=self.TabInstrument.beam_direction,
                sample_offsets=self.TabInstrument.sample_offsets,
                detector_distance=self.TabInstrument.detector_distance,
                energy=self.TabInstrument.energy,
                custom_motors=self.TabInstrument.custom_motors,
                unused_label_xru=self.TabInstrument.unused_label_xru,
                align_q=self.TabInstrument.align_q,
                ref_axis_q=self.TabInstrument.ref_axis_q,
                direct_beam=self.TabInstrument.direct_beam,
                dirbeam_detector_angles=self.TabInstrument.dirbeam_detector_angles,
                outofplane_angle=self.TabInstrument.outofplane_angle,
                inplane_angle=self.TabInstrument.inplane_angle,
                tilt_angle=self.TabInstrument.tilt_angle,
                sample_inplane=self.TabInstrument.sample_inplane,
                sample_outofplane=self.TabInstrument.sample_outofplane,
                offset_inplane=self.TabInstrument.offset_inplane,
                cch1=self.TabInstrument.cch1,
                cch2=self.TabInstrument.cch2,
                detrot=self.TabInstrument.detrot,
                tiltazimuth=self.TabInstrument.tiltazimuth,
                tilt_detector=self.TabInstrument.tilt_detector,
                unused_label_beamline=self.TabPreprocess.unused_label_beamline,
                beamline=self.TabPreprocess.beamline,
                actuators=self.TabPreprocess.actuators,
                is_series=self.TabPreprocess.is_series,
                custom_scan=self.TabPreprocess.custom_scan,
                custom_images=self.TabPreprocess.custom_images,
                custom_monitor=self.TabPreprocess.custom_monitor,
                specfile_name=self.TabPreprocess.specfile_name,
                rocking_angle=self.TabPreprocess.rocking_angle,
                unused_label_masking=self.TabPreprocess.unused_label_masking,
                flag_interact=self.TabPreprocess.flag_interact,
                background_plot=self.TabPreprocess.background_plot,
                unused_label_centering=self.TabPreprocess.unused_label_centering,
                centering_method_reciprocal_space=self.TabPreprocess.centering_method_reciprocal_space,
                bragg_peak=self.TabPreprocess.bragg_peak,
                fix_size=self.TabPreprocess.fix_size,
                center_fft=self.TabPreprocess.center_fft,
                pad_size=self.TabPreprocess.pad_size,
                normalize_flux=self.TabPreprocess.normalize_flux,
                unused_label_filtering=self.TabPreprocess.unused_label_filtering,
                mask_zero_event=self.TabPreprocess.mask_zero_event,
                median_filter=self.TabPreprocess.median_filter,
                median_filter_order=self.TabPreprocess.median_filter_order,
                phasing_binning=self.TabPreprocess.phasing_binning,
                unused_label_reload=self.TabPreprocess.unused_label_reload,
                reload_previous=self.TabPreprocess.reload_previous,
                reload_orthogonal=self.TabPreprocess.reload_orthogonal,
                preprocessing_binning=self.TabPreprocess.preprocessing_binning,
                unused_label_saving=self.TabPreprocess.unused_label_saving,
                save_rawdata=self.TabPreprocess.save_rawdata,
                save_to_npz=self.TabPreprocess.save_to_npz,
                save_to_mat=self.TabPreprocess.save_to_mat,
                save_to_vti=self.TabPreprocess.save_to_vti,
                save_as_int=self.TabPreprocess.save_as_int,
                unused_label_preprocess=self.TabPreprocess.unused_label_preprocess,
                run_preprocess=self.TabPreprocess.run_preprocess,
            )

            self.init_data_frame_tab_gui = interactive(
                init_data_frame_tab,
                interface=fixed(self),
                unused_label_logs=self.TabDataFrame.unused_label_logs,
                parent_folder=self.TabDataFrame.parent_folder,
                csv_file=self.TabDataFrame.csv_file,
                show_logs=self.TabDataFrame.show_logs,
            )

            if pynx_import_success:
                self.init_phase_retrieval_tab_gui = interactive(
                    init_phase_retrieval_tab,
                    interface=fixed(self),
                    unused_label_data=self.TabPhaseRetrieval.unused_label_data,
                    parent_folder=self.TabPhaseRetrieval.parent_folder,
                    iobs=self.TabPhaseRetrieval.iobs,
                    mask=self.TabPhaseRetrieval.mask,
                    support=self.TabPhaseRetrieval.support,
                    obj=self.TabPhaseRetrieval.obj,
                    auto_center_resize=self.TabPhaseRetrieval.auto_center_resize,
                    max_size=self.TabPhaseRetrieval.max_size,
                    unused_label_support=self.TabPhaseRetrieval.unused_label_support,
                    support_threshold=self.TabPhaseRetrieval.support_threshold,
                    support_only_shrink=self.TabPhaseRetrieval.support_only_shrink,
                    support_update_period=self.TabPhaseRetrieval.support_update_period,
                    support_smooth_width=self.TabPhaseRetrieval.support_smooth_width,
                    support_post_expand=self.TabPhaseRetrieval.support_post_expand,
                    support_method=self.TabPhaseRetrieval.support_method,
                    support_autocorrelation_threshold=self.TabPhaseRetrieval.support_autocorrelation_threshold,
                    unused_label_psf=self.TabPhaseRetrieval.unused_label_psf,
                    psf=self.TabPhaseRetrieval.psf,
                    psf_model=self.TabPhaseRetrieval.psf_model,
                    fwhm=self.TabPhaseRetrieval.fwhm,
                    eta=self.TabPhaseRetrieval.eta,
                    psf_filter=self.TabPhaseRetrieval.psf_filter,
                    update_psf=self.TabPhaseRetrieval.update_psf,
                    unused_label_algo=self.TabPhaseRetrieval.unused_label_algo,
                    nb_hio=self.TabPhaseRetrieval.nb_hio,
                    nb_raar=self.TabPhaseRetrieval.nb_raar,
                    nb_er=self.TabPhaseRetrieval.nb_er,
                    nb_ml=self.TabPhaseRetrieval.nb_ml,
                    nb_run=self.TabPhaseRetrieval.nb_run,
                    unused_label_filtering=self.TabPhaseRetrieval.unused_label_filtering,
                    filter_criteria=self.TabPhaseRetrieval.filter_criteria,
                    nb_run_keep=self.TabPhaseRetrieval.nb_run_keep,
                    unused_label_options=self.TabPhaseRetrieval.unused_label_options,
                    live_plot=self.TabPhaseRetrieval.live_plot,
                    plot_axis=self.TabPhaseRetrieval.plot_axis,
                    verbose=self.TabPhaseRetrieval.verbose,
                    rebin=self.TabPhaseRetrieval.rebin,
                    positivity=self.TabPhaseRetrieval.positivity,
                    beta=self.TabPhaseRetrieval.beta,
                    detwin=self.TabPhaseRetrieval.detwin,
                    calc_llk=self.TabPhaseRetrieval.calc_llk,
                    pixel_size_detector=self.TabPhaseRetrieval.pixel_size_detector,
                    unused_label_mask_options=self.TabPhaseRetrieval.unused_label_mask_options,
                    zero_mask=self.TabPhaseRetrieval.zero_mask,
                    mask_interp=self.TabPhaseRetrieval.mask_interp,
                    unused_label_phase_retrieval=self.TabPhaseRetrieval.unused_label_phase_retrieval,
                    run_phase_retrieval=self.TabPhaseRetrieval.run_phase_retrieval,
                    unused_label_run_pynx_tools=self.TabPhaseRetrieval.unused_label_run_pynx_tools,
                    run_pynx_tools=self.TabPhaseRetrieval.run_pynx_tools,
                )

            self.init_postprocess_tab_gui = interactive(
                init_postprocess_tab,
                interface=fixed(self),
                unused_label_averaging=self.TabPostprocess.unused_label_averaging,
                sort_method=self.TabPostprocess.sort_method,
                correlation_threshold=self.TabPostprocess.correlation_threshold,
                unused_label_FFT=self.TabPostprocess.unused_label_FFT,
                phasing_binning=self.TabPostprocess.phasing_binning,
                original_size=self.TabPostprocess.original_size,
                preprocessing_binning=self.TabPostprocess.preprocessing_binning,
                output_size=self.TabPostprocess.output_size,
                keep_size=self.TabPostprocess.keep_size,
                fix_voxel=self.TabPostprocess.fix_voxel,
                unused_label_disp_strain=self.TabPostprocess.unused_label_disp_strain,
                data_frame=self.TabPostprocess.data_frame,
                save_frame=self.TabPostprocess.save_frame,
                ref_axis_q=self.TabPostprocess.ref_axis_q,
                isosurface_strain=self.TabPostprocess.isosurface_strain,
                skip_unwrap=self.TabPostprocess.skip_unwrap,
                strain_method=self.TabPostprocess.strain_method,
                phase_offset=self.TabPostprocess.phase_offset,
                phase_offset_origin=self.TabPostprocess.phase_offset_origin,
                offset_method=self.TabPostprocess.offset_method,
                centering_method_direct_space=self.TabPostprocess.centering_method_direct_space,
                unused_label_refraction=self.TabPostprocess.unused_label_refraction,
                correct_refraction=self.TabPostprocess.correct_refraction,
                optical_path_method=self.TabPostprocess.optical_path_method,
                dispersion=self.TabPostprocess.dispersion,
                absorption=self.TabPostprocess.absorption,
                threshold_unwrap_refraction=self.TabPostprocess.threshold_unwrap_refraction,
                unused_label_options=self.TabPostprocess.unused_label_options,
                simulation=self.TabPostprocess.simulation,
                invert_phase=self.TabPostprocess.invert_phase,
                flip_reconstruction=self.TabPostprocess.flip_reconstruction,
                phase_ramp_removal=self.TabPostprocess.phase_ramp_removal,
                threshold_gradient=self.TabPostprocess.threshold_gradient,
                save_raw=self.TabPostprocess.save_raw,
                save_support=self.TabPostprocess.save_support,
                save=self.TabPostprocess.save,
                debug=self.TabPostprocess.debug,
                roll_modes=self.TabPostprocess.roll_modes,
                unused_label_data_vis=self.TabPostprocess.unused_label_data_vis,
                align_axis=self.TabPostprocess.align_axis,
                ref_axis=self.TabPostprocess.ref_axis,
                axis_to_align=self.TabPostprocess.axis_to_align,
                strain_range=self.TabPostprocess.strain_range,
                phase_range=self.TabPostprocess.phase_range,
                grey_background=self.TabPostprocess.grey_background,
                tick_spacing=self.TabPostprocess.tick_spacing,
                tick_direction=self.TabPostprocess.tick_direction,
                tick_length=self.TabPostprocess.tick_length,
                tick_width=self.TabPostprocess.tick_width,
                unused_label_average=self.TabPostprocess.unused_label_average,
                averaging_space=self.TabPostprocess.averaging_space,
                threshold_avg=self.TabPostprocess.threshold_avg,
                unused_label_apodize=self.TabPostprocess.unused_label_apodize,
                apodize=self.TabPostprocess.apodize,
                apodization_window=self.TabPostprocess.apodization_window,
                half_width_avg_phase=self.TabPostprocess.half_width_avg_phase,
                apodization_mu=self.TabPostprocess.apodization_mu,
                apodization_sigma=self.TabPostprocess.apodization_sigma,
                apodization_alpha=self.TabPostprocess.apodization_alpha,
                unused_label_strain=self.TabPostprocess.unused_label_strain,
                strain_folder=self.TabPostprocess.strain_folder,
                reconstruction_file=self.TabPostprocess.reconstruction_file,
                init_postprocess_parameters=self.TabPostprocess.init_postprocess_parameters,
            )

            self.init_plot_data_tab_gui = interactive(
                init_plot_data_tab,
                interface=fixed(self),
                unused_label_plot=self.TabPlotData.unused_label_plot,
                parent_folder=self.TabPlotData.parent_folder,
                filename=self.TabPlotData.filename,
                cmap=self.TabPlotData.cmap,
                data_use=self.TabPlotData.data_use,
            )

            self.init_facet_tab_gui = interactive(
                init_facet_tab,
                interface=fixed(self),
                unused_label_facet=self.TabFacet.unused_label_facet,
                parent_folder=self.TabFacet.parent_folder,
                vtk_file=self.TabFacet.vtk_file,
                load_data=self.TabFacet.load_data,
            )

            self.init_readme_tab_gui = interactive(
                init_readme_tab,
                contents=self.TabReadme.contents,
            )

            # Create window
            if pynx_import_success:
                self.window = Tab(children=(
                    widgets.VBox([
                        self.TabStartup,
                        self.init_startup_tab_gui.children[-1]
                    ]),
                    self.TabDetector,
                    self.TabInstrument,
                    widgets.VBox([
                        self.TabPreprocess,
                        self.init_preprocess_tab_gui.children[-1]
                    ]),
                    widgets.VBox([
                        self.TabDataFrame,
                        self.init_data_frame_tab_gui.children[-1]
                    ]),
                    widgets.VBox([
                        self.TabPhaseRetrieval,
                        self.init_phase_retrieval_tab_gui.children[-1]
                    ]),
                    widgets.VBox([
                        self.TabPostprocess,
                        self.init_postprocess_tab_gui.children[-1]
                    ]),
                    widgets.VBox([
                        self.TabPlotData,
                        self.init_plot_data_tab_gui.children[-1]
                    ]),
                    widgets.VBox([
                        self.TabFacet,
                        self.init_facet_tab_gui.children[-1]
                    ]),
                    widgets.VBox([
                        self.TabReadme,
                        self.init_readme_tab_gui.children[-1]
                    ]),
                ))

                # Set tab names
                self.window.set_title(0, "Startup")
                self.window.set_title(1, "Detector")
                self.window.set_title(2, "Setup")
                self.window.set_title(3, "Preprocess")
                self.window.set_title(4, "Metadata")
                self.window.set_title(5, "Phase retrieval")
                self.window.set_title(6, "Postprocess")
                self.window.set_title(7, "Plot data")
                self.window.set_title(8, "Facet")
                self.window.set_title(9, "Readme")

            else:
                self.window = Tab(children=(
                    widgets.VBox([
                        self.TabStartup,
                        self.init_startup_tab_gui.children[-1]
                    ]),
                    self.TabDetector,
                    self.TabInstrument,
                    widgets.VBox([
                        self.TabPreprocess,
                        self.init_preprocess_tab_gui.children[-1]
                    ]),
                    widgets.VBox([
                        self.TabDataFrame,
                        self.init_data_frame_tab_gui.children[-1]
                    ]),
                    widgets.VBox([
                        self.TabPostprocess,
                        self.init_postprocess_tab_gui.children[-1]
                    ]),
                    widgets.VBox([
                        self.TabPlotData,
                        self.init_plot_data_tab_gui.children[-1]
                    ]),
                    widgets.VBox([
                        self.TabFacet,
                        self.init_facet_tab_gui.children[-1]
                    ]),
                    widgets.VBox([
                        self.TabReadme,
                        self.init_readme_tab_gui.children[-1]
                    ]),
                ))

                # Set tab names
                self.window.set_title(0, "Startup")
                self.window.set_title(1, "Detector")
                self.window.set_title(2, "Setup")
                self.window.set_title(3, "Preprocess")
                self.window.set_title(4, "Metadata")
                self.window.set_title(5, "Postprocess")
                self.window.set_title(6, "Plot data")
                self.window.set_title(7, "Facet")
                self.window.set_title(8, "Readme")

            # Handlers specific to GUI because they
            # interact with multiple tabs
            self.TabStartup.root_folder.observe(
                self.root_folder_handler, names="value")
            self.TabStartup.run_dir_init.observe(
                self.init_handler, names="value")
            self.TabPreprocess.run_preprocess.observe(
                self.preprocess_handler, names="value")

        # Display the final window
        display(self.window)

    # Define handlers
    def root_folder_handler(self, change):
        """Handles changes linked to root_folder subdirectories"""
        if hasattr(change, "new"):
            change = change.new
        sub_dirs = [x[0] + "/" for x in os.walk(change)]

        if self.TabStartup.run_dir_init.value:
            self.TabPostprocess.strain_folder.options = sub_dirs
            self.TabPlotData.parent_folder.options = sub_dirs
            self.TabFacet.parent_folder.options = sub_dirs
            self.TabPhaseRetrieval.parent_folder.options = sub_dirs

    def init_handler(self, change):
        """Handles changes on the widget used for the initialization."""
        if not change.new:
            for w in self.TabStartup.children[:-1]:
                if isinstance(w, widgets.VBox) or isinstance(w, widgets.HBox):
                    for wc in w.children:
                        wc.disabled = False
                else:
                    w.disabled = False

            for w in self.TabDetector.children + self.TabInstrument.children + self.TabPreprocess.children:
                if isinstance(w, widgets.VBox) or isinstance(w, widgets.HBox):
                    for wc in w.children:
                        wc.disabled = True
                else:
                    w.disabled = True

        if change.new:
            for w in self.TabStartup.children[:-1]:
                if isinstance(w, widgets.VBox) or isinstance(w, widgets.HBox):
                    for wc in w.children:
                        wc.disabled = True
                else:
                    w.disabled = True

            for w in self.TabDetector.children + self.TabInstrument.children + self.TabPreprocess.children:
                if isinstance(w, widgets.VBox) or isinstance(w, widgets.HBox):
                    for wc in w.children:
                        wc.disabled = False
                else:
                    w.disabled = False

            # Refresh handlers
            self.TabPreprocess.beamline_handler(
                change=self.TabPreprocess.beamline.value)
            self.TabPreprocess.bragg_peak_centering_handler(
                change=self.TabPreprocess.centering_method_reciprocal_space.value)
            self.TabPreprocess.reload_data_handler(
                change=self.TabPreprocess.reload_previous.value)

    def preprocess_handler(self, change):
        """Handles changes on the widget used for the preprocessing."""
        if hasattr(change, "new"):
            change = change.new

        if not change:
            self.TabStartup.run_dir_init.disabled = False

            for w in self.TabPreprocess.children[:-1]:
                if isinstance(w, widgets.VBox) or isinstance(w, widgets.HBox):
                    for wc in w.children:
                        wc.disabled = False
                else:
                    w.disabled = False

            # Refresh handlers
            self.TabPreprocess.beamline_handler(
                change=self.TabPreprocess.beamline.value)
            self.TabPreprocess.bragg_peak_centering_handler(
                change=self.TabPreprocess.centering_method_reciprocal_space.value)
            self.TabPreprocess.reload_data_handler(
                change=self.TabPreprocess.reload_previous.value)

        if change:
            self.TabStartup.run_dir_init.disabled = True

            for w in self.TabPreprocess.children[:-1]:
                if isinstance(w, widgets.VBox) or isinstance(w, widgets.HBox):
                    for wc in w.children:
                        wc.disabled = True
                else:
                    w.disabled = True
