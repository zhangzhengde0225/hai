import ipywidgets as widgets
import os
import glob


class TabPhaseRetrieval(widgets.VBox):
    """

    """

    def __init__(self, box_style=""):
        """

        """
        super(TabPhaseRetrieval, self).__init__()

        # Brief header describing the tab
        self.header = 'Phase retrieval'
        self.box_style = box_style

        # Define widgets
        self.unused_label_data = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Data files",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.parent_folder = widgets.Dropdown(
            options=[x[0] + "/" for x in os.walk(os.getcwd())],
            value=os.getcwd() + "/",
            placeholder=os.getcwd() + "/",
            description='Parent folder:',
            continuous_update=False,
            layout=widgets.Layout(width='90%'),
            style={'description_width': 'initial'}
        )

        self.iobs = widgets.Dropdown(
            options=[""]
            + sorted([os.path.basename(f) for f in
                      glob.glob(os.getcwd() + "*.npz")],
                     key=os.path.getmtime),
            description='Dataset',
            layout=widgets.Layout(width='90%'),
            style={'description_width': 'initial'}
        )

        self.mask = widgets.Dropdown(
            options=[""]
            + sorted([os.path.basename(f) for f in
                      glob.glob(os.getcwd() + "*.npz")],
                     key=os.path.getmtime),
            description='Mask',
            layout=widgets.Layout(width='90%'),
            style={'description_width': 'initial'}
        )

        self.support = widgets.Dropdown(
            options=[""]
            + sorted([os.path.basename(f) for f in
                      glob.glob(os.getcwd() + "*.npz")],
                     key=os.path.getmtime),
            value="",
            description='Support',
            layout=widgets.Layout(width='90%'),
            style={'description_width': 'initial'}
        )

        self.obj = widgets.Dropdown(
            options=[""]
            + sorted([os.path.basename(f) for f in
                      glob.glob(os.getcwd() + "*.npz")],
                     key=os.path.getmtime),
            value="",
            description='Object',
            layout=widgets.Layout(width='90%'),
            style={'description_width': 'initial'}
        )

        self.auto_center_resize = widgets.Checkbox(
            value=False,
            description='Auto center and resize',
            continuous_update=False,
            indent=False,
            layout=widgets.Layout(height="50px"),
            icon='check'
        )

        self.max_size = widgets.BoundedIntText(
            value=256,
            step=1,
            min=0,
            max=1000,
            layout=widgets.Layout(
                height="50px", width="30%"),
            continuous_update=False,
            description='Maximum array size for cropping:',
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.unused_label_support = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Support parameters",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.support_threshold = widgets.Text(
            value="(0.23, 0.30)",
            placeholder="(0.23, 0.30)",
            description='Support threshold',
            layout=widgets.Layout(
                height="50px", width="20%"),
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.support_only_shrink = widgets.Checkbox(
            value=False,
            description='Support only shrink',
            continuous_update=False,
            indent=False,
            layout=widgets.Layout(
                height="50px", width="15%"),
            icon='check'
        )

        self.support_update_period = widgets.BoundedIntText(
            value=20,
            step=5,
            layout=widgets.Layout(
                height="50px", width="20%"),
            continuous_update=False,
            description='Support update period:',
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.support_smooth_width = widgets.Text(
            value="(2, 1, 600)",
            placeholder="(2, 1, 600)",
            description='Support smooth width',
            layout=widgets.Layout(
                height="50px", width="20%"),
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.support_post_expand = widgets.Text(
            value="(1, -2, 1)",
            placeholder="(1, -2, 1)",
            description='Support post expand',
            layout=widgets.Layout(width="20%"),
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.support_method = widgets.Dropdown(
            options=["max", "average", "rms"],
            value="rms",
            description='Support method',
            layout=widgets.Layout(width='15%'),
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.support_autocorrelation_threshold = widgets.Text(
            value="(0.10)",
            placeholder="(0.10)",
            description='Support autocorrelation threshold',
            layout=widgets.Layout(
                height="50px", width="25%"),
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.unused_label_psf = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Point spread function parameters",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.psf = widgets.Checkbox(
            value=True,
            description='Use point spread function',
            continuous_update=False,
            indent=False,
            layout=widgets.Layout(width="20%", height="50px"),
            icon='check'
        )

        self.psf_model = widgets.Dropdown(
            options=[
                "gaussian", "lorentzian", "pseudo-voigt"],
            value="pseudo-voigt",
            description='PSF peak shape',
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.fwhm = widgets.FloatText(
            value=0.5,
            step=0.01,
            min=0,
            continuous_update=False,
            description="FWHM:",
            layout=widgets.Layout(
                width='10%', height="50px"),
            style={
                'description_width': 'initial'}
        )

        self.eta = widgets.FloatText(
            value=0.05,
            step=0.01,
            max=1,
            min=0,
            continuous_update=False,
            description='Eta:',
            layout=widgets.Layout(
                width='10%', height="50px"),
            readout=True,
            style={
                'description_width': 'initial'}
        )

        self.psf_filter = widgets.Dropdown(
            options=["None", "hann", "tukey"],
            value="None",
            description='PSF filter',
            layout=widgets.Layout(width='15%'),
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.update_psf = widgets.BoundedIntText(
            value=20,
            step=5,
            continuous_update=False,
            description='Update PSF every:',
            layout=widgets.Layout(
                width='15%', height="50px"),
            readout=True,
            style={
                'description_width': 'initial'}
        )

        self.unused_label_algo = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Iterative algorithms parameters",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.nb_raar = widgets.BoundedIntText(
            value=1000,
            min=0,
            max=9999,
            step=10,
            continuous_update=False,
            description='Nb of RAAR:',
            layout=widgets.Layout(
                height="35px", width="15%"),
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.nb_hio = widgets.BoundedIntText(
            value=400,
            min=0,
            max=9999,
            step=10,
            continuous_update=False,
            description='Nb of HIO:',
            layout=widgets.Layout(
                height="35px", width="15%"),
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.nb_er = widgets.BoundedIntText(
            value=300,
            min=0,
            max=9999,
            step=10,
            continuous_update=False,
            description='Nb of ER:',
            layout=widgets.Layout(
                height="35px", width="15%"),
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.nb_ml = widgets.BoundedIntText(
            value=0,
            min=0,
            max=9999,
            step=10,
            continuous_update=False,
            description='Nb of ML:',
            layout=widgets.Layout(
                height="35px", width="15%"),
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.nb_run = widgets.BoundedIntText(
            value=30,
            min=0,
            max=100,
            continuous_update=False,
            description='Number of run:',
            layout=widgets.Layout(width="15%", height="50px"),
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.unused_label_filtering = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Filtering criteria for reconstructions",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.filter_criteria = widgets.Dropdown(
            options=[
                ("No filtering",
                 "no_filtering"),
                ("Standard deviation",
                    "standard_deviation"),
                ("Log-likelihood (FLLK)", "FLLK"),
                ("FLLK > Standard deviation",
                    "FLLK_standard_deviation"),
                # ("Standard deviation > FLLK", "standard_deviation_FLLK"),
            ],
            value="FLLK_standard_deviation",
            description='Filtering criteria',
            layout=widgets.Layout(width='30%'),
            style={'description_width': 'initial'}
        )

        self.nb_run_keep = widgets.BoundedIntText(
            value=10,
            continuous_update=False,
            description='Number of run to keep:',
            layout=widgets.Layout(width='20%', height="50px"),
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.unused_label_options = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Options",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.live_plot = widgets.BoundedIntText(
            value=200,
            step=10,
            max=500,
            min=0,
            continuous_update=False,
            description='Plot every:',
            readout=True,
            layout=widgets.Layout(
                height="50px", width="15%"),
            style={
                'description_width': 'initial'},
        )

        self.plot_axis = widgets.Dropdown(
            options=[0, 1, 2],
            value=0,
            description='Axis used for plots',
            layout=widgets.Layout(width='15%'),
            style={'description_width': 'initial'}
        )

        self.verbose = widgets.BoundedIntText(
            value=100,
            min=10,
            max=300,
            continuous_update=False,
            description='Verbose:',
            layout=widgets.Layout(width='15%', height="50px"),
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.rebin = widgets.Text(
            value="(1, 1, 1)",
            placeholder="(1, 1, 1)",
            description='Rebin',
            layout=widgets.Layout(width='10%', height="50px"),
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.pixel_size_detector = widgets.BoundedIntText(
            value=55,
            continuous_update=False,
            description='Pixel size of detector (um):',
            layout=widgets.Layout(width="20%", height="50px"),
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.positivity = widgets.Checkbox(
            value=False,
            description='Force positivity',
            continuous_update=False,
            indent=False,
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(
                height="50px", width="15%"),
            icon='check'
        )

        self.beta = widgets.FloatText(
            value=0.9,
            step=0.01,
            max=1,
            min=0,
            continuous_update=False,
            description='Beta parameter for RAAR and HIO:',
            layout=widgets.Layout(
                width='25%', height="50px"),
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.detwin = widgets.Checkbox(
            value=False,
            description='Detwinning',
            continuous_update=False,
            indent=False,
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(
                height="50px", width="15%"),
            icon='check'
        )

        self.calc_llk = widgets.BoundedIntText(
            value=50,
            min=0,
            max=100,
            continuous_update=False,
            description='Log likelihood update interval:',
            layout=widgets.Layout(width="25%", height="50px"),
            readout=True,
            style={
                'description_width': 'initial'},
        )

        self.unused_label_mask_options = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Mask options</p>",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.zero_mask = widgets.Dropdown(
            options=("True", "False", 'auto'),
            value='False',
            description='Force mask pixels to zero',
            continuous_update=False,
            indent=False,
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width="20%"),
            icon='check'
        )

        self.mask_interp = widgets.Text(
            value="(8, 2)",
            description='Mask interp.',
            layout=widgets.Layout(
                height="50px", width="20%"),
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.unused_label_phase_retrieval = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Click below to run the phase retrieval</p>",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.run_phase_retrieval = widgets.ToggleButtons(
            options=[
                ('No phase retrieval', False),
                ('Run batch job (slurm)', "batch"),
                ("Run script locally",
                    "local_script"),
                ("Use operators",
                    "operators"),
            ],
            value=False,
            tooltips=[
                "Click to be able to change parameters",
                "Collect parameters to run a job on slurm, will \
                automatically apply a std deviation filter and run modes \
                decomposition, freed the kernel",
                "Run script on jupyter notebook environment, uses notebook\
                 kernel, will be performed in background also but more \
                 slowly, good if you cannot use jobs.",
                r"Use operators on local environment, if using PSF, it is \
                activated after 50\% of RAAR cycles"
            ],
            description='Run phase retrieval ...',
            continuous_update=False,
            button_style='',
            layout=widgets.Layout(
                width='100%', height="50px"),
            style={
                'description_width': 'initial'},
            icon='fast-forward'
        )

        self.unused_label_run_pynx_tools = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Click below to use a phase retrieval tool</p>",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.run_pynx_tools = widgets.ToggleButtons(
            options=[
                ('No tool running', False),
                ("Modes decomposition",
                    "modes"),
                ("Filter reconstructions",
                    "filter")
            ],
            value=False,
            tooltips=[
                "Click to be able to change parameters",
                "Run modes decomposition in data folder, selects *FLLK*.cxi\
                 files",
                "Filter reconstructions"
            ],
            description="Choose analysis:",
            continuous_update=False,
            button_style='',
            layout=widgets.Layout(
                width='100%', height="50px"),
            style={
                'description_width': 'initial'},
            icon='fast-forward'
        )

        # Define children
        self.children = (
            self.unused_label_data,
            self.parent_folder,
            self.iobs,
            self.mask,
            self.support,
            self.obj,
            widgets.HBox([
                self.auto_center_resize,
                self.max_size,
            ]),
            self.unused_label_support,
            widgets.HBox([
                self.support_threshold,
                self.support_only_shrink
            ]),
            widgets.HBox([
                self.support_update_period,
                self.support_smooth_width,
                self.support_post_expand,
                self.support_method,
            ]),
            self.support_autocorrelation_threshold,
            self.unused_label_psf,
            widgets.HBox([
                self.psf,
                self.psf_model,
                self.fwhm,
                self.eta,
                self.psf_filter,
            ]),
            self.update_psf,
            self.unused_label_algo,
            widgets.HBox([
                self.nb_hio,
                self.nb_raar,
                self.nb_er,
                self.nb_ml,
            ]),
            self.nb_run,
            self.unused_label_filtering,
            widgets.HBox([
                self.filter_criteria,
                self.nb_run_keep,
            ]),
            self.unused_label_options,
            widgets.HBox([
                self.live_plot,
                self.plot_axis,
                self.verbose,
            ]),
            widgets.HBox([
                self.rebin,
                self.pixel_size_detector,
            ]),
            widgets.HBox([
                self.positivity,
                self.beta,
                self.detwin,
                self.calc_llk,
            ]),
            self.unused_label_mask_options,
            widgets.HBox([
                self.zero_mask,
                self.mask_interp,
            ]),
            self.unused_label_phase_retrieval,
            self.run_phase_retrieval,
            self.unused_label_run_pynx_tools,
            self.run_pynx_tools,
        )

        # Assign handler
        self.parent_folder.observe(
            self.pynx_folder_handler, names="value")
        self.psf.observe(
            self.pynx_psf_handler, names="value")
        self.psf_model.observe(
            self.pynx_peak_shape_handler, names="value")
        self.run_phase_retrieval.observe(
            self.run_pynx_handler, names="value")
        self.run_pynx_tools.observe(
            self.run_pynx_handler, names="value")

    # Define handlers
    def pynx_folder_handler(self, change):
        """Handles changes on the widget used to load a data file."""
        if hasattr(change, "new"):
            change = change.new

        list_all_npz = [os.path.basename(f) for f in sorted(
            glob.glob(change + "/*.npz"), key=os.path.getmtime)]

        list_probable_iobs_files = [os.path.basename(f) for f in sorted(
            glob.glob(change + "/*_pynx_*.npz"), key=os.path.getmtime)]

        list_probable_mask_files = [os.path.basename(f) for f in sorted(
            glob.glob(change + "/*maskpynx*.npz"), key=os.path.getmtime)]

        # support list
        self.support.options = [""]\
            + [os.path.basename(f) for f in sorted(
                glob.glob(change + "/*.npz"), key=os.path.getmtime)]

        # obj list
        self.obj.options = [""]\
            + [os.path.basename(f) for f in sorted(
                glob.glob(change + "/*.npz"), key=os.path.getmtime)]

        # Find probable iobs file
        temp_list = list_all_npz.copy()
        for f in list_probable_iobs_files:
            try:
                temp_list.remove(f)
            except ValueError:
                # Not in list
                pass
        sorted_iobs_list = list_probable_iobs_files + temp_list + [""]

        # Find probable mask file
        temp_list = list_all_npz.copy()
        for f in list_probable_mask_files:
            try:
                temp_list.remove(f)
            except ValueError:
                # not in list
                pass
        sorted_mask_list = list_probable_mask_files + temp_list + [""]

        # iobs list
        self.iobs.options = sorted_iobs_list

        # mask list
        self.mask.options = sorted_mask_list

    def pynx_psf_handler(self, change):
        """Handles changes related to the psf."""
        if hasattr(change, "new"):
            change = change.new

        for w in [
            self.psf_model,
            self.fwhm,
            self.eta,
            self.psf_filter,
            self.update_psf,
        ]:
            if change:
                w.disabled = False
            else:
                w.disabled = True

        self.pynx_peak_shape_handler(
            change=self.psf_model.value)

    def pynx_peak_shape_handler(self, change):
        """Handles changes related to psf the peak shape."""
        if hasattr(change, "new"):
            change = change.new

        if change != "pseudo-voigt":
            self.eta.disabled = True

        else:
            self.eta.disabled = False

    def run_pynx_handler(self, change):
        """Handles changes related to the phase retrieval."""

        if change.new:
            for w in self.children[:-1]:
                if isinstance(w, widgets.widgets.widget_box.HBox):
                    for wc in w.children:
                        wc.disabled = True
                else:
                    w.disabled = True

            self.run_phase_retrieval.disabled = False

        elif not change.new:
            for w in self.children[:-1]:
                if isinstance(w, widgets.widgets.widget_box.HBox):
                    for wc in w.children:
                        wc.disabled = False
                else:
                    w.disabled = False

            self.pynx_psf_handler(
                change=self.psf.value)
