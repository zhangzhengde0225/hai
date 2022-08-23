import warnings
import numpy as np
import h5py as h5
import os

from tornado.ioloop import PeriodicCallback

from skimage.measure import marching_cubes
from scipy.spatial.transform import Rotation
from scipy.interpolate import RegularGridInterpolator

import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import LogNorm, Normalize
from mpl_toolkits.axes_grid1.axes_divider import make_axes_locatable

import ipywidgets as widgets
from ipywidgets import interact, fixed
from IPython.core.display import display, HTML
import ipyvolume as ipv

from bokeh.plotting import figure
from bokeh.layouts import row
from bokeh.io import output_notebook
from bokeh.models import ColumnDataSource, ColorBar, LinearColorMapper
from bokeh.models import Slider, RadioButtonGroup
import bokeh.palettes as bp
import panel as pn
pn.extension()

warnings.filterwarnings("ignore")


class Plotter:
    """
    Class based on interactive functions for plotting.
    Gets data array from file and plot if specified
    """

    def __init__(
        self,
        data,
        plot="slices",
        log=False,
        cmap="turbo",
        figsize=(10, 10),
        fontsize=15,
        title=None,
    ):
        """Either directly loads a data array from 'data_array' or extracts a
        data array from 'filename'. Plots the data according to the value of
        'plot'.

        :param filename: path to data, supported files extensions are .cxi,
         .npy or .npz
        :param data_array: a np.ndarray
        :param plot: str in [
            '2D', 'slices', 'contour_slices',
            'sum_slices', 'sum_contour_slices',
            '3D', False,
         ]
        :param log: True to have a logarithmic scale
         False to have a linear scale
        :param cmap: matplotlib cmap used for plot, default 'YlGnBu_r'
         Other possible values are 'Cool', 'Gray', 'Gray_r', 'Hot', 'Hsv',
         'Inferno', 'Jet', 'Plasma', 'Rainbow', 'Viridis'
        :param figsize: default (10, 10)
        :param fontsize: default 15
        """
        self.filename = None
        self.data_array = None
        self.plot = plot
        self.log = log
        self.cmap = cmap
        self.figsize = figsize
        self.fontsize = fontsize
        self.title = title

        # Future attributes
        self.interact_scale = False

        # Get data array from any of the supported files
        if os.path.isfile(data):
            self.filename = data
            self.get_data_array()

        elif isinstance(data, np.ndarray):
            self.data_array = data
            self.init_plot()

        else:
            print(
                "Please provide either a valid filename (arg filename)"
                " or directly an np.ndarray (arg data_array)."
            )

    def init_plot(self):
        if self.plot == "2D":
            plot_data(
                data_array=self.data_array,
                figsize=self.figsize, fontsize=self.fontsize,
                log=self.log, cmap=self.cmap, title=self.title,
            )

        elif self.plot == "slices" and self.data_array.ndim == 3:
            plot_3d_slices(
                data_array=self.data_array,
                fontsize=self.fontsize, title=self.title,
                figsize=None, log=self.log, cmap=self.cmap,
                contour=False, sum_over_axis=False,
            )

        elif self.plot == "contour_slices" and self.data_array.ndim == 3:
            plot_3d_slices(
                data_array=self.data_array,
                fontsize=self.fontsize, title=self.title,
                figsize=None, log=self.log, cmap=self.cmap,
                contour=True, sum_over_axis=False,
            )

        elif self.plot == "sum_slices" and self.data_array.ndim == 3:
            plot_3d_slices(
                data_array=self.data_array,
                fontsize=self.fontsize, title=self.title,
                figsize=None, log=self.log, cmap=self.cmap,
                contour=False, sum_over_axis=True,
            )

        elif self.plot == "sum_contour_slices" and self.data_array.ndim == 3:
            plot_3d_slices(
                data_array=self.data_array,
                fontsize=self.fontsize, title=self.title,
                figsize=None, log=self.log, cmap=self.cmap,
                contour=True, sum_over_axis=True,
            )

        elif self.plot == "3D" and self.data_array.ndim == 3:
            ThreeDViewer(self.data_array)

        else:
            print(
                "#########################################################"
                "########################################################\n"
                f"Loaded data array\n"
                f"\tNb of dimensions: {self.data_array.ndim}\n"
                f"\tShape: {self.data_array.shape}\n"
                "\n#########################################################"
                "########################################################"
            )

    def get_data_array(self):
        """Get numpy array from file.

        :param plot: either '2D', 'slices', '3D' or False
        """
        # No need to select data array interactively
        if self.filename.endswith((".npy", ".h5", ".cxi")):
            if self.filename.endswith(".npy"):
                try:
                    self.data_array = np.load(self.filename)

                except ValueError:
                    print("Could not load data ... ")

            elif self.filename.endswith(".cxi"):
                try:
                    self.data_array = h5.File(self.filename, mode='r')[
                        'entry_1/data_1/data'][()]

                except (KeyError, OSError):
                    print("""
                        The file could not be loaded, verify that you are
                        loading a file with an hdf5 architecture (.nxs, .cxi,
                        .h5, ...) and that the file exists. Otherwise, verify
                        that the data is saved in f.root.entry_1.data_1.data[:],
                        as it should be following cxi conventions.
                        """)

            elif self.filename.endswith(".h5"):
                try:
                    self.data_array = h5.File(self.filename, mode='r')[
                        'entry_1/data_1/data'][()]
                    if self.data_array.ndim == 4:
                        self.data_array = self.data_array[0]
                    # Due to labelling of axes x,y,z and not z,y,x
                    self.data_array = np.swapaxes(self.data_array, 0, 2)

                except (KeyError, OSError):
                    try:
                        self.data_array = h5.File(self.filename, mode='r')[
                            'entry_1/image_1/data'][()]
                        if self.data_array.ndim == 4:
                            self.data_array = self.data_array[0]
                        # Due to labelling of axes x,y,z and not z,y,x
                        self.data_array = np.swapaxes(self.data_array, 0, 2)
                    except (KeyError, OSError):
                        raise KeyError("""
                            The file could not be loaded, verify that you are\
                            loading a file with an hdf5 architecture (.nxs, .cxi,\
                            .h5, ...) and that the file exists. Otherwise, verify\
                            that the data is saved in f.root.entry_1.data_1.data[:],\
                            as it should be following cxi conventions.\
                            """)

            # Plot data
            self.init_plot()

        # Need to select data array interactively
        elif self.filename.endswith(".npz"):
            # Open npz file and allow the user to pick an array
            try:
                rawdata = np.load(self.filename)

                @interact(
                    file=widgets.Dropdown(
                        options=rawdata.files,
                        value=rawdata.files[0],
                        description='Pick an array to load:',
                        style={'description_width': 'initial'}))
                def open_npz(file):
                    # Pick an array
                    try:
                        self.data_array = rawdata[file]
                    except ValueError:
                        print("Key not valid, is this an array ?")

                    # Plot data
                    self.init_plot()

            except ValueError:
                print("Could not load data.")

        else:
            print("Data type not supported.")


