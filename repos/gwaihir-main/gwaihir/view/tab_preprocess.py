import ipywidgets as widgets


class TabPreprocess(widgets.VBox):
    """

    """

    def __init__(self, box_style=""):
        """

        """
        super(TabPreprocess, self).__init__()

        # Brief header describing the tab
        self.header = 'Preprocess'
        self.box_style = box_style

        # Define widgets
        self.unused_label_beamline = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Parameters specific to the beamline",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.beamline = widgets.Dropdown(
            options=['ID01', 'SIXS_2018', 'SIXS_2019',
                     'CRISTAL', 'P10', 'NANOMAX', '34ID',
                     "ID01BLISS", "ID27"],
            value="SIXS_2019",
            description='Beamline',
            continuous_update=False,
            disabled=True,
            tooltip="Name of the beamline, used for data loading and \
            normalization by monitor",
            style={'description_width': 'initial'}
        )

        self.actuators = widgets.Text(
            value="{}",
            placeholder="{}",
            continuous_update=False,
            description='Actuators',
            tooltip="Optional dictionary that can be used to define the \
            entries corresponding to actuators in data files (useful at \
            CRISTAL where the location of data keeps changing)",
            readout=True,
            style={
                'description_width': 'initial'},
            disabled=True
        )

        self.is_series = widgets.Checkbox(
            value=False,
            description='Is series (P10)',
            disabled=True,
            continuous_update=False,
            tooltip='specific to series measurement at P10',
            icon='check'
        )

        self.custom_scan = widgets.Checkbox(
            value=False,
            description='Custom scan',
            continuous_update=False,
            disabled=True,
            indent=False,
            tooltip='set it to True for a stack of images acquired without\
             scan, e.g. with ct in a macro, or when there is no spec/log \
             file available',
            icon='check'
        )

        self.custom_images = widgets.Text(
            value="[]",
            description='Custom images',
            continuous_update=False,
            disabled=True,
            style={'description_width': 'initial'}
        )

        self.custom_monitor = widgets.IntText(
            value=0,
            description='Custom monitor',
            continuous_update=False,
            disabled=True,
            style={'description_width': 'initial'}
        )

        self.specfile_name = widgets.Text(
            placeholder="alias_dict_2019.txt",
            value="",
            description='Specfile name',
            disabled=True,
            continuous_update=False,
            layout=widgets.Layout(
                width='90%'),
            style={'description_width': 'initial'}
        )

        self.rocking_angle = widgets.Dropdown(
            options=[
                'inplane', 'outofplane', 'energy'],
            value="inplane",
            continuous_update=False,
            description='Rocking angle',
            disabled=True,
            tooltip="Name of the beamline, used for data loading and \
            normalization by monitor",
            layout=widgets.Layout(
                height="50px"),
            style={'description_width': 'initial'}
        )

        self.unused_label_masking = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Parameters used in masking",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.flag_interact = widgets.Checkbox(
            value=False,
            description='Manual masking',
            continuous_update=False,
            disabled=True,
            indent=False,
            tooltip='True to interact with plots and manually mask points',
            layout=widgets.Layout(
                height="50px"),
            icon='check'
        )

        self.background_plot = widgets.FloatText(
            value=0.5,
            step=0.01,
            max=1,
            min=0,
            continuous_update=False,
            description='Background plot:',
            layout=widgets.Layout(
                width='30%', height="50px"),
            tooltip="In level of grey in [0,1], 0 being dark. For visual \
            comfort during masking",
            readout=True,
            style={
                'description_width': 'initial'},
            disabled=True
        )

        self.unused_label_centering = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Parameters related to data cropping/padding/centering</p>",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='60%', height="35px")
        )

        self.centering_method_reciprocal_space = widgets.Dropdown(
            options=[
                "max", "com", "manual"],
            value="max",
            description='Centering of Bragg peak method:',
            continuous_update=False,
            disabled=True,
            layout=widgets.Layout(
                width='45%'),
            tooltip="Bragg peak determination: 'max' or 'com', 'max' is \
            better usually. It will be overridden by 'bragg_peak' if \
            not empty",
            style={'description_width': 'initial'}
        )

        self.bragg_peak = widgets.Text(
            placeholder="[z_bragg, y_bragg, x_bragg]",
            description='Bragg peak position',
            disabled=True,
            continuous_update=False,
            layout=widgets.Layout(
                width='45%'),
            style={'description_width': 'initial'}
        )

        self.fix_size = widgets.Text(
            placeholder="[zstart, zstop, ystart, ystop, xstart, xstop]",
            description='Fix array size',
            disabled=True,
            continuous_update=False,
            layout=widgets.Layout(
                width='45%'),
            style={'description_width': 'initial'}
        )

        self.center_fft = widgets.Dropdown(
            options=[
                'crop_sym_ZYX', 'crop_asym_ZYX', 'pad_asym_Z_crop_sym_YX',
                'pad_sym_Z_crop_asym_YX', 'pad_sym_Z', 'pad_asym_Z',
                'pad_sym_ZYX', 'pad_asym_ZYX', 'skip'],
            value="crop_sym_ZYX",
            description='Center FFT',
            continuous_update=False,
            layout=widgets.Layout(
                height="50px"),
            disabled=True,
            style={'description_width': 'initial'}
        )

        self.pad_size = widgets.Text(
            placeholder="[256, 512, 512]",
            description='Array size after padding',
            disabled=True,
            continuous_update=False,
            layout=widgets.Layout(
                width='50%', height="50px"),
            style={'description_width': 'initial'}
        )

        self.normalize_flux = widgets.Dropdown(
            options=[
                "skip", "monitor"],
            value="skip",
            description='Normalize flux',
            disabled=True,
            continuous_update=False,
            layout=widgets.Layout(
                height="50px", width="25%"),
            tooltip='Monitor to normalize the intensity by the default \
            monitor values, skip to do nothing',
            style={'description_width': 'initial'}
        )

        self.unused_label_filtering = widgets.HTML(
            description="""<p style='font-weight: bold;font-size:1.2em'>\
            Parameters for data filtering</p>""",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.mask_zero_event = widgets.Checkbox(
            value=False,
            description='Mask zero event',
            disabled=True,
            continuous_update=False,
            indent=False,
            tooltip='Mask pixels where the sum along the rocking curve is \
            zero - may be dead pixels',
            icon='check'
        )

        self.median_filter = widgets.Dropdown(
            options=[
                'skip', 'median', 'interp_isolated', 'mask_isolated'],
            value="skip",
            description='Flag median filter',
            continuous_update=False,
            disabled=True,
            tooltip="set to 'median' for applying med2filter [3,3], set to \
            'interp_isolated' to interpolate isolated empty pixels based on\
             'median_filter_order' parameter, set to 'mask_isolated' it \
             will mask isolated empty pixels, set to 'skip' will skip \
             filtering",
            style={'description_width': 'initial'}
        )

        self.median_filter_order = widgets.IntText(
            value=7,
            description='Med filter order:',
            disabled=True,
            continuous_update=False,
            tooltip="for custom median filter, number of pixels with \
            intensity surrounding the empty pixel",
            style={'description_width': 'initial'}
        )

        self.phasing_binning = widgets.Text(
            value="(1, 1, 1)",
            placeholder="(1, 1, 1)",
            description='Binning for phasing',
            disabled=True,
            continuous_update=False,
            layout=widgets.Layout(
                width='20%', height="50px"),
            style={
                'description_width': 'initial'},
            tooltip="binning that will be used for phasing (stacking \
            dimension, detector vertical axis, detector horizontal axis)"
        )

        self.unused_label_reload = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Parameters used when reloading processed data</p>",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.reload_previous = widgets.Checkbox(
            value=False,
            description='Reload previous',
            continuous_update=False,
            disabled=True,
            indent=False,
            layout=widgets.Layout(
                height="50px"),
            tooltip='True to resume a previous masking (load data\
            and mask)',
            icon='check'
        )

        self.reload_orthogonal = widgets.Checkbox(
            value=False,
            description='Reload orthogonal',
            continuous_update=False,
            disabled=True,
            indent=False,
            layout=widgets.Layout(
                height="50px"),
            tooltip='True if the reloaded data is already intepolated \
            in an orthonormal frame',
            icon='check'
        )

        self.preprocessing_binning = widgets.Text(
            value="(1, 1, 1)",
            placeholder="(1, 1, 1)",
            description='Binning used in data to be reloaded',
            disabled=True,
            continuous_update=False,
            layout=widgets.Layout(
                width='30%', height="50px"),
            style={
                'description_width': 'initial'},
            tooltip="binning that will be used for phasing (stacking \
            dimension, detector vertical axis, detector horizontal axis)"
        )

        self.unused_label_saving = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Parameters used when saving the data</p>",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.save_rawdata = widgets.Checkbox(
            value=False,
            description='Save raw data',
            disabled=True,
            continuous_update=False,
            indent=False,
            layout=widgets.Layout(
                width="15%", height="50px"),
            tooltip='Save also the raw data when use_rawdata is False',
            icon='check'
        )

        self.save_to_npz = widgets.Checkbox(
            value=True,
            description='Save to npz',
            disabled=True,
            continuous_update=False,
            indent=False,
            layout=widgets.Layout(
                width="15%", height="50px"),
            tooltip='True to save the processed data in npz format',
            icon='check'
        )

        self.save_to_mat = widgets.Checkbox(
            value=False,
            description='Save to mat',
            disabled=True,
            continuous_update=False,
            indent=False,
            layout=widgets.Layout(
                width="15%", height="50px"),
            tooltip='True to save also in .mat format',
            icon='check'
        )

        self.save_to_vti = widgets.Checkbox(
            value=False,
            description='Save to vti',
            continuous_update=False,
            disabled=True,
            indent=False,
            layout=widgets.Layout(
                width="15%", height="50px"),
            tooltip='Save the orthogonalized diffraction pattern to \
            VTK file',
            icon='check'
        )

        self.save_as_int = widgets.Checkbox(
            value=False,
            description='Save as int',
            continuous_update=False,
            disabled=True,
            indent=False,
            layout=widgets.Layout(
                width="15%", height="50px"),
            tooltip='if True, the result will be saved as an array of \
            integers (save space)',
            icon='check'
        )

        self.unused_label_preprocess = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Click below to run the data processing before phasing</p>",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.run_preprocess = widgets.ToggleButtons(
            options=[
                ("False", False),
                ("In GUI.", "GUI"),
                ("In terminal.", "terminal"),
            ],
            value=False,
            description="Run preprocess:",
            continuous_update=False,
            button_style='',
            layout=widgets.Layout(
                width='100%', height="50px"),
            style={
                'description_width': 'initial'},
            icon='fast-forward')

        # Define children
        self.children = (
            # Beamline
            self.unused_label_beamline,
            self.beamline,
            widgets.HBox([self.actuators, self.is_series]),
            widgets.HBox(
                [self.custom_scan, self.custom_images, self.custom_monitor]),
            self.specfile_name,
            self.rocking_angle,
            self.unused_label_masking,
            widgets.HBox([self.flag_interact, self.background_plot]),

            # Parameters related to data cropping/padding/centering
            self.unused_label_centering,
            widgets.HBox(
                [self.centering_method_reciprocal_space, self.bragg_peak]),
            self.fix_size,
            widgets.HBox(
                [self.center_fft, self.pad_size, self.normalize_flux]),
            self.unused_label_filtering,
            widgets.HBox(
                [self.mask_zero_event, self.median_filter, self.median_filter_order]),
            self.phasing_binning,

            # Parameters used when reloading processed data
            self.unused_label_reload,
            widgets.HBox(
                [self.reload_previous, self.reload_orthogonal, self.preprocessing_binning]),
            self.unused_label_saving,
            widgets.HBox([self.save_rawdata, self.save_to_npz,
                         self.save_to_mat, self.save_to_vti, self.save_as_int]),
            self.unused_label_preprocess,
            self.run_preprocess,
        )

        # Assign handlers
        self.beamline.observe(
            self.beamline_handler, names="value")
        self.centering_method_reciprocal_space.observe(
            self.bragg_peak_centering_handler, names="value")
        self.reload_previous.observe(
            self.reload_data_handler, names="value")

    # Define handlers
    def beamline_handler(self, change):
        """Handles changes on the widget used for the beamline."""
        if hasattr(change, "new"):
            change = change.new

        for w in [
            self.actuators,
            self.is_series,
            self.custom_scan,
            self.custom_images,
            self.custom_monitor,
        ]:
            if change in ["SIXS_2019", "ID01"]:
                w.disabled = True
            else:
                w.disabled = False

    def bragg_peak_centering_handler(self, change):
        """Handles changes related to the centering of the Bragg peak."""
        if hasattr(change, "new"):
            change = change.new

        if change == "manual":
            self.bragg_peak.disabled = False

        if change != "manual":
            self.bragg_peak.disabled = True

    def reload_data_handler(self, change):
        """Handles changes related to data reloading."""
        if hasattr(change, "new"):
            change = change.new

        for w in [
            self.reload_orthogonal,
            self.preprocessing_binning,
        ]:
            if change:
                w.disabled = False
            else:
                w.disabled = True
