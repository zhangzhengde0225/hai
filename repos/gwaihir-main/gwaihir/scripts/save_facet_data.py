#!/usr/bin/python
# trace generated using paraview version 5.10.0-RC1
#paraview.compatibility.major = 5
#paraview.compatibility.minor = 10

# Example file
# can be used in the command line like this :
# ?

# import the simple module from the paraview
try:
    from paraview.simple import *
except ModuleNotFoundError:
    print("This script/function must be used with the paraview python environment!")
    exit()

import os


# disable automatic camera reset on 'Show'
paraview.simple._DisableFirstRenderCameraReset()

# Parameters
scan_number = 3854
contour_treshold = 0.4
SampleSize = 30
AngleUncertainty = 8.0
SplatRadius = 0.25
MinRelFacetSize = 0.0006
OfExtraWS = 10

full_path = f'/home/david/Documents/PhDScripts/SIXS_June_2021/reconstructions/new_supports_D6_400/S{scan_number}_amp_disp_strain_fixed_support.vti'
file = os.path.basename(full_path)
dirname = os.path.dirname(full_path)
save_as = dirname + "/" + f"{scan_number}_fa_fixed.vtk"

########################################################## Start script ##########################################################

# load plugin
LoadPlugin('/usr/lib/x86_64-linux-gnu/paraview-5.10/plugins/FacetAnalyser/FacetAnalyser.so',
           remote=False, ns=globals())

# create a new 'XML Image Data Reader'
amp_disp_strain_fixed_supportvti = XMLImageDataReader(
    registrationName=file,
    FileName=[full_path]
)
amp_disp_strain_fixed_supportvti.PointArrayStatus = [
    'amp', 'support', 'disp', 'strain']

# Properties modified on amp_disp_strain_fixed_supportvti
amp_disp_strain_fixed_supportvti.TimeArray = 'None'

# get active view
renderView1 = GetActiveViewOrCreate('RenderView')

# show data in view
s3854_amp_disp_strain_fixed_supportvtiDisplay = Show(
    amp_disp_strain_fixed_supportvti, renderView1, 'UniformGridRepresentation')

# trace defaults for the display properties.
s3854_amp_disp_strain_fixed_supportvtiDisplay.Representation = 'Outline'
s3854_amp_disp_strain_fixed_supportvtiDisplay.ColorArrayName = ['POINTS', '']
s3854_amp_disp_strain_fixed_supportvtiDisplay.SelectTCoordArray = 'None'
s3854_amp_disp_strain_fixed_supportvtiDisplay.SelectNormalArray = 'None'
s3854_amp_disp_strain_fixed_supportvtiDisplay.SelectTangentArray = 'None'
s3854_amp_disp_strain_fixed_supportvtiDisplay.OSPRayScaleArray = 'amp'
s3854_amp_disp_strain_fixed_supportvtiDisplay.OSPRayScaleFunction = 'PiecewiseFunction'
s3854_amp_disp_strain_fixed_supportvtiDisplay.SelectOrientationVectors = 'None'
s3854_amp_disp_strain_fixed_supportvtiDisplay.ScaleFactor = 179.10000000000002
s3854_amp_disp_strain_fixed_supportvtiDisplay.SelectScaleArray = 'amp'
s3854_amp_disp_strain_fixed_supportvtiDisplay.GlyphType = 'Arrow'
s3854_amp_disp_strain_fixed_supportvtiDisplay.GlyphTableIndexArray = 'amp'
s3854_amp_disp_strain_fixed_supportvtiDisplay.GaussianRadius = 8.955
s3854_amp_disp_strain_fixed_supportvtiDisplay.SetScaleArray = ['POINTS', 'amp']
s3854_amp_disp_strain_fixed_supportvtiDisplay.ScaleTransferFunction = 'PiecewiseFunction'
s3854_amp_disp_strain_fixed_supportvtiDisplay.OpacityArray = ['POINTS', 'amp']
s3854_amp_disp_strain_fixed_supportvtiDisplay.OpacityTransferFunction = 'PiecewiseFunction'
s3854_amp_disp_strain_fixed_supportvtiDisplay.DataAxesGrid = 'GridAxesRepresentation'
s3854_amp_disp_strain_fixed_supportvtiDisplay.PolarAxes = 'PolarAxesRepresentation'
s3854_amp_disp_strain_fixed_supportvtiDisplay.ScalarOpacityUnitDistance = 15.588457268119896
s3854_amp_disp_strain_fixed_supportvtiDisplay.OpacityArrayName = [
    'POINTS', 'amp']
s3854_amp_disp_strain_fixed_supportvtiDisplay.IsosurfaceValues = [0.5]
s3854_amp_disp_strain_fixed_supportvtiDisplay.SliceFunction = 'Plane'
s3854_amp_disp_strain_fixed_supportvtiDisplay.Slice = 99

# init the 'Plane' selected for 'SliceFunction'
s3854_amp_disp_strain_fixed_supportvtiDisplay.SliceFunction.Origin = [
    895.5, 895.5, 895.5]