class ThreeDViewer(widgets.Box):
    """
    Widget to display 3D objects from CDI optimisation, loaded from a result
    CXI file or a mode file.

    Simplified from the widgets class in PyNX @Vincent Favre Nicolin (ESRF)
    """

    def __init__(self, input_file=None, html_width=None):
        """
        Initialize the output and widgets

        :param input_file: the data filename or directly the 3D data array.
        :param html_width: html width in %. If given, the width of the
         notebook will be changed to that value (e.g. full width with 100)
        """
        super(ThreeDViewer, self).__init__()

        if html_width is not None:
            display(
                HTML("<style>.container { width:%d%% !important; }\
                    </style>" % int(html_width)
                     )
            )

        # focus_label = widgets.Label(value='Focal distance (cm):')
        self.threshold = widgets.FloatSlider(
            value=5,
            min=0,
            max=20,
            step=0.02,
            description='Contour.',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='.01f',
        )
        self.toggle_phase = widgets.ToggleButtons(
            options=['Abs', 'Phase'],
            description='',
            disabled=False,
            value='Phase',
            button_style='',
        )
        self.toggle_rotate = widgets.ToggleButton(
            value=False,
            description='Rotate',
            tooltips='Rotate',
        )
        self.pcb_rotate = None
        hbox1 = widgets.HBox([self.toggle_phase, self.toggle_rotate])

        self.toggle_dark = widgets.ToggleButton(
            value=False,
            description='Dark',
            tooltips='Dark/Light theme',
        )
        self.toggle_box = widgets.ToggleButton(
            value=True,
            description='Box',
            tooltips='Box ?',
        )
        self.toggle_axes = widgets.ToggleButton(
            value=True,
            description='Axes',
            tooltips='Axes ?',
        )
        hbox_toggle = widgets.HBox(
            [self.toggle_dark, self.toggle_box, self.toggle_axes])

        # Colormap widgets
        self.colormap = widgets.Dropdown(
            options=['Cool', 'Gray', 'Gray_r', 'Hot', 'Hsv',
                     'Inferno', 'Jet', 'Plasma', 'Rainbow', 'Viridis'],
            value='Jet',
            description='Colors:',
            disabled=True,
        )
        self.colormap_range = widgets.FloatRangeSlider(
            value=[20, 80],
            min=0,
            max=100,
            step=1,
            description='Range:',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True
        )

        # Progress bar
        self.progress = widgets.IntProgress(
            value=10,
            min=0,
            max=10,
            description='Processing:',
            bar_style='',
            style={'bar_color': 'green'},
            orientation='horizontal'
        )

        # Set observers
        self.threshold.observe(self.on_update_plot)
        self.toggle_phase.observe(self.on_change_scale)
        self.colormap.observe(self.on_update_plot)
        self.colormap_range.observe(self.on_update_plot)

        self.toggle_dark.observe(self.on_update_style)
        self.toggle_box.observe(self.on_update_style)
        self.toggle_axes.observe(self.on_update_style)

        self.toggle_rotate.observe(self.on_animate)

        # Future attributes
        # self.mesh = None
        # self.color = None
        # self.d0 = None
        # self.progress.value = None

        # Create final vertical box with all the widgets
        self.vbox = widgets.VBox([self.threshold,
                                  hbox1, hbox_toggle,
                                  self.colormap,
                                  # self.colormap_range, # useless for one contour
                                  self.progress,
                                  ])

        # Load data
        if isinstance(input_file, np.ndarray):
            # We create an output for ipyvolume
            self.output_view = widgets.Output()
            with self.output_view:
                self.fig = ipv.figure()
                self.set_data(input_file)
                display(self.fig)

            self.window = widgets.HBox([self.output_view, self.vbox])

            display(self.window)

        else:
            print("Could not load data")

    def on_update_plot(self, change=None):
        """Update the plot according to parameters. The points are re-computed.

        :param change: used to update the values
        :return:
        """
        if change is not None and change['name'] != 'value':
            return
        self.progress.value = 7

        try:
            verts, faces, _, _ = marching_cubes(
                abs(self.d),
                level=self.threshold.value,
                step_size=1,
            )
            vals = self.rgi(verts)

            # Phase colouring
            if self.toggle_phase.value == "Phase":
                self.colormap.disabled = True
                rgba = complex2rgbalin(vals)
                color = rgba[..., :3] / 256

            # Linear or log colouring
            elif self.toggle_phase.value in ['Abs', 'log10(Abs)']:
                self.colormap.disabled = False
                cs = cm.ScalarMappable(
                    norm=Normalize(
                        vmin=self.colormap_range.value[0],
                        vmax=self.colormap_range.value[1]),
                    cmap=self.colormap.value.lower())
                color = cs.to_rgba(abs(vals))[..., :3]
            else:
                # TODO: Gradient
                gx, gy, gz = self.rgi_gx(verts), self.rgi_gy(
                    verts), self.rgi_gz(verts)
                color = np.empty((len(vals), 3), dtype=np.float32)
                color[:, 0] = abs(gx)
                color[:, 1] = abs(gy)
                color[:, 2] = abs(gz)
                color *= 100
                self.color = color
            x, y, z = verts.T
            self.mesh = ipv.plot_trisurf(x, y, z, triangles=faces, color=color)
            self.fig.meshes = [self.mesh]

        # Keep general exception for debugging purposes
        except Exception as E:
            print(E)

        # Update progress bar
        self.progress.value = 10

    def on_update_style(self, change):
        """
        Update the plot style - for all parameters which
        do not involved recomputing
        the displayed object.
        :param change: dict from widget
        :return:
        """
        if change['name'] == 'value':
            if self.toggle_dark.value:
                ipv.pylab.style.set_style_dark()
            else:
                ipv.pylab.style.set_style_light()
                # Fix label colours (see self.fig.style)
                ipv.pylab.style.use(
                    {'axes': {'label': {'color': 'black'},
                              'ticklabel': {'color': 'black'}}})
            if self.toggle_box.value:
                ipv.pylab.style.box_on()
            else:
                ipv.pylab.style.box_off()
            if self.toggle_axes.value:
                ipv.pylab.style.axes_on()
            else:
                ipv.pylab.style.axes_off()

    def on_change_scale(self, change):
        """Change scale between logarithmic and linear"""
        if change['name'] == 'value':
            if isinstance(change['old'], str):
                newv = change['new']
                oldv = change['old']

                # linear scale
                if 'log' in oldv and 'log' not in newv:
                    d = self.d0
                    self.set_data(d, threshold=10 ** self.threshold.value)

                # log scale
                elif 'log' in newv and 'log' not in oldv:
                    self.d0 = self.d
                    d = np.log10(np.maximum(0.1, abs(self.d0)))
                    self.set_data(d, threshold=np.log10(self.threshold.value))
                    return
            self.on_update_plot()

    def set_data(self, d, threshold=None):
        """Check if data is complex or not

        :param d: data 3d array, complex ot not, to be plotted
        :param threshold: threshold for contour, if None set to max/2
        """

        # Update progress bar
        self.progress.value = 5

        # Save data
        self.d = d

        # Change scale options depending on data
        self.toggle_phase.unobserve(self.on_change_scale)

        if np.iscomplexobj(d):
            if self.toggle_phase.value == 'log10(Abs)':
                self.toggle_phase.value = 'Abs'
            self.toggle_phase.options = ('Abs', 'Phase')
        else:
            if self.toggle_phase.value == 'Phase':
                self.toggle_phase.value = 'Abs'
            self.toggle_phase.options = ('Abs', 'log10(Abs)')
        self.toggle_phase.observe(self.on_change_scale)

        # Set threshold
        self.threshold.unobserve(self.on_update_plot)
        self.colormap_range.unobserve(self.on_update_plot)
        self.threshold.max = abs(self.d).max()
        if threshold is None:
            self.threshold.value = self.threshold.max / 2
        else:
            self.threshold.value = threshold

        # Set colormap
        self.colormap_range.max = abs(self.d).max()
        self.colormap_range.value = [0, abs(self.d).max()]
        self.threshold.observe(self.on_update_plot)
        self.colormap_range.observe(self.on_update_plot)

        nz, ny, nx = self.d.shape
        z, y, x = np.arange(nz), np.arange(ny), np.arange(nx)

        # Interpolate probe to object grid
        self.rgi = RegularGridInterpolator(
            (z, y, x),
            self.d,
            method='linear',
            bounds_error=False,
            fill_value=0,
        )

        # Also prepare the phase gradient
        gz, gy, gx = np.gradient(self.d)
        a = np.maximum(abs(self.d), 1e-6)
        ph = self.d / a
        gaz, gay, gax = np.gradient(a)
        self.rgi_gx = RegularGridInterpolator(
            (z, y, x), ((gx - gax * ph) / (ph * a)).real,
            method='linear', bounds_error=False, fill_value=0)
        self.rgi_gy = RegularGridInterpolator(
            (z, y, x), ((gy - gay * ph) / (ph * a)).real,
            method='linear', bounds_error=False, fill_value=0)
        self.rgi_gz = RegularGridInterpolator(
            (z, y, x), ((gz - gaz * ph) / (ph * a)).real,
            method='linear', bounds_error=False, fill_value=0)

        # Fix extent otherwise weird things happen
        ipv.pylab.xlim(0, self.d.shape[0])
        ipv.pylab.ylim(0, self.d.shape[1])
        ipv.pylab.zlim(0, self.d.shape[2])
        ipv.squarelim()
        self.on_update_plot()

    def on_animate(self, v):
        """Trigger the animation (rotation around vertical axis)
        """
        if self.pcb_rotate is None:
            self.pcb_rotate = PeriodicCallback(self.callback_rotate, 50.)
        if self.toggle_rotate.value:
            self.pcb_rotate.start()
        else:
            self.pcb_rotate.stop()

    def callback_rotate(self):
        """Used for periodic rotation."""
        # ipv.view() only supports a rotation against
        # the starting azimuth and elevation
        # ipv.view(azimuth=ipv.view()[0]+1)

        # Use a quaternion and the camera's 'up' as rotation axis
        x, y, z = self.fig.camera.up
        n = np.sqrt(x ** 2 + y ** 2 + z ** 2)
        a = np.deg2rad(2.5) / 2  # angular step
        sa, ca = np.sin(a / 2) / n, np.cos(a / 2)
        r = Rotation.from_quat((sa * x, sa * y, sa * z, ca))
        self.fig.camera.position = tuple(r.apply(self.fig.camera.position))


