import ipywidgets as widgets
import os


class TabDetector(widgets.VBox):
    """

    """

    def __init__(self, box_style=""):
        """

        """
        super(TabDetector, self).__init__()

        # Brief header describing the tab
        self.header = 'Detector'
        self.box_style = box_style

        # Define widgets
        self.unused_label_detector = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Parameters related to the detector used</p>",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.detector = widgets.Dropdown(
            options=[
                "Eiger2M", "Maxipix", "Eiger4M", "Merlin", "MerlinSixS", "Timepix"],
            value="Merlin",
            description='Detector',
            continuous_update=False,
            disabled=True,
            style={'description_width': 'initial'}
        )

        self.roi_detector = widgets.Text(
            placeholder="""[low_y_bound, high_y_bound, low_x_bound, high_x_bound]""",
            description='Fix roi area, will overwrite cropping parameters',
            disabled=True,
            continuous_update=False,
            layout=widgets.Layout(
                width='90%'),
            style={'description_width': 'initial'}
        )

        self.photon_threshold = widgets.IntText(
            value=0,
            description='Photon Threshold:',
            disabled=True,
            continuous_update=False,
            tooltip="data[data < photon_threshold] = 0",
            style={'description_width': 'initial'}
        )

        self.photon_filter = widgets.Dropdown(
            options=[
                'loading', 'postprocessing'],
            value="loading",
            continuous_update=False,
            description='Photon filter',
            disabled=True,
            tooltip="When the photon threshold should be applied, if \
            'loading', it is applied before binning; if 'postprocessing',\
             it is applied at the end of the script before saving",
            style={'description_width': 'initial'}
        )

        self.background_file = widgets.Text(
            value="",
            placeholder=f"{os.getcwd()}/background.npz'",
            description='Background file',
            disabled=True,
            continuous_update=False,
            layout=widgets.Layout(
                width='90%'),
            style={'description_width': 'initial'}
        )

        self.flatfield_file = widgets.Text(
            value="",
            placeholder=f"{os.getcwd()}/flatfield_maxipix_8kev.npz",
            description='Flatfield file',
            disabled=True,
            continuous_update=False,
            layout=widgets.Layout(
                width='90%'),
            style={'description_width': 'initial'}
        )

        self.hotpixels_file = widgets.Text(
            value="",
            placeholder=f"{os.getcwd()}/mask_merlin.npz",
            description='Hotpixels file',
            disabled=True,
            continuous_update=False,
            layout=widgets.Layout(
                width='90%'),
            style={'description_width': 'initial'}
        )

        self.template_imagefile = widgets.Text(
            value='Pt_ascan_mu_%05d.nxs',
            description='Template imagefile',
            disabled=True,
            layout=widgets.Layout(
                width='90%'),
            style={'description_width': 'initial'}
        )

        # Define children
        self.children = (
            self.unused_label_detector,
            self.detector,
            self.roi_detector,
            widgets.HBox([self.photon_threshold, self.photon_filter]),
            self.background_file,
            self.flatfield_file,
            self.hotpixels_file,
            self.template_imagefile,
        )

    def __str__(self):
        return "Detector tab"
