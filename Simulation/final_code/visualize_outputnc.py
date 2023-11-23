import vtkmodules.all as vtk
import netCDF4
import time

tt_loading_data = 0
tt_visualizing_data = 0
tt_creating_data = 0
tt_broadcasting_data = 0


begin = time.time()
# Load the NetCDF data
ncfile = netCDF4.Dataset("output.nc", "r")
end = time.time()

tt_creating_data = ncfile.variables["tt_creating_data"][:]
tt_broadcasting_data = ncfile.variables["tt_broadcasting_data"][:]

tt_loading_data = end - begin

begin = time.time()
field_data = ncfile.variables["field"][:]

numSteps = field_data.shape[0]

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
color_transfer_function.AddRGBPoint(max_value, 0.0, 1.0, 0.0)  # Blue for higher values

# Create a VTK grid outside the loop to reuse in each iteration
grid = vtk.vtkStructuredGrid()
grid.SetDimensions(field_data.shape[1], field_data.shape[2], 1)

# print(field_data.shape[1])
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

# Create a VTK mapper
mapper = vtk.vtkDataSetMapper()
mapper.SetInputData(grid)
mapper.SetScalarRange(min_value, max_value)  # Set the scalar range for the color map
mapper.GetLookupTable().SetScaleToLinear()
mapper.SetLookupTable(color_transfer_function)

# Create a VTK actor
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetColor(1.0, 1.0, 1.0)  # Set the actor's color to white (initially)
actor.GetProperty().SetOpacity(1.0)  # Set the opacity to 1.0

# Add the actor to the renderer
renderer.AddActor(actor)

end = time.time()

tt_visualizing_data = end - begin

# Loop through all time steps and create images
for time_step in range(numSteps):
    begin = time.time()
    # Flatten the 2D data to a 1D array for the current time step
    flat_data = field_data[time_step, :, :].flatten()

    # Create a new vtkFloatArray
    scalar_data = vtk.vtkFloatArray()
    scalar_data.SetNumberOfComponents(1)
    scalar_data.SetName("WeatherData")

    # Set the size of the array
    scalar_data.SetNumberOfTuples(len(flat_data))

    # Set individual tuple values
    for i, value in enumerate(flat_data):
        scalar_data.SetTuple1(i, value)

    # Update the scalar data for the grid
    grid.GetPointData().SetScalars(scalar_data)

    # time.sleep(1)

    # Render the scene
    render_window.Render()
    end = time.time()
    tt_visualizing_data = tt_visualizing_data + end - begin
    # Start the interaction
    input("Press Enter to continue to the next time step...")

    # Clear actors from the renderer before adding a new one
    renderer.RemoveActor(actor)



print("Total time taken to create, load-read and visualise data for ({}*{}) grid-size 2D array for {} time steps is {}, {} and {} seconds.".format(field_data.shape[1], field_data.shape[2], numSteps, tt_creating_data, tt_loading_data + tt_broadcasting_data, tt_visualizing_data))
render_window_interactor.Start()
