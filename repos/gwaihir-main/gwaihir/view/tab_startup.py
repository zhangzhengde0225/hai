import ipywidgets as widgets
import os


class TabStartup(widgets.VBox):
    """

    """

    def __init__(self, box_style=""):
        """

        """
        super(TabStartup, self).__init__()

        # Brief header describing the tab
        self.header = 'Initialization'
        self.box_style = box_style

        # Define widgets
        self.unused_label_scan = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Define working directory and scan number",
            style={
                'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.sample_name = widgets.Text(
            value="S",
            placeholder="",
            description='Sample Name',
            continuous_update=False,
            layout=widgets.Layout(
                width='45%'),
            style={'description_width': 'initial'}
        )

        self.scan = widgets.BoundedIntText(
            value="01415",
            description='Scan nb:',
            min=0,
            max=9999999,
            continuous_update=False,
            layout=widgets.Layout(
                width='45%'),
            style={'description_width': 'initial'}
        )

        self.data_dir = widgets.Text(
            value=os.getcwd() + "/data_dir/",
            placeholder="Path to data directory",
            description='Data directory',
            continuous_update=False,
            layout=widgets.Layout(
                width='90%'),
            style={'description_width': 'initial'}
        )

        self.root_folder = widgets.Text(
            value=os.getcwd() + "/TestGui/",
            placeholder="Root folder (parent to all scan directories)",
            description='Target directory (root_folder)',
            continuous_update=False,
            layout=widgets.Layout(
                width='90%'),
            style={'description_width': 'initial'}
        )

        self.comment = widgets.Text(
            value="",
            description='Comment',
            continuous_update=False,
            layout=widgets.Layout(
                width='90%'),
            placeholder="Comment regarding Dataset...",
            style={'description_width': 'initial'}
        )

        self.debug = widgets.Checkbox(
            value=False,
            description='Debug scripts',
            tooltip='True to interact with plots, False to close it \
            automatically',
            indent=False,
            continuous_update=False,
            style={'description_width': 'initial'}
        )

        self.matplotlib_backend = widgets.Dropdown(
            options=[('Agg - No plots (faster)', 'Agg'), ('Qt5Agg - Interactive plots', 'Qt5Agg'),
                     ("ipympl- Plots in notebook output", "module://matplotlib_inline.backend_inline")],
            value="module://matplotlib_inline.backend_inline",
            description='Matplotlib backend for scripts:',
            continuous_update=False,
            layout=widgets.Layout(
                width='60%'),
            style={'description_width': 'initial'}
        )

        self.run_dir_init = widgets.ToggleButton(
            value=False,
            description='Initialize directories ...',
            button_style='',
            icon='step-forward',
            layout=widgets.Layout(
                width='45%'),
            style={'description_width': 'initial'}
        )

        # Define children
        self.children = (
            self.unused_label_scan,
            widgets.HBox([self.sample_name, self.scan]),
            self.data_dir,
            self.root_folder,
            self.comment,
            self.debug,
            self.matplotlib_backend,
            self.run_dir_init,
        )
