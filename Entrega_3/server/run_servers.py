#!/usr/bin/python3
import os
import sys 

try:
    PORT = 50050
    try:
            N_nodes = int(sys.argv[1])
            N_replicas = int(sys.argv[2])
    except:
            N_nodes = 3
            N_replicas = 3
            
    print(f"Total Servers {N_nodes * N_replicas}")
    for i in range(N_nodes * N_replicas):
            print(f"PORT: {PORT}")
            build_x = f'docker build -t neonat_{i} .'
            run_x = f'docker run -d -p {PORT}:{PORT} -e "SERVER_PORT={PORT}" --network="host" neonat_{i}'
            print(f"Running: {build_x}")
            os.system(build_x)
            print(f"Running: {run_x}")
            os.system(run_x)
            PORT += 1
except Exception as e:
    print(f'{e}')
