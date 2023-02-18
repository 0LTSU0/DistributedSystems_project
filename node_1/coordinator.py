import threading
import argparse
from sensor_receiver import dummyReceiver
from dummy_sensor import dummySensor
import time
import logging
import sqlite3
import os

START_PORT = 12345
logging.basicConfig(level=logging.INFO, format="%(threadName)s - %(asctime)s: %(message)s")

def main(rcvs, dummy_mode):
    rcv_threads = []
    
    if dummy_mode:
        # Create dummy receiver instances
        for i in range(rcvs):
            t = dummyReceiver(i, "127.0.0.1", START_PORT + i)
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
    tokenholder = 0
    while time.time() - st < 30:
        if tokenholder == rcvs:
            tokenholder = 0
        rcv_thread = rcv_threads[tokenholder]
        logging.info(f"Setting db_access_event for {tokenholder}")
        rcv_thread.db_access_event.set()
        while rcv_thread.db_access_event.is_set():
            time.sleep(0.1)
        logging.info(f"db_access_event returned from {tokenholder}")
        tokenholder += 1

    #time.sleep(10)
    print("kill everything")
    exit(0)

def create_db(path):
    print(path)
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE meas(sensor, humidity, temperature, pressure, battery, timestamp)")
    conn.commit()

# usage: "python coordinator.py --rcv_threads X --use_dummy"
if __name__ == "__main__":
    if not os.path.exists(os.path.join(__file__, "../..", "db", "database.db")):
        create_db(os.path.join(__file__, "../..", "db", "database.db"))

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