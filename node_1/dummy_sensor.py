import threading
import logging
import socket
import random
import time
import json
import datetime

class dummySensor(threading.Thread):
    def __init__(self, start_port, num_rcvs, address):
        super(dummySensor,self).__init__()
        self.rcvs = num_rcvs
        self.sport = start_port
        self.rcv_address = address
        self.connections = []
        logging.basicConfig(level=logging.INFO, format="%(threadName)s - %(asctime)s: %(message)s")

    def run(self):
        self.main()

    def main(self):
        for i in range(self.rcvs):
            connport = self.sport + i
            logging.info(f"creating connection to {self.rcv_address}:{connport}")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((self.rcv_address, connport))
            self.connections.append(sock)
        
        # Send random data to random receivers
        while True:
            conn_num = random.randrange(0, self.rcvs)
            meas_to_send = self.create_dummy_meas(conn_num)
            sock = self.connections[conn_num]
            packet = json.dumps(meas_to_send)
            logging.info(f"sending {packet} to connection {conn_num}")
            sock.sendall(packet.encode())
            time.sleep(random.uniform(0.01, 0.1))

    def create_dummy_meas(self, sensor_idx):
        meas = {}
        meas["sensor"] = f"Sensor-{sensor_idx}"
        meas["humidity"] = random.uniform(0, 100)
        meas["temperature"] = random.uniform(-20, 50)
        meas["pressure"] = random.uniform(0, 2000)
        meas["battery"] = random.uniform(0, 100)
        meas["timestamp"] = datetime.datetime.isoformat(datetime.datetime.now())
        logging.info(f"Created dummy measurement: {meas}")
        return meas
