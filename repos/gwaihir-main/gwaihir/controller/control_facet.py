import numpy as np
import pandas as pd
import os
from ast import literal_eval

from IPython.display import display, clear_output
import ipywidgets as widgets
from ipywidgets import interact

from bcdi.preprocessing import ReadNxs3 as rd
from bcdi.postprocessing import facet_analysis


def init_facet_tab(
    interface,
    unused_label_facet,
    parent_folder,
    vtk_file,
    load_data,
):
    """
    Allows one to:

        Load a vtk file (previously created in paraview via the FacetAnalyser
        plugin)
        Realign the particle by assigning a vector to 2 of its facets
        Extract information from each facet

    :param parent_folder: all .vtk files in the parent_folder subsirectories
     will be shown in the dropdown list.
    :param vtk_file: path to vtk file
    :param load_data: True to load vtk file dataframe
    """
    if load_data:
        # Disable text widget to avoid bugs
        interface.TabFacet.parent_folder.disabled = True
        try:
            interface.Dataset.facet_filename = vtk_file
        except AttributeError:
            pass

        try:
            interface.Dataset.Facets = facet_analysis.Facets(
                filename=os.path.basename(vtk_file),
                pathdir=vtk_file.replace(os.path.basename(vtk_file), ""))
            print(
                "Facets object saved as interface.Dataset.Facets. "
                "Use help(interface.Dataset.Facets) for more details."
            )

            # Button to rotate data
            button_rotate = widgets.Button(
                description="Work on facet data",
                continuous_update=False,
                button_style='',
                layout=widgets.Layout(width='40%'),
                style={'description_width': 'initial'},
                icon='fast-forward')

            # Button to view data
            button_view_particle = widgets.Button(
                description="View particle",
                continuous_update=False,
                button_style='',
                layout=widgets.Layout(width='40%'),
                style={'description_width': 'initial'},
                icon='fast-forward')

            # Common button as widget
            buttons_facets = widgets.HBox(
                [button_rotate, button_view_particle])

            @ button_rotate.on_click
            def action_button_rotate(selfbutton):
                clear_output(True)
                display(buttons_facets)

                # Run interactive function
                @ interact(
                    facet_a_id=widgets.Dropdown(
                        options=[
                            i + 1 for i in range(interface.Dataset.Facets.nb_facets)],
                        value=1,
                        description='Facet a id:',
                        continuous_update=True,
                        layout=widgets.Layout(width='45%'),
                        style={'description_width': 'initial'}),
                    facet_b_id=widgets.Dropdown(
                        options=[
                            i + 1 for i in range(interface.Dataset.Facets.nb_facets)],
                        value=2,
                        description='Facet b id:',
                        continuous_update=True,
                        layout=widgets.Layout(width='45%'),
                        style={'description_width': 'initial'}),
                    u0=widgets.Text(
                        value="[1, 1, 1]",
                        placeholder="[1, 1, 1]",
                        description='Vector perpendicular to facet a:',
                        continuous_update=False,
                        style={'description_width': 'initial'},),
                    v0=widgets.Text(
                        value="[1, -1, 0]",
                        placeholder="[1, -1, 0]",
                        description='Vector perpendicular to facet b:',
                        continuous_update=False,
                        style={'description_width': 'initial'},),
                    w0=widgets.Text(
                        value="[1, 1, -2]",
                        placeholder="[1, 1, -2]",
                        description='Cross product of u0 and v0:',
                        continuous_update=False,
                        style={'description_width': 'initial'},),
                    hkl_reference=widgets.Text(
                        value="[1, 1, 1]",
                        placeholder="[1, 1, 1]",
                        description='Reference for interplanar angles:',
                        continuous_update=False,
                        style={'description_width': 'initial'},),
                    elev=widgets.BoundedIntText(
                        value=90,
                        placeholder=90,
                        min=0,
                        max=360,
                        description='Elevation of the axes in degrees:',
                        continuous_update=False,
                        layout=widgets.Layout(width='70%'),
                        style={'description_width': 'initial'},),
                    azim=widgets.BoundedIntText(
                        value=0,
                        placeholder=0,
                        min=0,
                        max=360,
                        description='Azimuth of the axes in degrees:',
                        continuous_update=False,
                        layout=widgets.Layout(width='70%'),
                        style={'description_width': 'initial'},),
                )
                def fix_facets(
                    facet_a_id,
                    facet_b_id,
                    u0,
                    v0,
                    w0,
                    hkl_reference,
                    elev,
                    azim,
                ):
                    """
                    Function to interactively visualize the two facets that
                    will be chosen, to also help pick two vectors.
                    """
                    # Save parameters value
                    interface.Dataset.Facets.facet_a_id = facet_a_id
                    interface.Dataset.Facets.facet_b_id = facet_b_id
                    interface.Dataset.Facets.u0 = u0
                    interface.Dataset.Facets.v0 = v0
                    interface.Dataset.Facets.w0 = w0
                    interface.Dataset.Facets.hkl_reference = hkl_reference
                    interface.Dataset.Facets.elev = elev
                    interface.Dataset.Facets.azim = azim

                    # Extract list from strings
                    list_parameters = ["u0", "v0",
                                       "w0", "hkl_reference"]
                    try:
                        for p in list_parameters:
                            if getattr(interface.Dataset.Facets, p) == "":
                                setattr(interface.Dataset.Facets, p, [])
                            else:
                                setattr(interface.Dataset.Facets, p, literal_eval(
                                    getattr(interface.Dataset.Facets, p)))
                    except ValueError:
                        print(f"Wrong list syntax for {p}")

                    # Plot the chosen facet to help the user to pick the facets
                    # he wants to use to orient the particule
                    interface.Dataset.Facets.extract_facet(
                        facet_id=interface.Dataset.Facets.facet_a_id,
                        plot=True,
                        elev=interface.Dataset.Facets.elev,
                        azim=interface.Dataset.Facets.azim,
                        output=False,
                        save=False
                    )
                    interface.Dataset.Facets.extract_facet(
                        facet_id=interface.Dataset.Facets.facet_b_id,
                        plot=True,
                        elev=interface.Dataset.Facets.elev,
                        azim=interface.Dataset.Facets.azim,
                        output=False,
                        save=False
                    )

                    display(Markdown("""# Field data"""))
                    display(interface.Dataset.Facets.field_data)

                    button_fix_facets = widgets.Button(
                        description="Fix parameters and extract data.",
                        layout=widgets.Layout(width='50%', height='35px'))
                    display(button_fix_facets)

                    @ button_fix_facets.on_click
                    def action_button_fix_facets(selfbutton):
                        """
                        Fix facets to compute the new rotation matrix and
                        launch the data extraction.
                        """
                        clear_output(True)

                        display(button_fix_facets)

                        display(
                            Markdown("""# Computing the rotation matrix"""))

                        # Take those facets' vectors
                        u = np.array([
                            interface.Dataset.Facets.field_data.n0[interface.Dataset.Facets.facet_a_id],
                            interface.Dataset.Facets.field_data.n1[interface.Dataset.Facets.facet_a_id],
                            interface.Dataset.Facets.field_data.n2[interface.Dataset.Facets.facet_a_id]
                        ])
                        v = np.array([
                            interface.Dataset.Facets.field_data.n0[interface.Dataset.Facets.facet_b_id],
                            interface.Dataset.Facets.field_data.n1[interface.Dataset.Facets.facet_b_id],
                            interface.Dataset.Facets.field_data.n2[interface.Dataset.Facets.facet_b_id]
                        ])

                        interface.Dataset.Facets.set_rotation_matrix(
                            u0=interface.Dataset.Facets.u0 /
                            np.linalg.norm(interface.Dataset.Facets.u0),
                            v0=interface.Dataset.Facets.v0 /
                            np.linalg.norm(interface.Dataset.Facets.v0),
                            w0=interface.Dataset.Facets.w0 /
                            np.linalg.norm(interface.Dataset.Facets.w0),
                            u=u,
                            v=v,
                        )

                        interface.Dataset.Facets.rotate_particle()

                        display(Markdown(
                            "# Computing interplanar angles from reference"
                        ))
                        print(
                            f"Used reference: {interface.Dataset.Facets.hkl_reference}")
                        interface.Dataset.Facets.fixed_reference(
                            hkl_reference=interface.Dataset.Facets.hkl_reference)

                        display(
                            Markdown("""# Strain values for each surface voxel \
                            and averaged per facet"""))
                        interface.Dataset.Facets.plot_strain(
                            elev=interface.Dataset.Facets.elev,
                            azim=interface.Dataset.Facets.azim
                        )

                        display(Markdown(
                            """# Displacement values for each surface voxel \
                            and averaged per facet"""))
                        interface.Dataset.Facets.plot_displacement(
                            elev=interface.Dataset.Facets.elev,
                            azim=interface.Dataset.Facets.azim
                        )

                        display(Markdown("""# Evolution curves"""))
                        interface.Dataset.Facets.evolution_curves()

                        # Also save edges and corners data
                        interface.Dataset.Facets.save_edges_corners_data()

                        display(Markdown("""# Field data"""))
                        display(interface.Dataset.Facets.field_data)

                        button_save_facet_data = widgets.Button(
                            description="Save data",
                            layout=widgets.Layout(width='50%', height='35px'))
                        display(button_save_facet_data)

                        @ button_save_facet_data.on_click
                        def action_button_save_facet_data(selfbutton):
                            """Save data ..."""
                            try:
                                # Create subfolder
                                try:
                                    os.mkdir(
                                        f"{interface.Dataset.root_folder}{interface.Dataset.scan_name}"
                                        "/postprocessing/facets_analysis/"
                                    )
                                    print(
                                        f"Created {interface.Dataset.root_folder}{interface.Dataset.scan_name}"
                                        "/postprocessing/facets_analysis/"
                                    )
                                except (FileExistsError, PermissionError):
                                    print(
                                        f"{interface.Dataset.root_folder}{interface.Dataset.scan_name}"
                                        "/postprocessing/facets_analysis/ exists"
                                    )

                                # Save data
                                interface.Dataset.Facets.save_data(
                                    f"{interface.Dataset.scan_folder}/postprocessing/"
                                    f"facets_analysis/field_data_{interface.Dataset.scan}.csv"
                                )
                                print(
                                    f"Saved field data as {interface.Dataset.scan_folder}/"
                                    "postprocessing/facets_analysis/"
                                    f"field_data_{interface.Dataset.scan}.csv"
                                )

                                interface.Dataset.Facets.to_hdf5(
                                    f"{interface.Dataset.scan_folder}{interface.Dataset.scan_name}.cxi")
                                print(
                                    f"Saved Facets class attributes in {interface.Dataset.scan_folder}"
                                    f"{interface.Dataset.scan_name}.cxi"
                                )
                            except AttributeError:
                                print(
                                    "Initialize the directories first to "
                                    "save the figures and data ..."
                                )

            @ button_view_particle.on_click
            def action_button_view_particle(selfbutton):
                clear_output(True)
                display(buttons_facets)

                # Display visualisation window of facet class
                display(interface.Dataset.Facets.window)

            # Display button
            display(buttons_facets)

        except TypeError:
            print("Data type not supported.")

    if not load_data:
        interface.TabFacet.parent_folder.disabled = False
        interface.TabFacet.vtk_file_handler(parent_folder)
        print("Cleared window.")
        clear_output(True)
