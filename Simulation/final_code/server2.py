import socket
import pickle
import struct
import time
import numpy as np
from mpi4py import MPI
import os
import time

tt_create_data = 0
tt_sending_data = 0
numSteps = 0
NX = 0
NY = 0

server_ip = None
server_port = None
server_address = None

DT = 60.0  # Time step in seconds
DX = 1000.0  # Spatial step in meters
U0 = 10.0  # Initial horizontal wind velocity (m/s)
V0 = 5.0  # Initial vertical wind velocity (m/s)
KX = 0.00001  # Diffusion coefficient for X-direction
KY = 0.00001  # Diffusion coefficient for Y-direction
KZ = 0.00001  # Diffusion coefficient for Z-direction

def initializeField(field, numSteps, NX, NY):
    for t in range(numSteps):
        for i in range(NX):
            for j in range(NY):
                field[t][i][j] = int.from_bytes(os.urandom(8), byteorder='big') % 100


def simulateWeather(field, rank, num_processes, numSteps, server_address, NX, NY):
    
    global tt_sending_data, tt_create_data

    begin = time.time()
    tempField = [[[0.0 for _ in range(NY)] for _ in range(NX)] for _ in range(numSteps)]

    if rank == 0:

        for t in range(numSteps):
            # Advection
            for i in range(NX):
                for j in range(NY):
                    i_prev = int((i - U0 * DT / DX + NX)) % NX
                    j_prev = int((j - V0 * DT / DX + NY)) % NY
                    tempField[t][i][j] = field[t][i_prev][j_prev]

            # Diffusion
            for i in range(NX):
                for j in range(NY):
                    laplacian = (field[t][(i + 1) % NX][j] + field[t][(i - 1 + NX) % NX][j]
                                  + field[t][i][(j + 1) % NY] + field[t][i][(j - 1 + NY) % NY]
                                  - 4 * field[t][i][j]) / (DX * DX)
                    tempField[t][i][j] += (KX * laplacian + KY * laplacian) * DT

            end = time.time()
            tt_create_data = end - begin

            begin = time.time()
            # tcp connection created and connected to client
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(server_address)
            end = time.time()
            tt_sending_data = end - begin

            # Listen for incoming connections
            server_socket.listen(1)
            print("Waiting for a connection...")

            begin = time.time()
            # Accept a connection
            connection, client_address = server_socket.accept()
            print("Connection from", client_address)

            data_list=tempField[t]
            data_array=np.array(data_list)
            
            # Serialize the NumPy array to bytes
            data_bytes = data_array.tobytes()
            # Send the data
            connection.sendall(data_bytes)

            # print("Sent Array:")
            # print(data_array)
            # print()

            # Close the connection
            connection.close()  
            server_socket.close()
            end = time.time()
            tt_sending_data = tt_sending_data + end - begin

def main():

    global tt_sending_data, tt_create_data, server_ip, server_port, server_address, numSteps, NX, NY

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    num_processes = comm.Get_size()

    # Get user input for NX, NY, IP address, and port
    NX = int(input("Enter the value for NX: "))
    NY = int(input("Enter the value for NY: "))
    server_ip = input("Enter the server IP address: ")
    server_port = int(input("Enter the server port number: "))
    server_address = (server_ip, server_port)
    numSteps = int(input("Enter the number of time steps: "))


    begin = time.time()
    # tcp connection created and connected to client
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(server_address)
    end = time.time()

    tt_sending_data = tt_sending_data + end - begin
    # Listen for incoming connections
    server_socket.listen(1)
    print("Waiting for a connection to send number of time steps...")

    begin = time.time()
    # Accept a connection
    connection, client_address = server_socket.accept()
    print("Connection from", client_address)
    numSteps_bytes = numSteps.to_bytes(4)
    NX_bytes = NX.to_bytes(4)
    NY_bytes = NY.to_bytes(4)

    connection.sendall(numSteps_bytes)
    connection.sendall(NX_bytes)
    connection.sendall(NY_bytes)

    connection.close()  
    server_socket.close()
    end = time.time()
    tt_sending_data = tt_sending_data + end - begin


    field = [[[0.0 for _ in range(NY)] for _ in range(NX)] for _ in range(numSteps)]

    if rank == 0:
        initializeField(field, numSteps,  NX, NY)

    # Distribute the initial field to all processes
    field = comm.bcast(field, root=0)

    simulateWeather(field, rank, num_processes, numSteps, server_address, NX, NY)

    if rank == 0:
        print("Weather simulation completed.")
        # print("Total time to create and send ({}*{}) 2D array for {} time steps is {} and {} seconds.".format(NX, NY, numSteps, tt_create_data, tt_sending_data))


if __name__ == "__main__":
    main()

    # tcp connection created and connected to client
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(server_address)

    # Listen for incoming connections
    server_socket.listen(1)
    print("Waiting for a connection to send number of time steps...")

    # Accept a connection
    connection, client_address = server_socket.accept()
    print("Connection from", client_address)

    tt_getting_data_client_bytes = connection.recv(8)
    tt_getting_data_client = struct.unpack('d', tt_getting_data_client_bytes)[0]

    tt_visualize_data_client_bytes = connection.recv(8)
    tt_visualize_data_client = struct.unpack('d', tt_visualize_data_client_bytes)[0]

    connection.close()  
    server_socket.close()
    print("Total time to create, send-receive and visualize ({}*{}) 2D array for {} time steps is {},{} and {} seconds.".format(NX, NY, numSteps, tt_create_data, tt_sending_data + tt_getting_data_client, tt_visualize_data_client))

    