import threading
import logging
import socket
import random
import time
import json
import datetime
from kafka import KafkaProducer

# For use with kafka
class dummySensor_kafka(threading.Thread):
    def __init__(self, num_rcvs, kafka_server):
        super(dummySensor_kafka,self).__init__()
        self.rcvs = num_rcvs
        self.kafka_addr = kafka_server
        self.producer = KafkaProducer(bootstrap_servers=self.kafka_addr)

    def run(self):
        self.main()

    def main(self):
        while True:
            sensor_num = random.randrange(0, self.rcvs)
            meas_to_send = create_dummy_meas(sensor_num)
            meas_to_send_str = json.dumps(meas_to_send)
            topic = meas_to_send["sensor"]
            logging.debug(f"sending {meas_to_send_str} as sensor {topic}")
            logging.info(f"Sending dummy data as sensor {topic}")
            self.producer.send(topic, meas_to_send_str.encode())
            self.producer.flush()
            time.sleep(random.uniform(0.01, 0.1)) #sleep a little


# For use with socket connections
class dummySensor_socket(threading.Thread):
    def __init__(self, start_port, num_rcvs, address):
        super(dummySensor_socket,self).__init__()
        self.rcvs = num_rcvs
        self.sport = start_port
        self.rcv_address = address
        self.connections = []
        #logging.basicConfig(level=logging.INFO, format="%(threadName)s - %(asctime)s: %(message)s")

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
            meas_to_send = create_dummy_meas(conn_num)
            sock = self.connections[conn_num]
            packet = json.dumps(meas_to_send)
            logging.debug(f"sending {packet} to connection {conn_num}")
            logging.info(f"Sending dummy data to conn num {conn_num}")
            sock.sendall(packet.encode())
            time.sleep(random.uniform(0.01, 0.1)) #sleep a little to prevent random socket errors


#Create dummy dataentry that has same value that would come out of ruuvitag
def create_dummy_meas(sensor_idx):
    meas = {}
    meas["sensor"] = f"Sensor-{sensor_idx}"
    meas["humidity"] = random.uniform(0, 100)
    meas["temperature"] = random.uniform(-20, 50)
    meas["pressure"] = random.uniform(0, 2000)
    meas["battery"] = random.uniform(0, 100)
    meas["timestamp"] = datetime.datetime.isoformat(datetime.datetime.now())
    logging.debug(f"Created dummy measurement: {meas}")
    return meas
