# Streaming Data Visualization 

Scientists and researchers across diverse fields rely on visualization techniques to analyze simulation data. How-
ever, this endeavor often proves cumbersome due to the resource-intensive nature of simulations, demanding high
computational power typically found in supercomputer. Unfortunately, access to supercomputers and other re-
sources is not consistently available. To address this challenge, there emerged a pressing need for a solution that
allows simulations to run on computers with high computational power while enabling scientists and researchers to
visualize the results conveniently on any computer, irrespective of its computational capabilities. This project aims
to bridge this gap by developing an efficient streaming data visualization system that accommodates large-scale
simulations, providing a flexible and accessible platform for data analysis and interpretation

## Our Approach
We have a weather simulation for multiple time steps running on a server (Simulation server) which generates data which can be visualized for further analysis after saving it as a file.

Instead of writing the simulation data on a file, we streamed the data from a simulation server to a server for visualization (Visualization server) using TCP/IP protocol.
The visualization cluster receives the data and visualizes it using VTK.
 
This is done for multiple time steps specified by the user.


## Running the Code

To run the code we first need to download and install the following dependencies:

Simulation Server:

1. MPICH: Link-https://www.mpich.org/downloads/
2. mpi4py: pip install mpi4py
3. NumPy: pip install numpy
4. Time: pip install time
5. Socket: pip install socket

Visualization Server:

1. VTK: pip install vtk
2. NumPy: pip install numpy
3. Socket: pip install socket
4. Time: pip install time

### Running Simulation:

Open the folder Single Socket Approach for using single socket connection for the streaming or open the folder Multiple Socket Approach for using multiple socket connections (one for each time step) for the streaming.

1. We first run the file SimulationServer.py using the following commands: 'python SimulationServer.py' on the simulation server.

2. Now we need to specify the grid width and height.

3. Now we need to specify the simulation servers IP address and port number
4. Now specify the number of time steps.

5. Now the simulation server will enter listen mode.

6. We now run file VisualizationServer.py using the following commands: 'VisualizationServer.py' on the Visualization server.
7. Now we need to specify the simulation servers IP address and port number.
9. Now a window will open on visualization server and the visualization run on this window.
10. When the visualisation ends, we can view the images for each time step in the same folder as VisualizationServer.py
