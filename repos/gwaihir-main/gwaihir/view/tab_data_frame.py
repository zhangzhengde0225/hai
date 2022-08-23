import ipywidgets as widgets
import glob
import os


class TabDataFrame(widgets.VBox):
    """

    """

    def __init__(self, box_style=""):
        """

        """
        super(TabDataFrame, self).__init__()

        # Brief header describing the tab
        self.header = 'Display DataFrames'
        self.box_style = box_style

        # Define widgets
        self.unused_label_logs = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Loads csv file and displays it in the GUI",
            style={'description_width': 'initial'},
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

        self.csv_file = widgets.Dropdown(
            options=sorted(glob.glob(os.getcwd()+"*.csv"),
                           key=os.path.getmtime),
            description='csv file in subdirectories:',
            continuous_update=False,
            layout=widgets.Layout(width='90%'),
            style={'description_width': 'initial'}
        )

        self.show_logs = widgets.ToggleButtons(
            options=[
                ("Clear/ Reload folder", False),
                ('Load .csv file', "load_csv"),
                ("Load facets data ", "load_field_data"),
            ],
            value=False,
            description='Load dataframe',
            button_style='',
            layout=widgets.Layout(width='90%'),
            style={'description_width': 'initial'}
        )

        # Define children
        self.children = (
            self.unused_label_logs,
            self.parent_folder,
            self.csv_file,
            self.show_logs,
        )

        # Assign handlers
        self.parent_folder.observe(
            self.csv_file_handler, names="value")

    # Define handlers
    def csv_file_handler(self, change):
        """List all .csv files in change subdirectories"""
        csv_files = []

        if hasattr(change, "new"):
            change = change.new

        for x in os.walk(change):
            csv_files += sorted(glob.glob(f"{x[0]}/*.csv"),
                                key=os.path.getmtime)

        self.csv_file.options = csv_files

    def __str__(self):
        return "DataFrame tab"
