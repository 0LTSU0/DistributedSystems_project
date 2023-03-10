# DistributedSystems_project

Project for course 521290S Distributed systems. This project demonstrates an IoT system in which the first node consists of receveires for sensor data (in this case the physical sensors are replaced by a script which sends randomly generated measuremnets through Apache Kafka), second node consists of a web server which can be used to attach these measurements in database and a third node whose purpose is to serve as a very rudimentary client for utilizing the web server. The DS topics demonstrated are *coordination* (through circulating database access token between receivers and web server) and *secure key management* (web server lives in a separate container -> token is sent to it through http request but the message is signed by the coordinator hence making sure that the permission to databae is indeed valid).

Note: in the coordinator.py you can see that there are two operation modes available --mode=kafka/socket. The mode that should be used for evaluation is kafka as the socket mode was mainly implemented to make testing possible without having kafka running but that mode is not guaranteed to work correctly anymore.

# Environment and prerequisites
This project has been tested to work correctly with the following setup:
- Ubuntu 18.04 LTS
- docker 20.10.12
- docker-compose 1.17.1

Before starting setup, make sure you have an empty folder created somewhere which you can mount to docker containers (database and logs will be created here). This folder will be mounted to the containers as /data/ and thus **THIS PROJECT WILL ONLY WORK ON LINUX!!!!**

# Usage (docker, Linux)
## Node 1 (sensors and kafka)
1. Set desired args for coordinator.py in node_1_sensors/Dockerfile (NOTE: max number of receivers is 20)
2. Build docker image for node1: /DistributedSystems_project/node_1_sensors: `docker build -t node_1 .`
3. Set path to fore-mentioned empty folder to docker-compose.yml
4. Run `docker-compose up` (prefarebly after web server is running)

## Node 2 (web server)
1. Build docker image for node2: /DistributedSystems_project/node_2_server: `docker build -t node_2 .`
2. `docker run -p 5000:5000 --volume /home/ltsu/Desktop/ds_proj2/DistributedSystems_project/node_1_sensors/db:/data node_2` **NOTE: replace path with the same path you used in Node 1**

## Node 3 (client)
1. Build docker image for node3: `docker build -t node_3 .`
2. `docker run --network host --env="DISPLAY" --user=$(id -u) --volume /home/ltsu/Deskt/ds_proj2/DistributedSystems_project/node_1_sensors/db:/data node_3` **NOTE: replace path with the same path you used in Node 1**


# Usage (locally, windows, do not use for evaluation)
1. If kafka mode is desired run kafka server:
    - C:\kafka>.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
    - C:\kafka>.\bin\windows\kafka-server-start.bat .\config\server.properties
2. Run coordinator.py
3. Run flask_server.py
4. Run data_visualizer.py
