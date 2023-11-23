import sys
import time
import numpy as np
from mpi4py import MPI
from netCDF4 import Dataset
import vtkmodules.all as vtk


# NX = 64
# NY = 64
DT = 60.0  # Time step in seconds
DX = 1000.0  # Spatial step in meters
U0 = 10.0  # Initial horizontal wind velocity (m/s)
V0 = 5.0  # Initial vertical wind velocity (m/s)
KX = 0.00001  # Diffusion coefficient for X-direction
KY = 0.00001  # Diffusion coefficient for Y-direction
KZ = 0.00001  # Diffusion coefficient for Z-direction

# aims to get total time for creating and broadcasting data for all timesteps specified
tt_creating_data = 0
tt_broadcasting_data = 0
t1 = 0


def initialize_field(num_steps, NX, NY):
    np.random.seed(0)  # Setting seed for reproducibility
    field = np.random.randint(0, 100, size=(num_steps, NX, NY))
    return field


def write_field_to_netcdf(field, num_steps, NX, NY):
    global tt_broadcasting_data, tt_creating_data
    begin = time.time()
    filename = "output.nc"
    with Dataset(filename, "w") as ncfile:
        ncfile.createDimension("time", num_steps)
        ncfile.createDimension("x", NX)
        ncfile.createDimension("y", NY)

        var = ncfile.createVariable("field", "f8", dimensions=("time", "x", "y"))
        var[:] = field

        # Add the times to the NetCDF file
        ncfile.createVariable("tt_creating_data", "f8").assignValue(tt_creating_data)
        end = time.time()

        tt_broadcasting_data = tt_broadcasting_data + end - begin
        ncfile.createVariable("tt_broadcasting_data", "f8").assignValue(tt_broadcasting_data)


def simulate_weather(field, num_steps, NX, NY):
    global tt_creating_data
    begin = time.time()
    temp_field = np.zeros_like(field)

    for t in range(num_steps):
        # Advection
        for i in range(NX):
            for j in range(NY):
                i_prev = (int(i - U0 * DT / DX + NX)) % NX
                j_prev = (int(j - V0 * DT / DX + NY)) % NY
                temp_field[t, i, j] = field[t, i_prev, j_prev]

        # Diffusion
        for i in range(NX):
            for j in range(NY):
                laplacian = (
                    (field[t, (i + 1) % NX, j] + field[t, (i - 1 + NX) % NX, j]
                     + field[t, i, (j + 1) % NY] + field[t, i, (j - 1 + NY) % NY]
                     - 4 * field[t, i, j]) / (DX * DX)
                )
                temp_field[t, i, j] += (KX * laplacian + KY * laplacian) * DT
    end = time.time()
    tt_creating_data = end - begin

    # Write the field and times to NetCDF
    write_field_to_netcdf(temp_field, num_steps, NX, NY)


def main():
    global tt_broadcasting_data

    num_steps = int(input("Enter the number of time steps: "))
    NX = int(input("Enter the value for NX: "))
    NY = int(input("Enter the value for NY: "))

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    num_processes = comm.Get_size()

    if num_steps <= 0:
        print("numSteps must be a positive integer.")
        sys.exit(1)

    if NX % num_processes != 0:
        if rank == 0:
            print("Number of processes must evenly divide NX.")
        sys.exit(1)

    if rank == 0:
        field = initialize_field(num_steps, NX, NY)
    else:
        field = np.empty((num_steps, NX, NY), dtype=np.float64)

    # begin = time.time()
    # Broadcast the initial field to all processes
    comm.Bcast(field, root=0)
    # end = time.time()
    # tt_broadcasting_data = end - begin
    
    # begin = time.time()
    simulate_weather(field, num_steps, NX, NY)
    # end = time.time()
    # tt_creating_data = end - begin

    if rank == 0:
        print("Weather simulation completed.")
        print("Total time taken to create and broadcast data for all {} time steps is {} and {} seconds".format(num_steps, tt_creating_data, tt_broadcasting_data))


if __name__ == "__main__":
    main()
