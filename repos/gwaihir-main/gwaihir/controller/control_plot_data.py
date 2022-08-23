import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import tables as tb
from IPython.display import display, clear_output, Image
import ipywidgets as widgets
from ipywidgets import interactive
from h5glance import H5Glance

from scipy.ndimage import gaussian_filter

from gwaihir.plot import Plotter, plot_3d_slices


def init_plot_data_tab(
    interface,
    unused_label_plot,
    parent_folder,
    filename,
    cmap,
    data_use,
):
    """
    Allows the user to plot an array (1D, 2D or 3D) from npz, npy or .cxi
    files.

    :param interface: GUI Interface Class
    :param parent_folder: parent_folder in which the files are located
    :param cmap: cmap used for plots
    :param filename: file name, can be multiple
    :param data_use: e.g. "2D"
     Can be "2D", "3D", "slices", "create_support", "extract_support",
     "smooth_support", "show_image", "hf_glance", "delete"
    """
    if data_use == "2D":
        # Plot data
        for p in filename:
            print(f"Showing {p}")
            Plotter(
                parent_folder + "/" + p,
                plot=data_use,
                log="interact",
                cmap=cmap
            )

    elif data_use == "3D" and len(filename) == 1:
        # Plot data
        Plotter(
            parent_folder + "/" + filename[0],
            plot=data_use,
            log="interact",
            cmap=cmap
        )

    elif data_use in [
        "slices", "contour_slices", "sum_slices", "sum_contour_slices"
    ]:
        # Plot data
        for p in filename:
            print(f"Showing {p}")
            Plotter(
                parent_folder + "/" + p,
                plot=data_use,
                log="interact",
                cmap=cmap
            )

    elif data_use == "create_support" and len(filename) == 1:
        # Disable widgets
        for w in interface.TabPlotData.children[:-1]:
            if not isinstance(w, widgets.HTML):
                w.disabled = True

        # Initialize class
        sup = SupportTools(
            path_to_data=parent_folder + "/" + filename[0])

        # Interactive function to loadt threshold value
        window_support = interactive(
            sup.compute_support,
            threshold=widgets.FloatText(
                value=0.05,
                step=0.001,
                max=1,
                min=0.001,
                continuous_update=False,
                description='Threshold:',
                readout=True,
                layout=widgets.Layout(width='20%'),
                style={
                    'description_width': 'initial'},
                disabled=False),
            compute=widgets.ToggleButton(
                value=False,
                description='Compute support ...',
                button_style='',
                icon='step-forward',
                layout=widgets.Layout(width='45%'),
                style={'description_width': 'initial'})
        )

        def support_handler(change):
            """Handles changes on the widget used for the initialization."""
            if not change.new:
                window_support.children[0].disabled = False

            if change.new:
                window_support.children[0].disabled = True

        window_support.children[1].observe(support_handler, names="value")

        display(window_support)

        # Update PyNX folder values
        interface.TabPhaseRetrieval.pynx_folder_handler(
            change=interface.preprocessing_folder)

    elif data_use == "extract_support" and len(filename) == 1:
        # Disable widgets
        for w in interface.TabPlotData.children[:-1]:
            if not isinstance(w, widgets.HTML):
                w.disabled = True

        # Initialize class
        sup = SupportTools(
            path_to_data=parent_folder + "/" + filename[0])

        # Extract the support from the data file and save it as npz
        sup.extract_support()

        # Update PyNX folder values
        interface.TabPhaseRetrieval.pynx_folder_handler(
            change=interface.preprocessing_folder)

    elif data_use == "smooth_support" and len(filename) == 1:
        # Disable widgets
        for w in interface.TabPlotData.children[:-1]:
            if not isinstance(w, widgets.HTML):
                w.disabled = True

        # Initialize class
        sup = SupportTools(
            path_to_support=parent_folder + "/" + filename[0])

        # Interactive function to loadt threshold value
        window_support = interactive(
            sup.gaussian_convolution,
            sigma=widgets.FloatText(
                value=0.05,
                step=0.001,
                max=1,
                min=0.001,
                continuous_update=False,
                description='Sigma:',
                readout=True,
                layout=widgets.Layout(width='20%'),
                style={'description_width': 'initial'}),
            threshold=widgets.FloatText(
                value=0.05,
                step=0.001,
                max=1,
                min=0.001,
                continuous_update=False,
                description='Threshold:',
                readout=True,
                layout=widgets.Layout(width='20%'),
                style={'description_width': 'initial'}),
            compute=widgets.ToggleButton(
                value=False,
                description='Compute support ...',
                button_style='',
                icon='step-forward',
                layout=widgets.Layout(width='45%'),
                style={'description_width': 'initial'})
        )

        def support_handler(change):
            """Handles changes on the widget used for the initialization."""
            if not change.new:
                window_support.children[0].disabled = False

            if change.new:
                window_support.children[0].disabled = True

        window_support.children[1].observe(support_handler, names="value")

        display(window_support)

        # Update PyNX folder values
        interface.TabPhaseRetrieval.pynx_folder_handler(
            change=interface.preprocessing_folder)

    elif data_use == "show_image":
        try:
            for p in filename:
                print(f"Showing {p}")
                display(Image(filename=parent_folder + "/" + p))

        except (FileNotFoundError, ValueError):
            print("Could not load image from file.")

    elif data_use == "hf_glance":
        # Show tree
        for p in filename:
            try:
                print(f"Showing {p}")
                display(H5Glance(parent_folder + "/" + filename[0]))
            except TypeError:
                print(
                    "This tool supports .nxs, .cxi or .hdf5 files only.")

    elif data_use in [
        "3D", "create_support", "extract_support",
        "smooth_support",
    ] and len(filename) != 1:
        print("Please select only one file.")

    elif data_use == "delete":
        # Disable widgets
        for w in interface.TabPlotData.children[:-2]:
            if not isinstance(w, widgets.HTML):
                w.disabled = True

        button_delete_data = widgets.Button(
            description="Delete files ?",
            button_style='',
            layout=widgets.Layout(width='70%'),
            style={'description_width': 'initial'},
            icon='step-forward')

        @ button_delete_data.on_click
        def action_button_delete_data(selfbutton):
            """Delete files."""
            for p in filename:
                try:
                    os.remove(parent_folder + "/" + p)
                    print(f"Removed {p}")

                except FileNotFoundError:
                    print(f"Could not remove {p}")

        display(button_delete_data)

    elif data_use is False:
        plt.close()
        for w in interface.TabPlotData.children[:-2]:
            if not isinstance(w, widgets.HTML):
                w.disabled = False
        interface.TabPlotData.plot_folder_handler(change=parent_folder)
        print("Cleared window.")
        clear_output(True)