# reset view to fit data
renderView1.ResetCamera(False)

# update the view to ensure updated data information
renderView1.Update()

# create a new 'Contour'
contour1 = Contour(registrationName='Contour1',
                   Input=amp_disp_strain_fixed_supportvti)
contour1.ContourBy = ['POINTS', 'amp']
contour1.ComputeGradients = 1
contour1.Isosurfaces = [contour_treshold]
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
contour1Display.ScaleFactor = 62.1363525390625
contour1Display.SelectScaleArray = 'amp'
contour1Display.GlyphType = 'Arrow'
contour1Display.GlyphTableIndexArray = 'amp'
contour1Display.GaussianRadius = 3.106817626953125
contour1Display.SetScaleArray = ['POINTS', 'amp']
contour1Display.ScaleTransferFunction = 'PiecewiseFunction'
contour1Display.OpacityArray = ['POINTS', 'amp']
contour1Display.OpacityTransferFunction = 'PiecewiseFunction'
contour1Display.DataAxesGrid = 'GridAxesRepresentation'
contour1Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
contour1Display.ScaleTransferFunction.Points = [
    0.4000000059604645, 0.0, 0.5, 0.0, 0.4000610411167145, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
contour1Display.OpacityTransferFunction.Points = [
    0.4000000059604645, 0.0, 0.5, 0.0, 0.4000610411167145, 1.0, 0.5, 0.0]

# show color bar/color legend
contour1Display.SetScalarBarVisibility(renderView1, True)

# update the view to ensure updated data information
renderView1.Update()

# get opacity transfer function/opacity map for 'amp'
ampPWF = GetOpacityTransferFunction('amp')

# hide data in view
Hide(amp_disp_strain_fixed_supportvti, renderView1)

# reset view to fit data bounds
renderView1.ResetCamera(599.22265625, 1220.586181640625, 690.1774291992188,
                        1120.3206787109375, 614.9483032226562, 1174.08203125, False)

# create a new 'Facet Analyser'
facetAnalyser1 = FacetAnalyser(
    registrationName='FacetAnalyser1', Input=contour1)

# Properties modified on facetAnalyser1
facetAnalyser1.SampleSize = SampleSize
facetAnalyser1.AngleUncertainty = AngleUncertainty
facetAnalyser1.SplatRadius = SplatRadius
facetAnalyser1.MinRelFacetSize = MinRelFacetSize
facetAnalyser1.OfExtraWS = OfExtraWS

# show data in view
facetAnalyser1Display = Show(
    facetAnalyser1, renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
facetAnalyser1Display.Representation = 'Surface'
facetAnalyser1Display.ColorArrayName = ['POINTS', 'amp']
facetAnalyser1Display.LookupTable = ampLUT
facetAnalyser1Display.SelectTCoordArray = 'None'
facetAnalyser1Display.SelectNormalArray = 'Normals'
facetAnalyser1Display.SelectTangentArray = 'None'
facetAnalyser1Display.OSPRayScaleArray = 'amp'
facetAnalyser1Display.OSPRayScaleFunction = 'PiecewiseFunction'
facetAnalyser1Display.SelectOrientationVectors = 'Gradients'
facetAnalyser1Display.ScaleFactor = 62.1363525390625
facetAnalyser1Display.SelectScaleArray = 'amp'
facetAnalyser1Display.GlyphType = 'Arrow'
facetAnalyser1Display.GlyphTableIndexArray = 'amp'
facetAnalyser1Display.GaussianRadius = 3.106817626953125
facetAnalyser1Display.SetScaleArray = ['POINTS', 'amp']
facetAnalyser1Display.ScaleTransferFunction = 'PiecewiseFunction'
facetAnalyser1Display.OpacityArray = ['POINTS', 'amp']
facetAnalyser1Display.OpacityTransferFunction = 'PiecewiseFunction'
facetAnalyser1Display.DataAxesGrid = 'GridAxesRepresentation'
facetAnalyser1Display.PolarAxes = 'PolarAxesRepresentation'

# init the 'PiecewiseFunction' selected for 'ScaleTransferFunction'
facetAnalyser1Display.ScaleTransferFunction.Points = [
    0.4000000059604645, 0.0, 0.5, 0.0, 0.4000610411167145, 1.0, 0.5, 0.0]

# init the 'PiecewiseFunction' selected for 'OpacityTransferFunction'
facetAnalyser1Display.OpacityTransferFunction.Points = [
    0.4000000059604645, 0.0, 0.5, 0.0, 0.4000610411167145, 1.0, 0.5, 0.0]

# hide data in view
Hide(contour1, renderView1)

# show color bar/color legend
facetAnalyser1Display.SetScalarBarVisibility(renderView1, True)

# show data in view
facetAnalyser1Display_1 = Show(OutputPort(
    facetAnalyser1, 1), renderView1, 'GeometryRepresentation')

# get color transfer function/color map for 'PlaneIDs'
planeIDsLUT = GetColorTransferFunction('PlaneIDs')

# trace defaults for the display properties.
facetAnalyser1Display_1.Representation = 'Surface'
facetAnalyser1Display_1.ColorArrayName = ['CELLS', 'PlaneIDs']
facetAnalyser1Display_1.LookupTable = planeIDsLUT
facetAnalyser1Display_1.SelectTCoordArray = 'None'
facetAnalyser1Display_1.SelectNormalArray = 'None'
facetAnalyser1Display_1.SelectTangentArray = 'None'
facetAnalyser1Display_1.OSPRayScaleFunction = 'PiecewiseFunction'
facetAnalyser1Display_1.SelectOrientationVectors = 'None'
facetAnalyser1Display_1.ScaleFactor = 64.80751953125001
facetAnalyser1Display_1.SelectScaleArray = 'PlaneIDs'
facetAnalyser1Display_1.GlyphType = 'Arrow'
facetAnalyser1Display_1.GlyphTableIndexArray = 'PlaneIDs'
facetAnalyser1Display_1.GaussianRadius = 3.2403759765625
facetAnalyser1Display_1.SetScaleArray = [None, '']
facetAnalyser1Display_1.ScaleTransferFunction = 'PiecewiseFunction'
facetAnalyser1Display_1.OpacityArray = [None, '']
facetAnalyser1Display_1.OpacityTransferFunction = 'PiecewiseFunction'
facetAnalyser1Display_1.DataAxesGrid = 'GridAxesRepresentation'
facetAnalyser1Display_1.PolarAxes = 'PolarAxesRepresentation'

# hide data in view
Hide(contour1, renderView1)

# show color bar/color legend
facetAnalyser1Display_1.SetScalarBarVisibility(renderView1, True)

# show data in view
facetAnalyser1Display_2 = Show(OutputPort(
    facetAnalyser1, 2), renderView1, 'GeometryRepresentation')

# trace defaults for the display properties.
facetAnalyser1Display_2.Representation = 'Surface'
facetAnalyser1Display_2.ColorArrayName = [None, '']
facetAnalyser1Display_2.SelectTCoordArray = 'None'
facetAnalyser1Display_2.SelectNormalArray = 'None'
facetAnalyser1Display_2.SelectTangentArray = 'None'
facetAnalyser1Display_2.OSPRayScaleFunction = 'PiecewiseFunction'
facetAnalyser1Display_2.SelectOrientationVectors = 'None'
facetAnalyser1Display_2.ScaleFactor = 64.80751953125001
facetAnalyser1Display_2.SelectScaleArray = 'None'
facetAnalyser1Display_2.GlyphType = 'Arrow'
facetAnalyser1Display_2.GlyphTableIndexArray = 'None'
facetAnalyser1Display_2.GaussianRadius = 3.2403759765625
facetAnalyser1Display_2.SetScaleArray = [None, '']
facetAnalyser1Display_2.ScaleTransferFunction = 'PiecewiseFunction'
facetAnalyser1Display_2.OpacityArray = [None, '']
facetAnalyser1Display_2.OpacityTransferFunction = 'PiecewiseFunction'
facetAnalyser1Display_2.DataAxesGrid = 'GridAxesRepresentation'
facetAnalyser1Display_2.PolarAxes = 'PolarAxesRepresentation'

# hide data in view
Hide(contour1, renderView1)

# update the view to ensure updated data information
renderView1.Update()

# set active source
SetActiveSource(facetAnalyser1)

# set active source
SetActiveSource(facetAnalyser1)

# save data
SaveData(
    save_as,
    proxy=facetAnalyser1,
    PointDataArrays=[
        'Gradients', 'Normals',
        'amp', 'disp', 'strain', 'support'
    ],
    CellDataArrays=['FacetIds', 'FacetProbabilities'],
    FieldDataArrays=[
        'FacetCenters', 'FacetIds', 'absFacetSize',
        'angleWeights', 'cellPairingIds', 'facetNormals',
        'interplanarAngles', 'relFacetSize'
    ]
)

# ================================================================
# addendum: following script captures some of the application
# state to faithfully reproduce the visualization during playback
# ================================================================

# get layout
layout1 = GetLayout()

# --------------------------------
# saving layout sizes for layouts

# layout/tab size in pixels
layout1.SetSize(1368, 773)

# -----------------------------------
# saving camera placements for views

# current camera placement for renderView1
renderView1.CameraPosition = [-766.032828859738,
                              814.4020238977992, 200.85277213289191]
renderView1.CameraFocalPoint = [
    909.9044189453125, 905.2490539550781, 894.5151672363281]
renderView1.CameraViewUp = [0.1740426621189035,
                            0.8304192564460544, -0.5292570361234202]
renderView1.CameraParallelScale = 470.0389270060838

# --------------------------------------------
# uncomment the following to render all views
# RenderAllViews()
# alternatively, if you want to write images, you can use SaveScreenshot(...).
