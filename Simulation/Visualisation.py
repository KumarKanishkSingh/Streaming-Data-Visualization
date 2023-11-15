import vtkmodules.all as vtk
import numpy as np
import socket
import struct

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
server_address = ('172.23.151.115', 5566)  # Replace 'server_ip' with the actual server IP
client_socket.connect(server_address)

# Receive the data as a 2D array
for t in range(1,10):

    data_shape = (64, 64)
    data = np.empty(data_shape)
    for row in range(data_shape[0]):
        for col in range(data_shape[1]):
 # Receive the length of the float in bytes (assuming 4 bytes for float)
            len_bytes = client_socket.recv(4)
            value_len = struct.unpack('I', len_bytes)[0]  # Unpack as unsigned int
            print(value_len)
            # Receive the float value based on the length received
            value_bytes = client_socket.recv(value_len)
            value = struct.unpack('d', value_bytes)[0]  # Unpack as float
            data[row, col] = value

            # value_bytes = client_socket.recv(8)  # Assuming a double is 8 bytes
            # if len(value_bytes) != 8:
            #     # print("Error: Unexpected number of bytes received.")
            #     value=0.0
            #     # Handle the error or exit the loop
            # else:

            #     # value = struct.unpack('d', value_bytes)[0]
            #     # data[row, col] = value
            #     value = struct.unpack('d', value_bytes)[0]
            # data[row, col] = value

    # Close the socket
    # client_socket.close()

    # Define the scalar range for the pseudocolor mapping
    # if t==1:
    min_value = data.min()
    max_value = data.max()

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
    color_transfer_function = vtk.vtkColorTransferFunction()
    color_transfer_function.AddRGBPoint(min_value, 1.0, 0.0, 0.0)  # Green for lower values
    color_transfer_function.AddRGBPoint(max_value, 0.0, 1.0, 0.0)  # Blue for higher values

    # Create a VTK grid
    grid = vtk.vtkStructuredGrid()
    grid.SetDimensions(data_shape[0], data_shape[1], 1)

    # Create points for the grid
    points = vtk.vtkPoints()
    for x in range(data_shape[0]):
        for y in range(data_shape[1]):
            points.InsertNextPoint(x, y, 0)
    grid.SetPoints(points)

    # Create a VTK array to store the scalar data
    scalar_data = vtk.vtkFloatArray()
    scalar_data.SetNumberOfComponents(1)
    scalar_data.SetName("WeatherData")

    # Flatten the 2D data to a 1D array
    flat_data = data.flatten()
    for value in flat_data:
        scalar_data.InsertNextValue(value)

    grid.GetPointData().SetScalars(scalar_data)

    # Create a VTK mapper
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(grid)
    mapper.SetScalarRange(min_value, max_value)

    # Create a VTK actor
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(1.0, 1.0, 1.0)
    actor.GetProperty().SetOpacity(1.0)
    mapper.GetLookupTable().SetScaleToLinear()
    mapper.SetLookupTable(color_transfer_function)

    # Add the actor to the renderer
    renderer.AddActor(actor)

    # Render the scene
    render_window.Render()

    # Start the interaction
    render_window_interactor.Start()
    
    # message = "1"
    # client_socket.sendall(message.encode('utf-8'))

client_socket.close()