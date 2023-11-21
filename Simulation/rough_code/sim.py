import socket
import struct
import time
from mpi4py import MPI
import os

NX = 64
NY = 64
DT = 60.0  # Time step in seconds
DX = 1000.0  # Spatial step in meters
U0 = 10.0  # Initial horizontal wind velocity (m/s)
V0 = 5.0  # Initial vertical wind velocity (m/s)
KX = 0.00001  # Diffusion coefficient for X-direction
KY = 0.00001  # Diffusion coefficient for Y-direction
KZ = 0.00001  # Diffusion coefficient for Z-direction


def initializeField(field, numSteps):
    for t in range(numSteps):
        for i in range(NX):
            for j in range(NY):
                field[t][i][j] = int.from_bytes(os.urandom(8), byteorder='big') % 100


def simulateWeather(field, rank, num_processes, numSteps):
    tempField = [[[0.0 for _ in range(NY)] for _ in range(NX)] for _ in range(numSteps)]

    if rank == 0:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('172.23.145.167', 5566)
        server_socket.bind(server_address)
        server_socket.listen(1)

        print("Socket Created")
        print("binded")
        print("Listening")

        client_socket, _ = server_socket.accept()
        print("Connected")

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

            for i in range(NX):
                for j in range(NY):
                    double_value = tempField[t][i][j]

                    # sending the length of the value first
                    length_bytes = struct.pack('I', 8)
                    client_socket.sendall(length_bytes)

                    # sending the actual value next
                    double_bytes = struct.pack('d', double_value)
                    client_socket.sendall(double_bytes)
            
            # Wait for a response from the client before proceeding to the next time step
            response = client_socket.recv(1024).decode('utf-8')
            print("Received response from client:", response)

        # Move this outside the loop
        client_socket.close()
        server_socket.close()



def main():
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    num_processes = comm.Get_size()

    numSteps = int(input("Enter the number of time steps: "))

    field = [[[0.0 for _ in range(NY)] for _ in range(NX)] for _ in range(numSteps)]

    if rank == 0:
        initializeField(field, numSteps)

    # Distribute the initial field to all processes
    field = comm.bcast(field, root=0)

    simulateWeather(field, rank, num_processes, numSteps)

    if rank == 0:
        print("Weather simulation completed.")


if __name__ == "__main__":
    main()
