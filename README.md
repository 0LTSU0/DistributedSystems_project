# DistributedSystems_project

Project for course 521290S Distributed systems

# Usage (docker)
## Node 1
1. Set desired args in node_1_sensors/Dockerfile (NOTE: max number of threads is 20 as only that many ports are allocated later)
2. Build docker image for node1: /DistributedSystems_project/node_1_sensors$: docker build -t node_1 .
3. Set database path to docker-compose.yml
4. Run docker-compose up


# Usage (locally)
1. If kafka mode is desired run kafka server:
    - C:\kafka>.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
    - C:\kafka>.\bin\windows\kafka-server-start.bat .\config\server.properties
2. Run coordinator.py (mode="socket"/"kafka")
3. Run flask_server.py
4. Run data_visualizer.py
