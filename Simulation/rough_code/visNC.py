import vtkmodules.all as vtk
import netCDF4

# Load the NetCDF data
ncfile = netCDF4.Dataset("output.nc", "r")
field_data = ncfile.variables["field"][:]

# Define the scalar range for the pseudocolor mapping
min_value = field_data.min()
max_value = field_data.max()

# Create a VTK renderer and render window
renderer = vtk.vtkRenderer()
render_window = vtk.vtkRenderWindow()
render_window.AddRenderer(renderer)

# Create a VTK render window interactor
render_window_interactor = vtk.vtkRenderWindowInteractor()
render_window_interactor.SetRenderWindow(render_window)

# Set up the render window size and background color
render_window.SetSize(800, 600)
renderer.SetBackground(1.0, 1.0, 1.0)  # White background

# Define a color transfer function (customize the color map as needed)
# Define a color transfer function with multiple points
color_transfer_function = vtk.vtkColorTransferFunction()

color_transfer_function.AddRGBPoint(min_value, 1.0, 0.0, 0.0)  # Green for lower values
  # Red for intermediate values
color_transfer_function.AddRGBPoint(max_value, 0.0, 1.0, 0.0)  # Blue for higher values



# Loop through all time steps and create images
for time_step in range(field_data.shape[0]):
    # Create a VTK grid for each time step
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(field_data.shape[1], field_data.shape[2], 1)

    # Create points for the grid
    points = vtk.vtkPoints()
    for x in range(field_data.shape[1]):
        for y in range(field_data.shape[2]):
            points.InsertNextPoint(x, y, 0)
    grid.SetPoints(points)

    # Create a VTK array to store the scalar data
    scalar_data = vtk.vtkFloatArray()
    scalar_data.SetNumberOfComponents(1)
    scalar_data.SetName("WeatherData")

    # Flatten the 2D data to a 1D array for the current time step
    flat_data = field_data[time_step, :, :].flatten()
    for value in flat_data:
        scalar_data.InsertNextValue(value)

    grid.GetPointData().SetScalars(scalar_data)

    # Create a VTK mapper
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(grid)
    mapper.SetScalarRange(min_value, max_value)  # Set the scalar range for the color map

    # Create a VTK actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Set the actor's properties to use pseudocolor
    actor.GetProperty().SetColor(1.0, 1.0, 1.0)  # Set the actor's color to white (initially)
    actor.GetProperty().SetOpacity(1.0)  # Set the opacity to 1.0

    # Use the color transfer function to map the scalar data to colors
    mapper.GetLookupTable().SetScaleToLinear()
    mapper.SetLookupTable(color_transfer_function)

    # Add the actor to the renderer
    renderer.AddActor(actor)

    # Render the scene
    render_window.Render()

    # Capture and save the image for this time step (you can save it as an image file)
    screenshotter = vtk.vtkWindowToImageFilter()
    screenshotter.SetInput(render_window)
    screenshotter.Update()

    writer = vtk.vtkPNGWriter()
    writer.SetFileName(f"/Users/kundankumar/Downloads/{time_step:04d}.png")  # Save as PNG files with a zero-padded time step
    writer.SetInputConnection(screenshotter.GetOutputPort())
    writer.Write()

# Start the interaction
render_window_interactor.Start()