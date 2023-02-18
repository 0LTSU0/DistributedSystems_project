import queue
import logging
import time
import threading
import socket
import json

# Receiver class for receiving dummy data from sensor_simulator.py
class dummyReceiver(threading.Thread):
    def __init__(self, threadnum, address, port):
        self.threadnum = threadnum
        self.address = address
        self.port = port
        self.cache = queue.Queue(100) #Receive max 100 measurements in between tokens
        self.database_access = False
        self.db_access_event = threading.Event()
        self.rcv_socket = None
        logging.basicConfig(level=logging.INFO, format="%(threadName)s - %(asctime)s: %(message)s")

        super(dummyReceiver,self).__init__()

    # when thrad.start() is called this is executed
    def run(self):
        self.main()


    # main data receiving loop
    def main(self):
        logging.info(f"Waiting for dummy sensor connection at {self.address}:{self.port}")
        self.rcv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.rcv_socket.bind((self.address, self.port))
        self.rcv_socket.listen()
        conn, addr = self.rcv_socket.accept()
        try:
            with conn:
                logging.info(f'Connected by {addr}')
                while True:
                    if self.db_access_event.is_set():
                        logging.info("Access to database is available!")
                        self.dump_cache()
                    self.rcv_socket.listen()
                    data = conn.recv(1024)
                    if data:
                        logging.info(f"Data received: {data.decode()}")
                        self.cache.put(json.loads(data.decode()))
        except Exception as e:
            logging.error(f"Error occurred {str(e)}")
            logging.info("Listening again on socket after 1s")
            self.rcv_socket.close()
            time.sleep(1)
            self.main()
    
    def test(self):
        while True:
            logging.info("testprint")
            time.sleep(0.5)


    def allow_database_access(self):
        logging.info(f"Database access granted for receiver {self.threadnum}")

    def deny_database_access(self):
        logging.info(f"Database access removed from receiver {self.threadnum}")
        self.database_access = False

    def dump_cache(self):
        logging.info(f"Dumping cache")
        while not self.cache.empty():
            item = self.cache.get()
            print("Item in queue:", item)

        self.db_access_event.clear()



# Receiver class for receiving data from real ruuviTags
class ruuvitagReceiver():
    def __init__(self, mac_addresses):
        self.ruuvtags = mac_addresses