# Methods

def plot_data(
    data_array,
    figsize=(10, 10),
    fontsize=15,
    log="interact",
    cmap="turbo",
    title=None,
):
    """
    Create figure based on the data dimensions.
    Data in 1D is plotted as a curve
    Data in 2D is plotted as a 2D image
    Data in 3D is plotted with Bokeh along one axis

    :param data_array: np.ndarray to plot
    :param figsize: default (10, 10)
    :param fontsize: default 15
    :param log: True, False or "interact"
    :param cmap: matplotlib cmap used for plot, default 'YlGnBu_r'
    :param title: title for plot, string or list of 3 strings if 3d data
    """
    # Get dimensions
    data_dimensions = data_array.ndim

    if data_dimensions == 1:
        plt.close()
        fig, ax = plt.subplots(figsize=figsize)

        # Depends on log scale
        if log:
            ax.plot(np.log(data_array))
            plt.title(title, fontsize=fontsize+2)
            plt.tight_layout()
            plt.show()

        elif log is False:
            ax.plot(data_array)
            plt.title(title, fontsize=fontsize+2)
            plt.tight_layout()
            plt.show()

        elif log == "interact":
            @interact(
                scale=widgets.ToggleButtons(
                    options=["linear", "logarithmic"],
                    value="linear",
                    description='Scale',
                    disabled=False,
                    style={'description_width': 'initial'}),
            )
            def plot_with_interactive_scale(scale, figsize):
                # Create figure
                if not figsize:
                    figsize = (7, 7)

                _, ax = plt.subplots(figsize=figsize)

                # Get scale
                log = scale == "logarithmic"

                if log:
                    ax.plot(np.log(data_array))
                else:
                    ax.plot(data_array)

                plt.title(title, fontsize=fontsize+2)
                plt.tight_layout()
                plt.show()

    elif data_dimensions == 2:
        # Depends on log scale
        if isinstance(log, bool):
            img = plot_2d_image(
                data_array, log=log, cmap=cmap, title=title, fontsize=fontsize
            )

            # Create axis for colorbar
            cbar_ax = make_axes_locatable(ax).append_axes(
                position='right', size='5%', pad=0.1)

            # Create colorbar
            fig.colorbar(mappable=img, cax=cbar_ax)

            # Show figure
            plt.tight_layout()
            plt.show()

        elif log == "interact":
            @interact(
                scale=widgets.ToggleButtons(
                    options=["linear", "logarithmic"],
                    value="linear",
                    description='Scale',
                    disabled=False,
                    style={'description_width': 'initial'}),
                figsize=fixed(figsize)
            )
            def plot_with_interactive_scale(scale, figsize):
                # Create figure
                if not figsize:
                    figsize = (10, 10)

                fig, ax = plt.subplots(figsize=figsize)

                # Get scale
                log = scale == "logarithmic"

                # Plot
                img = plot_2d_image(
                    data_array, log=log, fig=fig, ax=ax, cmap=cmap
                )

                # Create axis for colorbar
                cbar_ax = make_axes_locatable(ax).append_axes(
                    position='right', size='5%', pad=0.1)

                # Create colorbar
                fig.colorbar(mappable=img, cax=cbar_ax)

                # Show figure
                plt.tight_layout()
                plt.show()

    elif data_dimensions == 3:

        # Define function used to get data slice
        def get_data_slice(
            data,
            axis="x",
            index=0,
            data_type="Module",
            scale="linear",
        ):
            """
            Function used when using widgets with callbacks on the 3D image

            :param data: 3D data array
            :param axis: axis on which the data is projected in ("x", "y", "z")
            :param index: index along param axis
            :param data_type: plot module, phase, real or imaginary part of
                the data
            :param scale: "logarithmic" for log scale, otherwise linear scale
            """
            # Project on specific index
            if axis == "x":
                dt = data[index, :, :]
            elif axis == "y":
                dt = data[:, index, :]
            elif axis == "z":
                dt = data[:, :, index]

            # Data type
            if data_type == "Real":
                dt = np.real(dt)
            elif data_type == "Imaginary":
                dt = np.imag(dt)
            elif data_type == "Module":
                dt = np.abs(dt)
            elif data_type == "Phase":
                dt = np.angle(dt)

            # Scale
            if scale == "logarithmic":
                dt = np.where(dt > 0, np.log(dt), 0)

            lin_color_mapper.high = np.max(dt)

            return dt

        output_notebook()

        # Get bokeh palette from colormap
        TOOLTIPS = [
            ("x", "$x"),
            ("y", "$y"),
            ("value", "@data"),
        ]

        # List of compatible cmaps in bokeh
        bokey_cmaps = [
            p for p in bp.__palettes__ if p.endswith("256")
        ]

        palette = "Magma256"
        for p in bokey_cmaps:
            if cmap[1:] in p:  # skip capital letter
                palette = p
                print("Changing cmap to", palette)

        # Figure
        fig = figure(
            x_axis_label="x",
            y_axis_label="y",
            toolbar_location="above",
            toolbar_sticky=False,
            tools="pan, wheel_zoom, box_zoom, reset, undo, redo, crosshair, hover, save",
            active_scroll="wheel_zoom",
            active_tap="auto",
            active_drag="box_zoom",
            active_inspect="auto",
            tooltips=TOOLTIPS
        )

        # Define source
        source = ColumnDataSource(
            data=dict(
                data=[np.abs(data_array[0, :, :])],
                dw=[data_array.shape[1]],
                dh=[data_array.shape[2]],
                index=[0],
                axis=["x"],
                data_type=["Module"],
                scale=["linear"],
            )
        )

        # Index
        def callback_change_index(attr, old, new):
            # Compute data
            dt = get_data_slice(
                data=data_array,
                axis=source.data["axis"][0],
                index=new,
                data_type=source.data["data_type"][0],
                scale=source.data["scale"][0],
            )

            # Save new values
            source.data["data"] = [dt]
            source.data["index"] = [new]

        slider_index = Slider(
            start=0,
            end=data_array.shape[0]-1,
            value=0,
            step=1,
            title="Position",
            orientation="horizontal",
        )
        slider_index.on_change('value', callback_change_index)

        # Axis
        def callback_change_axis(attr, old, new):
            # Get axis for projection
            new_axis = ["x", "y", "z"][new]

            # Compute data
            dt = get_data_slice(
                data=data_array,
                axis=new_axis,
                index=source.data["index"][0],
                data_type=source.data["data_type"][0],
                scale=source.data["scale"][0],
            )

            # Save new values
            source.data["data"] = [dt]
            source.data["axis"] = [new_axis]
            source.data["dw"][0] = dt.shape[0]
            source.data["dh"][0] = dt.shape[1]

            # Get new axis names and slider range
            if new_axis == "x":
                slider_range = data_array.shape[0]
                fig.axis[0].axis_label = "y"
                fig.axis[1].axis_label = "z"

            elif new_axis == "y":
                slider_range = data_array.shape[1]
                fig.axis[0].axis_label = "x"
                fig.axis[1].axis_label = "z"

            elif new_axis == "z":
                slider_range = data_array.shape[2]
                fig.axis[0].axis_label = "x"
                fig.axis[1].axis_label = "y"

            # Change slider range
            slider_index.end = slider_range-1

        select_axis = RadioButtonGroup(
            labels=["x", "y", "z"],
            active=0,
        )
        select_axis.on_change('active', callback_change_axis)

        # Data type
        def callback_change_data_type(attr, old, new):
            # Get data type
            new_data_type = ["Real", "Imaginary", "Module", "Phase"][new]

            # Compute data
            dt = get_data_slice(
                data=data_array,
                axis=source.data["axis"][0],
                index=source.data["index"][0],
                data_type=new_data_type,
                scale=source.data["scale"][0],
            )

            # Save new values
            source.data["data"] = [dt]
            source.data["data_type"] = [new_data_type]

        select_data_type = RadioButtonGroup(
            labels=["Real", "Imaginary", "Module", "Phase"],
            active=2,
        )
        select_data_type.on_change('active', callback_change_data_type)

        # Color bar
        def callback_change_cbar(attr, old, new):
            # Get new cbar
            new_cbar = ["linear", "logarithmic"][new]

            # Compute data
            dt = get_data_slice(
                data=data_array,
                axis=source.data["axis"][0],
                index=source.data["index"][0],
                data_type=source.data["data_type"],
                scale=new_cbar,
            )

            # Save new values
            source.data["data"] = [dt]
            source.data["scale"] = [new_cbar]

        select_cbar = RadioButtonGroup(
            labels=["linear", "logarithmic"],
            active=0,
        )
        select_cbar.on_change('active', callback_change_cbar)

        # Background
        fig.background_fill_color = "white"
        fig.background_fill_alpha = 0.5

        # Title
        fig.title.text_font = "futura"
        fig.title.text_font_style = "bold"
        fig.title.text_font_size = "15px"

        # Color bars
        lin_color_mapper = LinearColorMapper(
            palette=palette,
            low=0,
            high=np.max(source.data["data"][0]),
        )
        lin_color_bar = ColorBar(color_mapper=lin_color_mapper)

        fig.add_layout(lin_color_bar, 'right')

        # Image
        fig.image(
            image="data",
            source=source,
            x=0,
            y=0,
            dw="dw",
            dh="dh",
            color_mapper=lin_color_mapper,
        )

        # Create app layout
        app = pn.Column(
            pn.pane.Bokeh(
                row(
                    select_axis,
                    select_cbar,
                )
            ),
            pn.pane.Bokeh(
                row(select_data_type)
            ),
            pn.pane.Bokeh(
                row(
                    fig,
                    slider_index,
                )
            )
        )

        display(app)


