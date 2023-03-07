import threading
import argparse
from sensor_receiver import dummyReceiver_socket, dummyReceiver_kafka
from dummy_sensor import dummySensor_socket, dummySensor_kafka
import time
import logging
import sqlite3
import os
import rsa
import requests
import tempfile
import kafka
import platform
from datetime import datetime


START_PORT = 12345
if platform.platform() == "Linux":
    start_time = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
    logging.basicConfig(level=logging.INFO, format="%(threadName)s - %(asctime)s: %(message)s", 
        handlers=[logging.FileHandler(f"/data/data_visualizer{start_time}.log"), logging.StreamHandler()])
else:
    logging.basicConfig(level=logging.INFO, format="%(threadName)s - %(asctime)s: %(message)s")
if platform.system() == "Linux":
    DB_PATH = os.path.join("/data", "database.db")
else:
    DB_PATH = os.path.join(__file__, "../..", "db", "database.db")
SERVER_CACHE_UPDATE_URL = "http://127.0.0.1:5000/update_cache"
PRIVATE_KEY, PUBLIC_KEY = None, None
KAFKA_SERVER = "localhost:9092"

def main(rcvs, mode, timeout=None):
    rcv_threads = []
    
    #Start dummy receivers that are listening to socket connection from dummy sensors
    #and dummy sensors that send data over sockets to the receivers
    if mode == "socket":
        # Create dummy receiver instances
        for i in range(rcvs):
            t = dummyReceiver_socket(i, "127.0.0.1", START_PORT + i, DB_PATH)
            if timeout: #If timeout, make threads die when finished
                t.daemon = True
            rcv_threads.append(t)

        # Start dummy receivers
        for t in rcv_threads:
            t.start()

        # Start "dummy sensor"
        t = dummySensor_socket(START_PORT, rcvs, "127.0.0.1")
        if timeout: #If timeout, make threads die when finished
            t.daemon = True
        t.start()
    
    #Start dummy receivers listening to data from kafka server
    #and start dummy sensors that send messages to the kafka server.
    #The kafka topics will correspond to separate sensors in the format of topic=Sensor-X
    elif mode == "kafka":
        #Create dummy receiver instances (create one for each sensor to make sure token has many places to be at)
        for i in range(rcvs):
            topics = [f"Sensor-{i}"]
            t = dummyReceiver_kafka(topics, DB_PATH)
            if timeout:
                t.daemon = True
            rcv_threads.append(t)
        
        # Start dummy receivers
        for t in rcv_threads:
            t.start()

        # Start dummy sensor(s)
        t = dummySensor_kafka(rcvs, KAFKA_SERVER)
        if timeout:
            t.daemon = True
        t.start()

    st = time.time()

    server_update_time = time.time()
    tokenholder = 0
    while True:
        if timeout:
            if time.time() - st > timeout:
                logging.info("Timeout reached")
                break

        if tokenholder == rcvs:
            tokenholder = 0
        
        if len(rcv_threads) > 0:
            rcv_thread = rcv_threads[tokenholder]
            logging.info(f"Setting db_access_event for {tokenholder}")
            rcv_thread.db_access_event.set()
            while rcv_thread.db_access_event.is_set(): #Wait for thread to say its ready
                time.sleep(0.1)
            logging.info(f"db_access_event returned from {tokenholder}")
            tokenholder += 1

        #give token to server every 5 seconds
        if time.time() - server_update_time > 5:
            logging.info("Giving token to flask server")
            token_to_server()
            server_update_time = time.time()

    print("kill everything")
    exit(0)


# Read public/private keys to global variables
def read_keypair():
    path = os.path.dirname(__file__)
    print(path)
    global PUBLIC_KEY, PRIVATE_KEY
    try:
        with open(os.path.join(path, "public.pem"), "rb") as f:
            PUBLIC_KEY = rsa.PublicKey.load_pkcs1(f.read())
        with open(os.path.join(path, "private.pem"), "rb") as f:
            PRIVATE_KEY = rsa.PrivateKey.load_pkcs1(f.read())
    except Exception as e:
        logging.fatal(f"Error reading keypair: {e}")
        exit(-1)


# Send signed message about db access to flask server
def token_to_server():
    if not PRIVATE_KEY and not PUBLIC_KEY:
        read_keypair()
    
    #Sending rsa signature over http requst seems to be inconveninat ->
    #make it into file and send it to keep formatting correct and rsa library happy
    msg = "db access granted"
    signature = rsa.sign(msg.encode(), PRIVATE_KEY, "SHA-256")
    sfile = tempfile.TemporaryFile()
    sfile.write(signature)
    sfile.seek(0)
    files={"file": sfile}
    try:
        response = requests.post(SERVER_CACHE_UPDATE_URL, files=files, headers={"msg": msg})
        if response.status_code == 200:
            logging.info("Server updated cache succesfully")
        else:
            logging.error(f"Server returned wrong code {response.status_code}: {response.text}")
    except requests.exceptions.ConnectionError:
        logging.error("Could not connect to flask server")
    sfile.close()


# Init database with correct table format
def create_db(path):
    print(path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    #Require all actual measurements but not battery level
    cur.execute("""CREATE TABLE meas(measurement_id INTEGER PRIMARY KEY,
                                    sensor VARCHAR(100) NOT NULL,
                                    humidity REAL NOT NULL,
                                    temperature REAL NOT NULL, 
                                    pressure REAL NOT NULL, 
                                    battery REAL, 
                                    timestamp DATETIME NOT NULL)""")
    conn.commit()
    if platform.system() == "Linux":
        os.chmod(path, 0o0777) #Must give premissions or other processes can't access


# usage: "python coordinator.py --rcv_threads X --mode socket/kafka"
if __name__ == "__main__":
    #for debuging purposes delete database on launch
    try:
        os.remove(DB_PATH)
        logging.info(f"db deleted")
    except Exception as e:
        logging.error(f"error occurred: {str(e)}")
    
    if not os.path.exists(DB_PATH):
        create_db(DB_PATH)

    argparser = argparse.ArgumentParser()
    argparser.add_argument("--rcv_threads")
    argparser.add_argument("--mode")
    argparser.add_argument("--timeout")
    args = argparser.parse_args()
    
    if not args.rcv_threads and args.mode:
        print("usage: 'python coordinator.py --rcv_threads X --mode socket/kafka (--timeout X)'")
        exit(-1)

    if args.mode == "kafka":
        # Wait until kafka is running
        while True:
            try:
                consumer = kafka.KafkaConsumer(group_id='test', bootstrap_servers=['localhost:9092'])
                break # connection was succesfull
            except Exception as e:
                print("Kafka not running")
                time.sleep(1)

    if args.timeout:
        main(int(args.rcv_threads), args.mode, timeout=int(args.timeout))
    
    main(int(args.rcv_threads), args.mode)
