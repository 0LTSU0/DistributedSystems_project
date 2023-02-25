# DistributedSystems_project

Project for course 521290S Distributed systems

## Usage
1. If kafka mode is desired run kafka server:
    - C:\kafka>.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties
    - C:\kafka>.\bin\windows\kafka-server-start.bat .\config\server.properties
2. Run coordinator.py (mode="socket"/"kafka")
3. Run flask_server.py
4. Run data_visualizer.py