def plot_2d_image(
    two_d_array,
    fontsize=15,
    fig=None,
    ax=None,
    log=False,
    cmap="turbo",
    title=None,
    x_label="x",
    y_label="y",
    contour=False,
):
    """
    Plot 2d image from 2d array.

    :param two_d_array: np.ndarray to plot, must be 2D
    :param fontsize: default to 15
    :param fig: plt.figure to plot in, default is None and
     will create a figure, used to add 2d images to 3d figures
    :param ax: axes of figure, default is None and will create axes
    :param log: True to have a logarithmic scale, False to have a linear scale
    :param cmap: matplotlib cmap used for plot, default 'turbo'
    :param title: str, title for this axe
    :param x_label: label on x axis
    :param y_label: label on y axis
    :param contour: True to plot contour of data

    :return: image on ax : ax.imshow()
    """
    if not fig and not ax:
        fig, ax = plt.subplots(1, 1, figsize=(5, 5))

    scale = "logarithmic" if log else "linear"

    try:
        if np.iscomplex(two_d_array).any():
            print(
                "Using complex data, switching to array module for plot."
            )
            two_d_array = np.abs(two_d_array)
        if contour:
            img = ax.contourf(
                two_d_array,
                norm={"linear": None, "logarithmic": LogNorm()}[
                    scale],
                cmap=cmap,
            )
        else:
            img = ax.imshow(
                two_d_array,
                norm={"linear": None, "logarithmic": LogNorm()}[
                    scale],
                cmap=cmap,
            )
        ax.set_xlabel(x_label, fontsize=fontsize)
        ax.set_ylabel(y_label, fontsize=fontsize)
        if isinstance(title, str):
            ax.set_title(title, fontsize=fontsize + 2)

        return img

    except ValueError:
        plt.close()
        if scale == "logarithmic":
            print("Log scale can not handle this kind of data ...")
        else:
            pass
        return None


