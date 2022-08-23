import ipywidgets as widgets
import os
import glob
import matplotlib.pyplot as plt


class TabPlotData(widgets.VBox):
    """

    """

    def __init__(self, plot_tab_only=False, box_style=""):
        """

        """
        super(TabPlotData, self).__init__()

        # Brief header describing the tab
        self.header = 'Plot data'
        self.plot_tab_only = plot_tab_only
        self.box_style = box_style

        # Define widgets
        self.unused_label_plot = widgets.HTML(
            description="<p style='font-weight: bold;font-size:1.2em'>\
            Loads data files and displays it in the GUI",
            style={'description_width': 'initial'},
            layout=widgets.Layout(width='90%', height="35px")
        )

        self.parent_folder = widgets.Dropdown(
            options=[x[0] + "/" for x in os.walk(os.getcwd())],
            value=os.getcwd() + "/",
            placeholder=os.getcwd() + "/",
            description='Data folder:',
            continuous_update=False,
            layout=widgets.Layout(width='90%'),
            style={'description_width': 'initial'}
        )

        self.filename = widgets.SelectMultiple(
            options=[""]
            + [os.path.basename(f) for f in sorted(
                glob.glob(os.getcwd() + "/*.npy")
                + glob.glob(os.getcwd() + "/*.npz")
                + glob.glob(os.getcwd() + "/*.cxi")
                + glob.glob(os.getcwd() + "/*.h5")
                + glob.glob(os.getcwd() + "/*.nxs")
                + glob.glob(os.getcwd() + "/*.png"),
                key=os.path.getmtime)],
            rows=20,
            description='Compatible file list',
            layout=widgets.Layout(width='90%'),
            style={'description_width': 'initial'}
        )

        self.cmap = widgets.Dropdown(
            options=plt.colormaps(),
            value="turbo",
            description="Color map:",
            continuous_update=False,
            layout=widgets.Layout(width='90%'),
            style={'description_width': 'initial'}
        )

        self.data_use = widgets.ToggleButtons(
            options=[
                ("Clear/ Reload folder", False),
                ('2D plot', "2D"),
                ("Plot slices", "slices"),
                ("Plot contour slices", "contour_slices"),
                ("Plot sum over axes", "sum_slices"),
                ("Plot contour of sum over axes", "sum_contour_slices"),
                ("3D plot", "3D"),
                ("Create support", "create_support"),
                ("Extract support", "extract_support"),
                ("Smooth support", "smooth_support"),
                ("Display .png image", "show_image"),
                ("Display hdf5 tree", "hf_glance"),
                ("Delete selected files", "delete")
            ],
            value=False,
            description='Load data',
            tooltips=[
                "Clear the output and unload data from GUI, saves RAM",
                "Load data and plot data slice interactively",
                "Load data and plot data slices for each dimension in \
                its middle",
                "Load data and plot 3D data interactively",
                "Load data and allow for the creation of a support \
                interactively",
                "Load data and allow for the creation of a support \
                automatically",
                "Load support and smooth its boundaries",
                "Delete selected files, careful !!"
            ],
            button_style='',
            icon='fast-forward',
            layout=widgets.Layout(width='90%'),
            style={'description_width': 'initial'}
        )

        # Define children
        self.children = (
            self.unused_label_plot,
            self.parent_folder,
            self.filename,
            self.cmap,
            self.data_use,
        )

        # Assign handlers
        self.parent_folder.observe(
            self.plot_folder_handler, names="value")

    # Define handlers
    def plot_folder_handler(self, change):
        """Handles changes on the widget used to load a data file."""
        if hasattr(change, "new"):
            change = change.new

        options = [""] + [os.path.basename(f) for f in sorted(
            glob.glob(change + "/*.npy")
            + glob.glob(change + "/*.npz")
            + glob.glob(change + "/*.cxi")
            + glob.glob(change + "/*.h5")
            + glob.glob(change + "/*.nxs")
            + glob.glob(change + "/*.png"),
            key=os.path.getmtime)
        ]

        self.filename.options = [
            os.path.basename(f) for f in options]

        if self.plot_tab_only:
            self.parent_folder.options = [
                x[0] + "/" for x in os.walk(os.getcwd())
            ]
