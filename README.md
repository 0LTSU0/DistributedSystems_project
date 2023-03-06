# DistributedSystems_project

Project for course 521290S Distributed systems

# Usage (docker)
## Node 1 (sensors and kafka)
1. Set desired args in node_1_sensors/Dockerfile (NOTE: max number of threads is 20 as only that many ports are allocated later)
2. Build docker image for node1: /DistributedSystems_project/node_1_sensors: <sub>docker build -t node_1 .</sub>
3. Set database path to docker-compose.yml
4. Run <sub>docker-compose up</sub>

## Node 2 (web server)
1. Build docker image for node2: /DistributedSystems_project/node_2_server: <sub>docker build -t node_2 .</sub>
2. <sub>docker run -p 5000:5000 --volume /home/ltsu/Desktop/_proj/DistributedSystems_project/node_1_sensors/db:/data node_2</sub>

## Node 3 (client)
1. Build docker image for node3: <sub>docker build -t node_3 .</sub>
2. <sub>docker run --network host --env="DISPLAY" --user=$(id -u) node_3</sub>


# Usage (locally)
1. If kafka mode is desired run kafka server:
    - C:\kafka>.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
    - C:\kafka>.\bin\windows\kafka-server-start.bat .\config\server.properties
2. Run coordinator.py (mode="socket"/"kafka")
3. Run flask_server.py
4. Run data_visualizer.py