def plot_3d_slices(
    data_array,
    fontsize=15,
    figsize=None,
    log=False,
    cmap="turbo",
    title=None,
    contour=False,
    sum_over_axis=False,
):
    """
    Plot 3 slices for 3d data.

    :param data_array: np.ndarray to plot, must be 3D
    :param fontsize: default 15
    :param figsize: default (10, 10)
    :param log: boolean (True, False) or, otherwise
     raises an interactive window
    :param cmap: matplotlib cmap used for plot, default 'YlGnBu_r'
    :param title: string to set as title for main plot or list of
     strings of length 3 for sub axes
    :param contour: True to plot contour of data
    :param sum_over_axis: True to plot sum intead of slices
    """
    if isinstance(log, bool):
        # Create figure
        if not figsize:
            figsize = (15, 7)

        fig, axs = plt.subplots(1, 3, figsize=figsize)

        # Add titles
        if isinstance(title, str):
            fig.suptitle(title, fontsize=fontsize + 2, y=0.95)
            titles = [None, None, None]
        elif isinstance(title, tuple) and len(title) == 3\
                or isinstance(title, list) and len(title) == 3:
            titles = title
        else:
            titles = [None, None, None]

        # 3D array shape
        shape = data_array.shape

        # Plot first image
        if sum_over_axis:  # Compute sum
            two_d_array = np.sum(np.nan_to_num(data_array), axis=(0))

        else:  # Get middle slice
            two_d_array = data_array[shape[0]//2, :, :]
        img_x = plot_2d_image(
            two_d_array, fig=fig, title=titles[0], ax=axs[0], log=log,
            cmap=cmap, fontsize=fontsize, x_label="z", y_label="y",
            contour=contour
        )

        # Create axis for colorbar
        cbar_ax = make_axes_locatable(axs[0]).append_axes(
            position='right', size='5%', pad=0.1)

        # Create colorbar
        fig.colorbar(mappable=img_x, cax=cbar_ax)

        # Plot second image
        if sum_over_axis:  # Compute sum
            two_d_array = np.sum(np.nan_to_num(data_array), axis=(1))

        else:  # Get middle slice
            two_d_array = data_array[:, shape[1]//2, :]
        img_y = plot_2d_image(
            two_d_array, fig=fig, title=titles[1], ax=axs[1], log=log,
            cmap=cmap, fontsize=fontsize, x_label="z", y_label="x",
            contour=contour
        )

        # Create axis for colorbar
        cbar_ax = make_axes_locatable(axs[1]).append_axes(
            position='right', size='5%', pad=0.1)

        # Create colorbar
        fig.colorbar(mappable=img_y, cax=cbar_ax)

        # Plot third image
        if sum_over_axis:  # Compute sum
            two_d_array = np.sum(np.nan_to_num(data_array), axis=(2))

        else:  # Get middle slice
            two_d_array = data_array[:, :, shape[2]//2]
        img_z = plot_2d_image(
            two_d_array, fig=fig, title=titles[2], ax=axs[2], log=log,
            cmap=cmap, fontsize=fontsize, x_label="y", y_label="x",
            contour=contour
        )

        # Create axis for colorbar
        cbar_ax = make_axes_locatable(axs[2]).append_axes(
            position='right', size='5%', pad=0.1)

        # Create colorbar
        fig.colorbar(mappable=img_z, cax=cbar_ax)

        # Show figure
        fig.tight_layout()
        fig.show()

    else:
        @interact(
            scale=widgets.ToggleButtons(
                options=[
                    ("linear", False),
                    ("logarithmic", True),
                ],
                value=False,
                description='Scale',
                disabled=False,
                style={'description_width': 'initial'}),
            figsize=fixed(figsize)
        )
        def plot_with_interactive_scale(scale, figsize):
            try:
                plot_3d_slices(
                    data_array=data_array,
                    fontsize=fontsize,
                    figsize=figsize,
                    log=scale,
                    cmap=cmap,
                    title=title,
                    contour=contour,
                    sum_over_axis=sum_over_axis,
                )
            except IndexError:
                plt.close()
                print("Is this a 3D array?")


def complex2rgbalin(
    s,
    gamma=1.0,
    smax=None,
    smin=None,
    percentile=(None, None),
    alpha=(0, 1),
    final_type='uint8'
):
    """
    Returns RGB image with with colour-coded phase and linear amplitude
    in brightness. Optional exponent gamma is applied to the amplitude.
    Taken from PyNX

    :param s: the complex data array (likely 2D, but can have higher
     dimensions)
    :param gamma: gamma parameter to change the brightness curve
    :param smax: maximum value (brightness = 1). If not supplied and
     percentile is not set, the maximum amplitude of the array is used.
    :param smin: minimum value(brightness = 0). If not supplied and
     percentile is not set, the maximum amplitude of the array is used.
    :param percentile: a tuple of two values (percent_min, percent_max)
     setting the percentile (between 0 and 100): the smax and smin values
     will be  set as the percentile value in the array (see numpy.percentile).
     These two values (when not None) supersede smax and smin.
     Example: percentile=(0,99) to scale the brightness to 0-1 between the 1%
     and 99% percentile of the data amplitude.
    :param alpha: the minimum and maximum value for the alpha channel,
     normally (0,1). Useful to have different max/min alpha when going
     through slices of one object
    final_type: either 'float': values are in the [0..1] range,
     or 'uint8' (0..255) (new default)
    Returns:
     the RGBA array, with the same diemensions as the input array,
     plus one additional R/G/B/A dimension appended.
    """
    rgba = phase2rgb(s)
    a = np.abs(s)
    if percentile is not None:
        if percentile[0] is not None:
            smin = np.percentile(a, percentile[0])
        if percentile[1] is not None:
            smax = np.percentile(a, percentile[1])
        if smax is not None and smin is not None and smin > smax:
            smin, smax = smax, smin
    if smax is not None:
        a = (a - smax) * (a <= smax) + smax
    if smin is not None:
        a = (a - smin) * (a >= smin)
    a /= a.max()
    a = a ** gamma
    rgba[..., 3] = alpha[0] + alpha[1] * a
    if final_type == 'float':
        return rgba
    return (rgba * 255).astype(np.uint8)


def phase2rgb(s):
    """
    Crates RGB image with colour-coded phase from a complex array.
    Taken from PyNX

    :param s: a complex numpy array

    Returns: an RGBA numpy array, with one additional dimension added
    """
    ph = np.angle(s)
    t = np.pi / 3
    rgba = np.zeros(list(s.shape) + [4])
    rgba[..., 0] = (ph < t) * (ph > -t) + (ph > t) * (ph < 2 * t) * \
        (2 * t - ph) / t + (ph > -2 * t) * (ph < -t) * (
        ph + 2 * t) / t
    rgba[..., 1] = (ph > t) + (ph < -2 * t) * (-2 * t - ph) / \
        t + (ph > 0) * (ph < t) * ph / t
    rgba[..., 2] = (ph < -t) + (ph > -t) * (ph < 0) * (-ph) / \
        t + (ph > 2 * t) * (ph - 2 * t) / t
    return rgba
