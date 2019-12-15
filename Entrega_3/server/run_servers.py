#!/usr/bin/python3
import os
import sys 


PORT = 50050
try:
        N_nodes = int(sys.argv[1])
        N_replicas = int(sys.argv[2])
except:
        N_nodes = 3
        N_replicas = 3
        
print(f"Number of servers: {N_nodes}\nNumber of replicas: {N_replicas}\nTotal of servers running: {N_nodes * N_replicas}\n")
print('Cleaning all containers')
os.system('docker rm -f $(docker ps -a -q)')

for i in range(N_nodes * N_replicas):
        #Command to build container
        build_neonat_container = f'docker build -t neonat_{i} .'

        #Command to run container
        run_neonat_container = f'docker run -d -p {PORT}:{PORT} -e "SERVER_PORT={PORT}" --network="host" neonat_{i}'
        print(f"Running: {build_neonat_container}")
        #Exec command to build container
        os.system(build_neonat_container)

        print(f"Running: {run_neonat_container}")
        #Exec command to run container
        os.system(run_neonat_container)
        PORT += 1
