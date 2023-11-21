#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <netcdf.h>
#include <mpi.h>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<unistd.h>
#include<arpa/inet.h>


#define NX 64
#define NY 64
#define DT 60.0 // Time step in seconds
#define DX 1000.0 // Spatial step in meters
#define U0 10.0 // Initial horizontal wind velocity (m/s)
#define V0 5.0 // Initial vertical wind velocity (m/s)
#define KX 0.00001 // Diffusion coefficient for X-direction
#define KY 0.00001 // Diffusion coefficient for Y-direction
#define KZ 0.00001 // Diffusion coefficient for Z-direction

void initializeField(double field[][NX][NY], int numSteps) {
    srand(time(NULL));
    for (int t = 0; t < numSteps; t++) {
        for (int i = 0; i < NX; i++) {
            for (int j = 0; j < NY; j++) {
                field[t][i][j] = rand() % 100;
            }
        }
    }
}

void simulateWeather(double field[][NX][NY], int rank, int num_processes, int numSteps) {
    double tempField[numSteps][NX][NY];

    if (rank == 0) {
         int server_socket = socket(AF_INET, SOCK_STREAM, 0);
            if (server_socket == -1) {
                perror("Socket creation failed");
                exit(EXIT_FAILURE);
            }
            printf("Socket Created\n");

            // Bind the socket to an address and port
            struct sockaddr_in server_address;
            server_address.sin_family = AF_INET;
            server_address.sin_port = htons(5566); // Replace with the desired port
            server_address.sin_addr.s_addr = inet_addr("127.0.0.1");

            if (bind(server_socket, (struct sockaddr*)&server_address, sizeof(server_address)) == -1) {
                perror("Bind failed");
                exit(EXIT_FAILURE);
            }
            printf("binded\n");

            // Listen for incoming connections
            if (listen(server_socket, 5) == -1) {
                perror("Listen failed");
                exit(EXIT_FAILURE);
            }
            printf("Listening\n");

            // Accept a client connection
            int client_socket = accept(server_socket, NULL, NULL);
            if (client_socket == -1) {
                perror("Accept failed");
                exit(EXIT_FAILURE);
            }
            printf("Connected\n");
    for (int t = 0; t < numSteps; t++) {
        // Advection
        for (int i = 0; i < NX; i++) {
            for (int j = 0; j < NY; j++) {
                int i_prev = ((int)(i - U0 * DT / DX + NX)) % NX;
                int j_prev = ((int)(j - V0 * DT / DX + NY)) % NY;
                tempField[t][i][j] = field[t][i_prev][j_prev];
            }
        }

        // Diffusion
        for (int i = 0; i < NX; i++) {
            for (int j = 0; j < NY; j++) {
                double laplacian = (field[t][(i + 1) % NX][j] + field[t][(i - 1 + NX) % NX][j]
                                    + field[t][i][(j + 1) % NY] + field[t][i][(j - 1 + NY) % NY]
                                    - 4 * field[t][i][j]) / (DX * DX);
                tempField[t][i][j] += (KX * laplacian + KY * laplacian) * DT;
            }
        }
        
        // printf("%f,%f,%f,%f\n",tempField[t][0][0],tempField[t][0][1],tempField[t][1][0],tempField[t][1][1]);
        // send(client_socket, tempField[t], sizeof(tempField[t]), 0);
        for (int i = 0; i < NX; i++) {
            for (int j = 0; j < NY; j++) {
                double double_value = tempField[t][i][j];

                // sending the length of the value first
                length_bytes = struct.pack('I', 8)
                client_socket.sendall(length_bytes)

                // sending the actual value next
                double_bytes = struct.pack('d', double_value)
                client_socket.sendall(double_bytes)

                // Send a chunk of data to the client
                // Send the double value                
                
                // send(client_socket, &value, sizeof(value), 0);
            }
        }
            
        // // Send a message to indicate that the data for the current time step has been sent
        // char message[] = "Data sent for current time-step";
        // send(client_socket, message, sizeof(message), 0);
        // // send(client_socket, &data, sizeof(data), 0);
        // // Send the length of the float in bytes (assuming 8 bytes for double)
        // int value_len = 8;  // Length of double in bytes
        // send(client_socket, &value_len, sizeof(value_len), 0);
        
        
    }
            // Move this outside the loop
            close(client_socket);
            close(server_socket);

            // Add a delay after sending the data for the current time step
            // to ensure the client has time to receive it before closing the connection
            sleep(1);

            // Add the following lines to wait for a response   
            // from the client before proceeding to the next time step
            // char response[1024];
            // recv(client_socket, response, sizeof(response), 0);
            // printf("Received response from client: %s\n", response);
}

int main(int argc, char **argv) {
    int rank, num_processes;
    int numSteps;

    if (argc != 2) {
        printf("Usage: %s <numSteps>\n", argv[0]);
        return 1;
    }

    numSteps = atoi(argv[1]);
    if (numSteps <= 0) {
        printf("numSteps must be a positive integer.\n");
        return 1;
    }

    double field[numSteps][NX][NY];

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &num_processes);

    if (NX % num_processes != 0) {
        if (rank == 0) {
            fprintf(stderr, "Number of processes must evenly divide NX.\n");
        }
        MPI_Finalize();
        return 1;
    }

    initializeField(field, numSteps); // Initialize the initial field for all time steps

    // Distribute the initial field to all processes
    MPI_Bcast(&field[0][0][0], numSteps * NX * NY, MPI_DOUBLE, 0, MPI_COMM_WORLD);

    simulateWeather(field, rank, num_processes, numSteps);

    printf("Weather simulation completed.\n");

    MPI_Finalize();
    return 0;
}
