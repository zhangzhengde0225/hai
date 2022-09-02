import pandas as pd
from IPython.display import display, clear_output
import ipywidgets as widgets
from ipywidgets import interact


def init_data_frame_tab(
    interface,
    unused_label_logs,
    parent_folder,
    csv_file,
    show_logs
):
    """
    Loads exterior .csv file and displays it in the GUI.

    :param parent_folder: all .csv files in the parent_folder subsirectories
     will be shown in the dropdown list.
    :param csv_file: path to csv file
    :param show_logs: True to display dataframe
    """
    # Load data
    if show_logs in ("load_csv", "load_field_data"):
        interface.TabDataFrame.parent_folder.disabled = True
        try:
            # csv data
            if show_logs == "load_csv":
                try:
                    logs = pd.read_csv(csv_file)
                except ValueError:
                    print("Data type not supported.")

            # field data taken from facet analysis
            elif show_logs == "load_field_data":
                logs = interface.Facets.field_data.copy()

            @ interact(
                cols=widgets.SelectMultiple(
                    options=list(logs.columns),
                    value=list(logs.columns)[:],
                    rows=10,
                    style={'description_width': 'initial'},
                    layout=widgets.Layout(width='90%'),
                    description='Select multiple columns with \
                    Ctrl + click:',
                )
            )
            def pick_columns(cols):
                display(logs[list(cols)])

        except (FileNotFoundError, UnboundLocalError):
            print("Wrong path")
        except AttributeError:
            print(
                "You need to run the facet analysis in the dedicated tab first."
                "\nThen this function will load the resulting DataFrame."
            )

    else:
        interface.TabDataFrame.parent_folder.disabled = False
        interface.TabDataFrame.csv_file_handler(parent_folder)
        clear_output(True)
