#!/usr/bin/python

# Example file
# can be used in the command line like this :
# plot_paraview_slices.py reconstructions/vti_files/S3572_amp-disp-strain_mode_avg3_apodize_blackman_crystalframe.vti strain 0.5

# import the simple module from the paraview
try:
    from paraview.simple import *
except ModuleNotFoundError:
    print("This script/function must be used with the paraview python environment!")
    exit()

import ast
import sys
import os
import glob
import numpy as np


def save_multislice(
    filename,
    array="disp",
    contour=0.5,
    save_dir=None,
    pixel_width=1280,
    pixel_height=720,
    scale_factor=61,
    gaussian_radius=3.074962463378906,
):
    """
    Create a png image from a vti file, with view along its
    3 axis.

    This function must be executed in the pvpython environment of Paraview 5.9 !

    Some parameters are hardcoded and should be determined with the Trace in
    Paraview. To do so:
    Tools >> Start Trace
    Create your three RenderViews and center the particle, choose an orientation
    for each view.
    Tools >> Stop Trace
    Extract from the printed code the following parameters:
        scale_factor, gaussian_radius (common to the three views)
        focal_point
        camera_parallel_scale
        camera_position

    Once these are determined, you can use the function in the terminal as follows:
    /home/david/Packages/ParaView5.9/bin/pvpython plot_paraview_slices.py file.vti

    :param filename: full path to .vti file
    :param array: contouring values to show, can be 'amp', disp', 'strain' or
     'bulk'
    :param contour: isosuface threshold
    :param save_dir: directory for image, default is vti file directory
    :param pixel_width: width in pixels for the image
    :param pixel_height: height in pixels for the image
    :param scale_factor: contouring parameter, use the Trace in paraview
     to determine it
    :param gaussian_radius: contouring parameter, use the Trace in paraview
     to determine it
    """

    # Determine the following parameters with the Trace in Paraview

    # Focal point is the same for all views
    focal_point = [902, 904, 891]

    # The camera scale or its position is not
    # it's ok to round the values
    camera_parallel_scale = [713, 751, 752]

    camera_position = np.array([
        [-1798,   904,   891],
        [902, -1936,   891],
        [902,   904, -1955]
    ])

    # disable automatic camera reset on 'Show'
    paraview.simple._DisableFirstRenderCameraReset()

    print("Opening", filename)
    # create a new 'XML Image Data Reader'
    data = XMLImageDataReader(
        registrationName='Particle',
        FileName=[filename])
    data.PointArrayStatus = ['amp', 'bulk', 'disp', 'strain']

    # Properties modified on data
    data.TimeArray = 'None'

    # get active view
    renderView1 = GetActiveViewOrCreate('RenderView')

    # show data in view
    data_display = Show(data, renderView1, 'UniformGridRepresentation')

    # reset view to fit data
    renderView1.ResetCamera()

    # get the material library
    materialLibrary1 = GetMaterialLibrary()

    # update the view to ensure updated data information
    renderView1.Update()

    # hide data in view
    Hide(data, renderView1)

    ######### FIRST CONTOUR #########

    # create a new 'Contour'
    contour1 = Contour(registrationName='Contour1', Input=data)
    contour1.ContourBy = ['POINTS', 'amp']
    contour1.ComputeGradients = 1
    contour1.Isosurfaces = [contour]
    contour1.PointMergeMethod = 'Uniform Binning'

    # show data in view
    contour1Display = Show(contour1, renderView1, 'GeometryRepresentation')

    # get color transfer function/color map for 'amp'
    ampLUT = GetColorTransferFunction('amp')

    # trace defaults for the display properties.
    contour1Display.Representation = 'Surface'
    contour1Display.ColorArrayName = ['POINTS', 'amp']
    contour1Display.LookupTable = ampLUT
    contour1Display.SelectTCoordArray = 'None'
    contour1Display.SelectNormalArray = 'Normals'
    contour1Display.SelectTangentArray = 'None'
    contour1Display.OSPRayScaleArray = 'amp'
    contour1Display.OSPRayScaleFunction = 'PiecewiseFunction'
    contour1Display.SelectOrientationVectors = 'Gradients'
    contour1Display.ScaleFactor = scale_factor
    # contour2Display.ScaleFactor = 61.49924926757813
    contour1Display.SelectScaleArray = 'amp'
    contour1Display.GlyphType = 'Arrow'
    contour1Display.GlyphTableIndexArray = 'amp'
    contour1Display.GaussianRadius = gaussian_radius
    # contour2Display.GaussianRadius = 3.074962463378906
    contour1Display.SetScaleArray = ['POINTS', 'amp']
    contour1Display.ScaleTransferFunction = 'PiecewiseFunction'
    contour1Display.OpacityArray = ['POINTS', 'amp']
    contour1Display.OpacityTransferFunction = 'PiecewiseFunction'
    contour1Display.DataAxesGrid = 'GridAxesRepresentation'
    contour1Display.PolarAxes = 'PolarAxesRepresentation'

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    contour1Display.ScaleTransferFunction.Points = [
        0.5, 0.0, 0.5, 0.0, 0.5, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    contour1Display.OpacityTransferFunction.Points = [
        0.5, 0.0, 0.5, 0.0, 0.5, 1.0, 0.5, 0.0]

    # reset view to fit data
    renderView1.ResetCamera()

    # show color bar/color legend
    contour1Display.SetScalarBarVisibility(renderView1, True)

    # update the view to ensure updated data information
    renderView1.Update()

    # get opacity transfer function/opacity map for 'amp'
    ampPWF = GetOpacityTransferFunction('amp')

    # set scalar coloring
    ColorBy(contour1Display, ('POINTS', array))

    # Hide the scalar bar for this color map if no visible data is colored by it.
    HideScalarBarIfNotNeeded(ampLUT, renderView1)

    # rescale color and/or opacity maps used to include current data range
    contour1Display.RescaleTransferFunctionToDataRange(True, False)

    # show color bar/color legend
    contour1Display.SetScalarBarVisibility(renderView1, True)

    # get color transfer function/color map for array
    dispLUT = GetColorTransferFunction(array)

    # get opacity transfer function/opacity map for array
    dispPWF = GetOpacityTransferFunction(array)

    ######### SECOND CONTOUR #########

    # get layout
    layout1 = GetLayout()

    # split cell
    layout1.SplitHorizontal(0, 0.5)

    # Create a new 'Render View'
    renderView2 = CreateView('RenderView')
    renderView2.AxesGrid = 'GridAxes3DActor'
    renderView2.StereoType = 'Crystal Eyes'
    renderView2.CameraFocalDisk = 1.0
    renderView2.BackEnd = 'OSPRay raycaster'
    renderView2.OSPRayMaterialLibrary = materialLibrary1

    # assign view to a particular cell in the layout
    AssignViewToLayout(view=renderView2, layout=layout1, hint=2)

    # set active view
    SetActiveView(renderView2)

    # set active source
    SetActiveSource(contour1)

    # show data in view
    contour1Display_1 = Show(contour1, renderView2, 'GeometryRepresentation')

    # trace defaults for the display properties.
    contour1Display_1.Representation = 'Surface'
    contour1Display_1.ColorArrayName = ['POINTS', 'amp']
    contour1Display_1.LookupTable = ampLUT
    contour1Display_1.SelectTCoordArray = 'None'
    contour1Display_1.SelectNormalArray = 'Normals'
    contour1Display_1.SelectTangentArray = 'None'
    contour1Display_1.OSPRayScaleArray = 'amp'
    contour1Display_1.OSPRayScaleFunction = 'PiecewiseFunction'
    contour1Display_1.SelectOrientationVectors = 'Gradients'
    contour1Display.ScaleFactor = scale_factor
    # contour2Display.ScaleFactor = 61.49924926757813
    contour1Display.SelectScaleArray = 'amp'
    contour1Display.GlyphType = 'Arrow'
    contour1Display.GlyphTableIndexArray = 'amp'
    contour1Display.GaussianRadius = gaussian_radius
    # contour2Display.GaussianRadius = 3.074962463378906
    contour1Display_1.SetScaleArray = ['POINTS', 'amp']
    contour1Display_1.ScaleTransferFunction = 'PiecewiseFunction'
    contour1Display_1.OpacityArray = ['POINTS', 'amp']
    contour1Display_1.OpacityTransferFunction = 'PiecewiseFunction'
    contour1Display_1.DataAxesGrid = 'GridAxesRepresentation'
    contour1Display_1.PolarAxes = 'PolarAxesRepresentation'

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    contour1Display_1.ScaleTransferFunction.Points = [
        0.5, 0.0, 0.5, 0.0, 0.5, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    contour1Display_1.OpacityTransferFunction.Points = [
        0.5, 0.0, 0.5, 0.0, 0.5, 1.0, 0.5, 0.0]

    # show color bar/color legend
    contour1Display_1.SetScalarBarVisibility(renderView2, True)

    # reset view to fit data
    renderView2.ResetCamera()

    # set scalar coloring
    ColorBy(contour1Display_1, ('POINTS', array))

    # Hide the scalar bar for this color map if no visible data is colored by it.
    HideScalarBarIfNotNeeded(ampLUT, renderView2)

    # rescale color and/or opacity maps used to include current data range
    contour1Display_1.RescaleTransferFunctionToDataRange(True, False)

    # show color bar/color legend
    contour1Display_1.SetScalarBarVisibility(renderView2, True)

    ######### THIRD CONTOUR #########

    # split cell
    layout1.SplitHorizontal(2, 0.5)

    # Create a new 'Render View'
    renderView3 = CreateView('RenderView')
    renderView3.AxesGrid = 'GridAxes3DActor'
    renderView3.StereoType = 'Crystal Eyes'
    renderView3.CameraFocalDisk = 1.0
    renderView3.BackEnd = 'OSPRay raycaster'
    renderView3.OSPRayMaterialLibrary = materialLibrary1

    # assign view to a particular cell in the layout
    AssignViewToLayout(view=renderView3, layout=layout1, hint=6)

    # resize frame
    layout1.SetSplitFraction(0, 0.33)

    # set active view
    SetActiveView(renderView3)

    # show data in view
    contour1Display_2 = Show(contour1, renderView3, 'GeometryRepresentation')

    # trace defaults for the display properties.
    contour1Display_2.Representation = 'Surface'
    contour1Display_2.ColorArrayName = ['POINTS', 'amp']
    contour1Display_2.LookupTable = ampLUT
    contour1Display_2.SelectTCoordArray = 'None'
    contour1Display_2.SelectNormalArray = 'Normals'
    contour1Display_2.SelectTangentArray = 'None'
    contour1Display_2.OSPRayScaleArray = 'amp'
    contour1Display_2.OSPRayScaleFunction = 'PiecewiseFunction'
    contour1Display_2.SelectOrientationVectors = 'Gradients'
    contour1Display.ScaleFactor = scale_factor
    # contour2Display.ScaleFactor = 61.49924926757813
    contour1Display.SelectScaleArray = 'amp'
    contour1Display.GlyphType = 'Arrow'
    contour1Display.GlyphTableIndexArray = 'amp'
    contour1Display.GaussianRadius = gaussian_radius
    # contour2Display.GaussianRadius = 3.074962463378906
    contour1Display_2.SetScaleArray = ['POINTS', 'amp']
    contour1Display_2.ScaleTransferFunction = 'PiecewiseFunction'
    contour1Display_2.OpacityArray = ['POINTS', 'amp']
    contour1Display_2.OpacityTransferFunction = 'PiecewiseFunction'
    contour1Display_2.DataAxesGrid = 'GridAxesRepresentation'
    contour1Display_2.PolarAxes = 'PolarAxesRepresentation'

    # init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
    contour1Display_2.ScaleTransferFunction.Points = [
        0.5, 0.0, 0.5, 0.0, 0.5, 1.0, 0.5, 0.0]

    # init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
    contour1Display_2.OpacityTransferFunction.Points = [
        0.5, 0.0, 0.5, 0.0, 0.5, 1.0, 0.5, 0.0]

    # show color bar/color legend
    contour1Display_2.SetScalarBarVisibility(renderView3, True)

    # reset view to fit data
    renderView3.ResetCamera()

    # set scalar coloring
    ColorBy(contour1Display_2, ('POINTS', array))

    # Hide the scalar bar for this color map if no visible data is colored by it.
    HideScalarBarIfNotNeeded(ampLUT, renderView3)

    # rescale color and/or opacity maps used to include current data range
    contour1Display_2.RescaleTransferFunctionToDataRange(True, False)

    # show color bar/color legend
    contour1Display_2.SetScalarBarVisibility(renderView3, True)

    ########### SCALE FINAL IMAGE #############

    # Enter preview mode
    layout1.PreviewMode = [pixel_width, pixel_height]

    # layout/tab size in pixels
    layout1.SetSize(pixel_width, pixel_height)

    ########### VIEWS ########

    # current camera placement for renderView1renderView2
    renderView1.CameraPosition = camera_position[0]
    renderView1.CameraFocalPoint = focal_point
    renderView1.CameraViewUp = [0.0, 0.0, 1.0]
    renderView1.CameraParallelScale = camera_parallel_scale[0]

    # current camera placement for renderView2
    renderView2.CameraPosition = camera_position[1]
    renderView2.CameraFocalPoint = focal_point
    renderView2.CameraViewUp = [0.0, 0.0, 1.0]
    renderView2.CameraParallelScale = camera_parallel_scale[1]

    # current camera placement for renderView3
    renderView3.CameraPosition = camera_position[2]
    renderView3.CameraFocalPoint = focal_point
    renderView3.CameraParallelScale = camera_parallel_scale[2]

    ########## TEXT ###############

    # create a new 'Text'
    text1 = Text(registrationName='Text1')

    # find source
    # s3572_ampdispstrain_mode_avg3_apodize_blackman_crystalframevti = FindSource('S3572_amp-disp-strain_mode_avg3_apodize_blackman_crystalframe.vti')

    # find source
    # contour1 = FindSource('Contour1')
    # SetActiveSource(contour1)

    # find view
    renderView1 = FindViewOrCreate('RenderView1', viewtype='RenderView')

    # set active view
    SetActiveView(renderView1)

    # Properties modified on text1
    text1.Text = f'Contour = {contour}'

    # get active view
    # renderView1 = GetActiveViewOrCreate('RenderView')

    # show data in view
    text1Display = Show(text1, renderView1, 'TextSourceRepresentation')

    # update the view to ensure updated data information
    renderView1.Update()

    ########## COLORBAR ###############

    # disable automatic camera reset on 'Show'
    paraview.simple._DisableFirstRenderCameraReset()

    # get color transfer function/color map for array
    dispLUT = GetColorTransferFunction(array)

    # Rescale transfer function

    cbar_limits = {
        "amp": [-1, 1],
        "bulk": [-1, 1],
        "disp": [-0.5, 0.5],
        "strain": [-0.0005, 0.0005],
    }

    dispLUT.RescaleTransferFunction(
        cbar_limits[array][0], cbar_limits[array][1])

    # get opacity transfer function/opacity map for array
    dispPWF = GetOpacityTransferFunction(array)

    # Rescale transfer function
    dispPWF.RescaleTransferFunction(
        cbar_limits[array][0], cbar_limits[array][1])

    # find view
    renderView2 = FindViewOrCreate('RenderView2', viewtype='RenderView')

    # set active view
    SetActiveView(renderView2)

    # find view
    renderView3 = FindViewOrCreate('RenderView3', viewtype='RenderView')

    # set active view
    SetActiveView(renderView3)

    # find view
    renderView1 = FindViewOrCreate('RenderView1', viewtype='RenderView')

    # set active view
    SetActiveView(renderView1)

    # get color legend/bar for dispLUT in view renderView1
    dispLUTColorBar = GetScalarBar(dispLUT, renderView1)

    # get cbar title
    cbar_titles = {
        "amp": "Amplitude",
        "bulk": "Support",
        "disp": 'Phase (rad)',
        "strain": 'Strain (%)',
    }

    cbar_formats = {
        "amp": '%-#6.1f',
        "bulk": '%-#6.1f',
        "disp": '%-#6.2f',
        "strain": '%-#6.4f',
    }

    # Properties modified on dispLUTColorBar
    dispLUTColorBar.Title = cbar_titles[array]
    dispLUTColorBar.HorizontalTitle = 1
    dispLUTColorBar.RangeLabelFormat = cbar_formats[array]

    # set active view
    SetActiveView(renderView2)

    # get color legend/bar for dispLUT in view renderView2
    dispLUTColorBar_1 = GetScalarBar(dispLUT, renderView2)

    # Properties modified on dispLUTColorBar_1
    dispLUTColorBar_1.Title = cbar_titles[array]
    dispLUTColorBar_1.HorizontalTitle = 1
    dispLUTColorBar_1.RangeLabelFormat = cbar_formats[array]

    # set active view
    SetActiveView(renderView3)

    # get color legend/bar for dispLUT in view renderView3
    dispLUTColorBar_2 = GetScalarBar(dispLUT, renderView3)

    # Properties modified on dispLUTColorBar_2
    dispLUTColorBar_2.Title = cbar_titles[array]
    dispLUTColorBar_2.HorizontalTitle = 1
    dispLUTColorBar_2.RangeLabelFormat = cbar_formats[array]

    # save screenshot
    if save_dir == None:
        save_dir = os.path.dirname(filename) + "/"

    image_name = os.path.splitext(os.path.basename(filename))[0]
    print(f"Saving as {save_dir}{image_name}_{array}_{contour}.png'")

    SaveScreenshot(save_dir + image_name + '.png',
                   layout1,
                   SaveAllViews=1,
                   ImageResolution=[pixel_width, pixel_height]
                   )


# If used as script, iterate on glob string
if __name__ == "__main__":

    # Takes few arguments
    # glob path for data
    # array
    # contour
    # save folder

    # Print help if error raised
    try:
        filename = os.getcwd() + "/" + glob.glob(sys.argv[1])[0]
        print('Glob string',  sys.argv[1])
    except IndexError:
        print("No matching files found.")
        exit()

    try:
        print("Array:", sys.argv[2])
        array = sys.argv[2]
    except IndexError:
        print("Array defaulted to 'disp'")
        array = "disp"
    except ValueError:
        print("Array must be a string, defaulted to 'disp'")
        array = "disp"

    try:
        print("Contour:", sys.argv[3])
        contour = float(sys.argv[3])
    except IndexError:
        print("Contour defaulted to 0.5")
        contour = 0.5
    except ValueError:
        print("Contour must be a float, defaulted to 0.5")
        contour = 0.5

    try:
        print("Save directory:", sys.argv[4])
        save_dir = sys.argv[4]
    except IndexError:
        print("Save directory defaulted to file folder.")
        save_dir = None

    save_multislice(
        filename=filename,
        array=array,
        contour=contour,
        save_dir=save_dir,
    )
