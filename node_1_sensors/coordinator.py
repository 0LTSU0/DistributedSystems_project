import threading
import argparse
from sensor_receiver import dummyReceiver
from dummy_sensor import dummySensor
import time
import logging
import sqlite3
import os
import rsa
import requests
import tempfile


START_PORT = 12345
logging.basicConfig(level=logging.INFO, format="%(threadName)s - %(asctime)s: %(message)s")
DB_PATH = os.path.join(__file__, "../..", "db", "database.db")
SERVER_CACHE_UPDATE_URL = "http://127.0.0.1:5000/update_cache"
PRIVATE_KEY, PUBLIC_KEY = None, None

def main(rcvs, dummy_mode):
    rcv_threads = []
    
    if dummy_mode:
        # Create dummy receiver instances
        for i in range(rcvs):
            t = dummyReceiver(i, "127.0.0.1", START_PORT + i, DB_PATH)
            t.daemon = True
            rcv_threads.append(t)

        # Start dumym receivers
        for t in rcv_threads:
            t.start()

        # Start "dummy sensor"
        t = dummySensor(START_PORT, rcvs, "127.0.0.1")
        t.daemon = True
        t.start()

    st = time.time()
    runtime = 60

    server_update_time = time.time()
    tokenholder = 0
    while time.time() - st < 60:
        if tokenholder == rcvs:
            tokenholder = 0
        rcv_thread = rcv_threads[tokenholder]
        logging.info(f"Setting db_access_event for {tokenholder}")
        rcv_thread.db_access_event.set()
        while rcv_thread.db_access_event.is_set():
            time.sleep(0.1)
        logging.info(f"db_access_event returned from {tokenholder}")
        tokenholder += 1

        #give token to server every 5 seconds
        if time.time() - server_update_time > 5:
            logging.info("Giving token to flask server")
            token_to_server()
            server_update_time = time.time()

    #time.sleep(10)
    print("kill everything")
    exit(0)


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
    response = requests.post(SERVER_CACHE_UPDATE_URL, files=files, headers={"msg": msg})
    sfile.close()

    if response.status_code == 200:
        logging.info("Server updated cache succesfully")
    else:
        logging.error(f"Server returned wrong code {response.status_code}: {response.text}")


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

# usage: "python coordinator.py --rcv_threads X --use_dummy"
if __name__ == "__main__":
    #for debuging purposes delete database on launch
    try:
        os.remove(DB_PATH)
        logging.info(f"db deleted")
    except Exception as e:
        logging.error(f"error occurred: {str(e)}")
    
    if not os.path.exists(DB_PATH):
        create_db(DB_PATH)

    #token_to_server()
    main(5, True)


    #argparser = argparse.ArgumentParser()
    #argparser.add_argument("--rcv_threads")
    #argparser.add_argument("--use_dummy", action="store_true")
    #args = argparser.parse_args()
    #
    #if not args.rcv_threads:
    #    print("usage: 'python coordinator.py --rcv_threads X --use_dummy'")
    #    exit(-1)
    #
    #main(args.rcv_threads, args.use_dummy)