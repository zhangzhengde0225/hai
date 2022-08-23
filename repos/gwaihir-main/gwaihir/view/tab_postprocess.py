import ipywidgets as widgets
import os
import glob
import numpy as np


class TabPostprocess(widgets.VBox):
    """

    """

    def __init__(self, box_style=""):
        """

        """
        super(TabPostprocess, self).__init__()

        # Brief header describing the tab
        self.header = 'Postprocess'
        self.box_style = box_style

        # Define widgets
        self.unused_label_averaging = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Parameters used when averaging several reconstruction",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.sort_method = widgets.Dropdown(
            options=['mean_amplitude', 'variance',
                     'variance/mean', 'volume'],
            value="variance/mean",
            description='Sorting method',
            style={'description_width': 'initial'}
        )

        self.correlation_threshold = widgets.FloatText(
            value=0.9,
            step=0.01,
            max=1,
            min=0,
            continuous_update=False,
            description='Correlation threshold:',
            style={
                'description_width': 'initial'},
        )

        self.unused_label_FFT = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Parameters relative to the FFT window and voxel sizes",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.original_size = widgets.Text(
            placeholder="[256, 512, 512]",
            description='FFT shape before PyNX binning in PyNX',
            layout=widgets.Layout(width='45%'),
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.phasing_binning = widgets.Text(
            value="(1, 1, 1)",
            placeholder="(1, 1, 1)",
            description='Binning factor used in phase retrieval',
            continuous_update=False,
            layout=widgets.Layout(width='30%'),
            style={
                'description_width': 'initial'},
        )

        self.preprocessing_binning = widgets.Text(
            value="(1, 1, 1)",
            placeholder="(1, 1, 1)",
            description='Binning factors used in preprocessing',
            continuous_update=False,
            layout=widgets.Layout(width='30%'),
            style={
                'description_width': 'initial'},
        )

        self.output_size = widgets.Text(
            placeholder="[256, 512, 512]",
            description='Output size',
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.keep_size = widgets.Checkbox(
            value=False,
            description='Keep the initial array size for orthogonalization\
             (slower)',
            layout=widgets.Layout(width='45%'),
            style={'description_width': 'initial'}
        )

        self.fix_voxel = widgets.BoundedIntText(
            placeholder="10",
            description='Fix voxel size, put 0 to set free:',
            min=0,
            max=9999999,
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.unused_label_disp_strain = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Parameters related to displacement and strain calculation",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.data_frame = widgets.ToggleButtons(
            options=[
                'detector', 'crystal', "laboratory"],
            value="detector",
            description='Data frame',
            tooltips=[
                "If the data is still in the detector frame",
                "If the data was interpolated into the crystal frame using\
                 (xrayutilities) or (transformation matrix + align_q=True)",
                "If the data was interpolated into the laboratory frame \
                using the transformation matrix (align_q = False)"
            ],
            style={'description_width': 'initial'}
        )

        self.ref_axis_q = widgets.Dropdown(
            options=["x", "y", "z"],
            value="y",
            description='Ref axis q',
            continuous_update=False,
            layout=widgets.Layout(width='15%'),
            tooltip="q will be aligned along that axis",
            style={'description_width': 'initial'}
        )

        self.save_frame = widgets.ToggleButtons(
            options=[
                'crystal', 'laboratory', "lab_flat_sample"],
            value="lab_flat_sample",
            description='Final frame',
            tooltips=[
                "Save the data with q aligned along ref_axis_q",
                "Save the data in the laboratory frame (experimental \
                geometry)",
                "Save the data in the laboratory frame, with all sample\
                 angles rotated back to 0"
            ],
            style={'description_width': 'initial'}
        )

        self.isosurface_strain = widgets.FloatText(
            value=0.1,
            step=0.01,
            max=1,
            min=0,
            continuous_update=False,
            description='Isosurface strain:',
            tooltip="Threshold use for removing the outer layer (strain is\
             undefined at the exact surface voxel)",
            readout=True,
            layout=widgets.Layout(width='15%'),
            style={
                'description_width': 'initial'},
        )

        self.skip_unwrap = widgets.Checkbox(
            value=False,
            description='Skip phase unwrap',
            layout=widgets.Layout(width='15%'),
            style={
                'description_width': 'initial'}
        )

        self.strain_method = widgets.ToggleButtons(
            options=[
                'default', 'defect'],
            value="default",
            description='Strain method',
            tooltips=[
                "",
                "Will offset the phase in a loop and keep the smallest \
                magnitude value for the strain. See: F. Hofmann et al. \
                PhysRevMaterials 4, 013801 (2020)"
            ],
            style={'description_width': 'initial'}
        )

        self.phase_offset = widgets.FloatText(
            value=0,
            step=0.01,
            min=0,
            max=360,
            continuous_update=False,
            description='Phase offset:',
            layout=widgets.Layout(width='15%'),
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.phase_offset_origin = widgets.Text(
            placeholder="(x, y, z), leave None for automatic.",
            description='Phase offset origin',
            continuous_update=False,
            layout=widgets.Layout(width='30%'),
            style={
                'description_width': 'initial'},
        )

        self.offset_method = widgets.Dropdown(
            options=["com", "mean"],
            value="com",
            description='Offset method:',
            continuous_update=False,
            layout=widgets.Layout(width='15%'),
            style={'description_width': 'initial'}
        )

        self.centering_method_direct_space = widgets.Dropdown(
            options=[
                "com", "max", "max_com"],
            value="com",
            description='Centering method in direct space:',
            continuous_update=False,
            layout=widgets.Layout(width='25%'),
            style={'description_width': 'initial'}
        )

        self.unused_label_refraction = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Parameters related to the refraction correction",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.correct_refraction = widgets.Checkbox(
            value=False,
            description='Correct refraction',
            style={
                'description_width': 'initial'}
        )

        self.optical_path_method = widgets.ToggleButtons(
            options=[
                'threshold', 'defect'],
            value="threshold",
            description='Optical path method',
            tooltips=[
                "Uses isosurface_strain to define the support for the \
                optical path calculation",
                "Tries to remove only outer layers even if the amplitude \
                is lower than isosurface_strain inside the crystal"
            ],
            disabled=True,
            style={'description_width': 'initial'}
        )

        self.dispersion = widgets.FloatText(
            value=0.000050328,
            continuous_update=False,
            description='Dispersion (delta):',
            readout=True,
            style={
                'description_width': 'initial'},
            disabled=True
        )

        self.absorption = widgets.FloatText(
            value=0.000050328,
            continuous_update=False,
            description='Absorption (beta):',
            readout=True,
            style={
                'description_width': 'initial'},
            disabled=True
        )

        self.threshold_unwrap_refraction = widgets.FloatText(
            value=0.05,
            step=0.01,
            continuous_update=False,
            description='Threshold unwrap refraction:',
            readout=True,
            style={
                'description_width': 'initial'},
            disabled=True
        )

        self.unused_label_options = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Options",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.simulation = widgets.Checkbox(
            value=False,
            description='Simulated data',
            layout=widgets.Layout(width='33%'),
            style={
                'description_width': 'initial'}
        )

        self.invert_phase = widgets.Checkbox(
            value=True,
            description='Invert phase',
            layout=widgets.Layout(width='33%'),
            style={
                'description_width': 'initial'}
        )

        self.flip_reconstruction = widgets.Checkbox(
            value=False,
            description='Get conjugated object',
            layout=widgets.Layout(width='33%'),
            style={
                'description_width': 'initial'}
        )

        self.phase_ramp_removal = widgets.Dropdown(
            options=[
                "gradient", "upsampling"],
            value="gradient",
            description='Phase ramp removal:',
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.threshold_gradient = widgets.FloatText(
            value=1.0,
            step=0.01,
            continuous_update=False,
            description='Upper threshold gradient:',
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.save_raw = widgets.Checkbox(
            value=False,
            description='Save raw data',
            style={
                'description_width': 'initial'}
        )

        self.save_support = widgets.Checkbox(
            value=False,
            description='Save support',
            style={
                'description_width': 'initial'}
        )

        self.save = widgets.Checkbox(
            value=True,
            description='Save output',
            style={
                'description_width': 'initial'}
        )

        self.debug = widgets.Checkbox(
            value=False,
            description='Debug',
            style={
                'description_width': 'initial'}
        )

        self.roll_modes = widgets.Text(
            value="(0, 0, 0)",
            placeholder="(0, 0, 0)",
            description='Roll modes',
            continuous_update=False,
            layout=widgets.Layout(width='20%'),
            style={
                'description_width': 'initial'},
        )

        self.unused_label_data_vis = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Parameters related to data visualization",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.align_axis = widgets.Checkbox(
            value=False,
            description='Align axis',
            style={
                'description_width': 'initial'}
        )

        self.ref_axis = widgets.Dropdown(
            options=["x", "y", "z"],
            value="y",
            description='Ref axis for align axis',
            continuous_update=False,
            layout=widgets.Layout(width='20%'),
            tooltip="q will be aligned along that axis",
            style={'description_width': 'initial'}
        )

        self.axis_to_align = widgets.Text(
            value="[0.0, 0.0, 0.0]",
            placeholder="[0.0, 0.0, 0.0]",
            description='Axis to align for ref axis',
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.strain_range = widgets.FloatText(
            value=0.0001,
            step=0.000001,
            continuous_update=False,
            description='Strain range:',
            readout=True,
            style={
                'description_width': 'initial'}
        )

        self.phase_range = widgets.FloatText(
            value=np.round(np.pi, 3),
            step=0.001,
            continuous_update=False,
            description='Phase range:',
            readout=True,
            style={
                'description_width': 'initial'}
        )

        self.grey_background = widgets.Checkbox(
            value=True,
            description='Grey background in plots',
            layout=widgets.Layout(width='25%'),
            style={
                'description_width': 'initial'}
        )

        self.tick_spacing = widgets.BoundedIntText(
            value="100",
            description='Tick spacing:',
            min=0,
            max=5000,
            layout=widgets.Layout(width='25%'),
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.tick_direction = widgets.Dropdown(
            options=[
                "out", "in", "inout"],
            value="inout",
            description='Tick direction:',
            layout=widgets.Layout(width='25%'),
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.tick_length = widgets.BoundedIntText(
            value="3",
            description='Tick length:',
            min=0,
            max=50,
            continuous_update=False,
            layout=widgets.Layout(width='20%'),
            style={'description_width': 'initial'}
        )

        self.tick_width = widgets.BoundedIntText(
            value="1",
            description='Tick width:',
            min=0,
            max=10,
            continuous_update=False,
            layout=widgets.Layout(width='20%'),
            style={'description_width': 'initial'}
        )

        self.unused_label_average = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Parameters for averaging several reconstructed objects",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.averaging_space = widgets.Dropdown(
            options=[
                "reciprocal_space", "real_space"],
            value="reciprocal_space",
            description='Average method:',
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.threshold_avg = widgets.FloatText(
            value=0.90,
            step=0.01,
            continuous_update=False,
            description='Average threshold:',
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.unused_label_apodize = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Setup for phase averaging or apodization",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.apodize = widgets.Checkbox(
            value=True,
            description='Multiply diffraction pattern by filtering window',
            style={
                'description_width': 'initial'}
        )

        self.apodization_window = widgets.Dropdown(
            options=[
                "normal", "tukey", "blackman"],
            value="blackman",
            description='Filtering window',
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.half_width_avg_phase = widgets.BoundedIntText(
            value=1,
            continuous_update=False,
            description='Width of apodizing window:',
            readout=True,
            style={
                'description_width': 'initial'}
        )

        self.apodization_mu = widgets.Text(
            value="[0.0, 0.0, 0.0]",
            placeholder="[0.0, 0.0, 0.0]",
            description='Mu of gaussian window',
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.apodization_sigma = widgets.Text(
            value="[0.30, 0.30, 0.30]",
            placeholder="[0.30, 0.30, 0.30]",
            description='Sigma of gaussian window',
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.apodization_alpha = widgets.Text(
            value="[1.0, 1.0, 1.0]",
            placeholder="[1.0, 1.0, 1.0]",
            description='Alpha of gaussian window',
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.unused_label_strain = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Path to file",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.strain_folder = widgets.Dropdown(
            options=[x[0] + "/" for x in os.walk(os.getcwd())],
            value=os.getcwd() + "/",
            placeholder=os.getcwd() + "/",
            description='Data folder:',
            continuous_update=False,
            layout=widgets.Layout(width='90%'),
            style={'description_width': 'initial'}
        )

        self.reconstruction_file = widgets.Dropdown(
            options=[""]
            + [os.path.basename(f) for f in sorted(
                glob.glob(os.getcwd() + "/*.h5")
                + glob.glob(os.getcwd() + "/*.cxi")
                + glob.glob(os.getcwd() + "/*.npy")
                + glob.glob(os.getcwd() + "/*.npz"),
                key=os.path.getmtime)],
            description='Compatible file list',
            layout=widgets.Layout(width='90%'),
            style={'description_width': 'initial'}
        )

        self.init_postprocess_parameters = widgets.ToggleButtons(
            options=[
                ("Clear/ Reload folder", False),
                ("Determine disp and strain arrays", "run_strain"),
                ("Determine PRTF", "run_prtf"),
                ("Determine FSC", "run_fsc"),
                ("Determine SSC", "run_ssc"),
            ],
            value=False,
            description='Run strain analysis',
            button_style='',
            icon='fast-forward',
            layout=widgets.Layout(width='90%'),
            style={'description_width': 'initial'}
        )

        # Define children
        self.children = (
            self.unused_label_averaging,
            widgets.HBox([self.sort_method, self.correlation_threshold]),
            self.unused_label_FFT,
            widgets.HBox([self.original_size, self.phasing_binning]),
            widgets.HBox([self.preprocessing_binning, self.output_size]),
            widgets.HBox([self.keep_size, self.fix_voxel]),
            self.unused_label_disp_strain,
            widgets.HBox([self.data_frame, self.ref_axis_q]),
            widgets.HBox([
                self.save_frame, self.isosurface_strain,
                self.skip_unwrap, self.strain_method
            ]),
            widgets.HBox([
                self.phase_offset, self.phase_offset_origin,
                self.offset_method, self.centering_method_direct_space
            ]),
            self.unused_label_refraction,
            widgets.HBox([self.correct_refraction, self.optical_path_method]),
            widgets.HBox([self.dispersion, self.absorption,
                         self.threshold_unwrap_refraction]),
            self.unused_label_options,
            widgets.HBox([self.simulation, self.invert_phase,
                         self.flip_reconstruction]),
            widgets.HBox([self.phase_ramp_removal, self.threshold_gradient]),
            widgets.HBox([self.save_raw, self.save_support, self.save]),
            widgets.HBox([self.debug, self.roll_modes]),
            self.unused_label_data_vis,
            widgets.HBox([self.align_axis, self.ref_axis, self.axis_to_align]),
            widgets.HBox([self.strain_range, self.phase_range]),
            self.grey_background,
            widgets.HBox([self.tick_spacing, self.tick_direction,
                         self.tick_length, self.tick_width]),
            self.unused_label_average,
            widgets.HBox([self.averaging_space, self.threshold_avg]),
            self.unused_label_apodize,
            widgets.HBox([self.apodize, self.apodization_window,
                         self.half_width_avg_phase]),
            widgets.HBox(
                [self.apodization_mu, self.apodization_sigma, self.apodization_alpha]),
            self.unused_label_strain,
            self.strain_folder,
            self.reconstruction_file,
            self.init_postprocess_parameters,
        )

        # Assign handler
        self.strain_folder.observe(
            self.strain_folder_handler, names="value")

    # Define handlers
    def strain_folder_handler(self, change):
        """Handles changes on the widget used to load a data file."""
        if hasattr(change, "new"):
            change = change.new

        options = [""] + [os.path.basename(f) for f in sorted(
            glob.glob(change + "/*.h5")
            + glob.glob(change + "/*.cxi")
            + glob.glob(change + "/*.npy")
            + glob.glob(change + "/*.npz"),
            key=os.path.getmtime)
        ]

        self.reconstruction_file.options = options