class SupportTools:
    """
    Class that regroups the methods used to create/extract/optimize support
    in BCDI.
    """

    def __init__(
        self,
        path_to_data=None,
        path_to_support=None,
        saving_directory=None
    ):
        """
        Initialize the class with either a reconstructed object or the
        support of the reconstructed object.

        :param path_to_data: path to reconstructed object file
        :param path_to_support: path to support of reconstructed object file
        :param saving_directory: where the figures will be saved
        """
        self.path_to_data = path_to_data
        self.path_to_support = path_to_support

        if saving_directory is None:
            try:
                self.saving_directory = self.path_to_data.replace(
                    self.path_to_data.split("/")[-1], "")
            except AttributeError:
                try:
                    self.saving_directory = self.path_to_support.replace(
                        self.path_to_support.split("/")[-1], "")
                except AttributeError:
                    raise AttributeError("Please provide a saving_directory.")
        else:
            self.saving_directory = saving_directory

    def extract_support(self, compute=True):
        """Extract support as a 3D array of 0 et 1 from a reconstruction.

        :param compute: True to run function
        """
        # Work on cxi files
        if compute:
            if self.path_to_data.endswith(".cxi"):
                try:
                    with tb.open_file(self.path_to_data, "r") as f:

                        # Since .cxi files follow a specific architectture,
                        # we know where the mask is.
                        support = f.root.entry_1.image_1.mask[:]

                        # Save support
                        print(
                            "\n###################"
                            "#####################"
                            "#####################"
                            "#####################"
                        )
                        np.savez_compressed(self.saving_directory +
                                            "extracted_support.npz", support=support)
                        print(f"Saved support in {self.saving_directory} as:")
                        print("\textracted_support.npz")
                        print(
                            "#####################"
                            "#####################"
                            "#####################"
                            "###################\n"
                        )
                        plot_3d_slices(support, log="interact")
                except tb.NoSuchNodeError:
                    print("Data type not supported")

            # elif self.self.path_to_data.endswith(".npz"):

            else:
                print("Data type not supported")

        else:
            clear_output(True)
            print("Set compute to true to continue")

    def gaussian_convolution(self, sigma, threshold, compute=True):
        """
        Apply a gaussian convolution to the support, to avoid having holes
        inside.

        :param sigma: parameter used in scipy.ndimage.gaussian_filter
        :param threshold: threshold above which we define the support
         between 1 and 0, 1 being the maximum intensity
        :param compute: True to run function
        """
        if compute:
            try:
                old_support = np.load(self.path_to_support)["support"]
            except KeyError:
                try:
                    old_support = np.load(self.path_to_support)["data"]
                except KeyError:
                    try:
                        old_support = np.load(self.path_to_support)
                    except Exception as E:
                        print("Could not load 'data' or 'support' array from \
                            file.")
                        raise E
            except ValueError:
                print("Data type not supported")

            try:
                bigdata = 100 * old_support
                conv_support = np.where(gaussian_filter(
                    bigdata, sigma) > threshold, 1, 0)
                print(
                    "\n###################"
                    "#####################"
                    "#####################"
                    "#####################"
                )
                np.savez_compressed(
                    f"{self.saving_directory}filter_sig{sigma}_t{threshold}",
                    oldsupport=old_support, support=conv_support)

                print(f"Saved support in {self.saving_directory} as:")
                print(f"\tfilter_sig{sigma}_t{threshold}")
                print(
                    "#####################"
                    "#####################"
                    "#####################"
                    "###################\n"
                )

                plot_3d_slices(conv_support, log="interact")

            except UnboundLocalError:
                pass

        else:
            clear_output(True)
            print("Set compute to true to continue")

    def compute_support(self, threshold, compute=True):
        """
        Create support from data, based on maximum value of electronic
        density module, a threshold is applied.

        :param compute: True to run function
        """
        if compute:
            try:
                with tb.open_file(self.path_to_data, "r") as f:
                    # Since .cxi files follow a specific architecture,
                    # we know where our data is
                    if self.path_to_data.endswith(".cxi"):
                        electronic_density = f.root.entry_1.data_1.data[:]

                    elif self.path_to_data.endswith(".h5"):
                        # Take first mode
                        electronic_density = f.root.entry_1.data_1.data[:][0]

                    print(
                        "\n###################"
                        "#####################"
                        "#####################"
                        "#####################"
                    )
                    print("Shape of real space complex electronic density array:")
                    print(f"\t{np.shape(electronic_density)}")

                    # Find max value in image, we work with the module
                    amp = np.abs(electronic_density)
                    print(f"\tMaximum value in amplitude array: {amp.max()}")

                    # Define support based on max value and threshold
                    support = np.where(amp < threshold * amp.max(), 0, 1)

                    # Check % occupied by the support
                    rocc = np.where(support == 1)
                    rnocc = np.where(support == 0)

                    print("Percentage of 3D array occupied by support:")
                    print(f"\t{np.shape(rocc)[1] / np.shape(rnocc)[1]}")

                    # Save support
                    np.savez_compressed(self.saving_directory +
                                        "computed_support.npz", support=support)
                    print(f"Saved support in {self.saving_directory} as:")
                    print("\tcomputed_support.npz")
                    print(
                        "#####################"
                        "#####################"
                        "#####################"
                        "###################\n"
                    )

                    plot_3d_slices(support, log="interact")
            except tb.HDF5ExtError:
                print("Data type not supported")

        else:
            clear_output(True)
            print("Set compute to true to continue")
