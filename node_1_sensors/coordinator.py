import threading
import argparse
from sensor_receiver import dummyReceiver
from dummy_sensor import dummySensor
import time
import logging
import sqlite3
import os
from urllib.request import urlopen


START_PORT = 12345
logging.basicConfig(level=logging.INFO, format="%(threadName)s - %(asctime)s: %(message)s")
DB_PATH = os.path.join(__file__, "../..", "db", "database.db")
SERVER_CACHE_UPDATE_URL = "http://127.0.0.1:5000/update_cache"

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


#TODO: implement secure key management
def token_to_server():
    page = urlopen(SERVER_CACHE_UPDATE_URL)
    if page.code == 200:
        logging.info("Server cache updated")
    else:
        logging.error(f"Server returned wrong code {page.code}")


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

    main(2, True)
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