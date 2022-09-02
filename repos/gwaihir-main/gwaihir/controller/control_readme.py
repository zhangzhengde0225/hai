from IPython.display import display, Markdown, clear_output
from bcdi.postprocessing import facet_analysis
from gwaihir.controller import control_preprocess
from gwaihir.controller import control_phase_retrieval
from gwaihir.controller import control_postprocess
import ipywidgets as widgets


def init_readme_tab(contents):
    """
    Help text about different steps in data analysis workflow.

    :param contents: e.g. "Preprocessing"
     Possible values are "Preprocessing", "Phase retrieval", "Postprocessing"
     or "Facet analysis"
    """
    if contents == "Preprocessing":
        clear_output(True)
        print(help(control_preprocess.init_preprocess_tab))

    elif contents == "Phase retrieval":
        clear_output(True)
        print(help(control_phase_retrieval.init_phase_retrieval_tab))

    elif contents == "Postprocessing":
        clear_output(True)
        print(help(control_postprocess.init_postprocess_tab))

    elif contents == "Facet analysis":
        clear_output(True)
        print(help(facet_analysis.Facets))
        print("""
            The output DataFrame can be opened in the `Logs` tab.
            The "View particle" tool helps you visualizing the particle
            facets.
            """)

    elif contents == "GUI":
        display(Markdown("# Welcome to `Gwaihir`"))
        display(Markdown("Remember that a detailed tutorial on the installation of each package is "
                         " available on the [Github](https://github.com/DSimonne/gwaihir#welcome),"
                         " together with a video that presents the data analysis workflow."
                         ))
        display(Markdown("On the other tabs of this README are presented the main functions used for"
                         " data analysis and their parameters."))
        display(Markdown(""))

        display(Markdown("# Example of parameter values"))
        display(Markdown("## SixS data (SOLEIL)"))
        display(Markdown(
            "Most of the initial guesses are valid. Be careful about the energy, scan number, central pixel and detector."
            " If you are working with the vertical configuration, make sure that the mask is correct."))

        display(Markdown("## ID01 data (ESRF)"))
        display(Markdown("* Scan number: `11`"))
        display(Markdown(
            "* Data directory: `/data/id01/inhouse/david/UM2022/ID01/CXIDB-I182/CH4760/`"))
        display(Markdown("* Detector: `Maxipix`"))
        display(Markdown("* Template imagefile: `S11/data_mpx4_%05d.edf.gz`"))
        display(Markdown("* Sample offsets: `(90, 0, 0)`"))
        display(Markdown("* Sample detector distance (m): `0.50678`"))
        display(Markdown("* X-ray energy (eV): `9000`"))
        display(Markdown("* Beamline: `ID01`"))
        display(Markdown(
            "* specfile name: `/data/id01/inhouse/david/UM2022/ID01/CXIDB-I182/CH4760/l5.spec` (in my case, please use a direct path)"))
        display(Markdown("* Rocking angle: `outofplane`"))

        display(Markdown("## P10 data (PETRA)"))
        display(Markdown("* Sample name: `align_03`"))
        display(Markdown("* Scan number: `11`"))
        display(
            Markdown("* Data directory: `/data/id01/inhouse/david/UM2022/Petra/raw/`"))
        display(Markdown("* Detector: `Eiger4M`"))
        display(Markdown("* Template imagefile: `_master.h5`"))
        display(Markdown("* Sample offsets: `(0, 0, 0, 0)`"))
        display(Markdown("* Sample detector distance (m): `1.818`"))
        display(Markdown("* X-ray energy (eV): `11294`"))
        display(Markdown("* Beamline: `P10`"))
        display(
            Markdown("* specfile name: `/` (in my case, please use a direct path)"))
        display(Markdown("* Rocking angle: `inplane`"))
        display(Markdown("* Pixel size (in phase retrieval): `75`"))

        display(Markdown("# To go further ..."))
        display(Markdown("* All the plotting functions are accessible in `gwaihir.plot`, try to use the `Plotter` Class"
                         " that reads all kind of numpy arrays."
                         " e.g. `Plotter(filename=\"TestGui/S11/preprocessing/S11_maskpynx_align-q-y_norm_252_420_392_1_1_1.npz\", plot=\"2D\")`"
                         ))
        display(Markdown("* I highly recommend the use of [Paraview](https://www.paraview.org/) for 3D contouring."
                         " Many tutorials can be found online: <https://www.bu.edu/tech/support/research/training-consulting/online-tutorials/paraview/>"))
        display(Markdown(
            "* If you saved your data in the cxi format, you can visualize it with JupyterLab !"))
        display(Markdown("* `Qt5Agg` is a backend that does not work on remote servers, if you install `Gwaihir` on"
                         " your local computer, you can use this backend for masking. "
                         " We are currently working on implementing a solution in Jupyter Notebook with Bokeh."))
        display(Markdown("* If you saved your data in the `.cxi` format, you can visualize it with JupyterLab !"
                         " Otherwise you can use [`silx`](http://www.silx.org/doc/silx/0.7.0/applications/view.html) from the terminal"))
        display(
            Markdown("Link to the [`cxi` databank](https://cxidb.org/deposit.html)"))

        display(Markdown(
            "## Type the following code to stop the scrolling in the output cell, then reload the cell."))
        display(Markdown("`%%javascript`"))
        display(
            Markdown("`IPython.OutputArea.prototype._should_scroll = function(lines) {`"))
        display(Markdown("`return false;`"))
        display(Markdown("`}`"))

        display(Markdown("To contact me <david.simonne@synchrotron-soleil.fr>"))
