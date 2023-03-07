from flask import Flask, request
import sqlite3
import os
import logging
import time
import json
import rsa
import platform
from datetime import datetime


if platform.system() == "Linux":
    DB_PATH = os.path.join("/data", "database.db")
else:
    DB_PATH = os.path.join(__file__, "../..", "db", "database.db")
app = Flask(__name__)
meas_cache = []
if platform.platform() == "Linux":
    start_time = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
    logging.basicConfig(level=logging.INFO, format="%(threadName)s - %(asctime)s: %(message)s", 
        handlers=[logging.FileHandler(f"/data/flask_server{start_time}.log"), logging.StreamHandler()])
else:
    logging.basicConfig(level=logging.INFO, format="%(threadName)s - %(asctime)s: %(message)s")
COORDINATOR_PUBLIC_KEY = None


@app.route("/get_measurements/<int:len_history>")
def get_measurements(len_history):
    ret_meas = {}
    ret_meas["measurements"] = meas_cache[:min(len(meas_cache), len_history)]
    return json.dumps(ret_meas)


#TODO: implement checking sender through key management
@app.route("/update_cache", methods=["POST"])
def update_cache():
    global meas_cache
    if verify_sender(request.headers):
        try:
            meas_cache = load_recent_records(500)
        except Exception as e:
            logging.error(f"Failed to update cache: {e}")
        return "Cache updated", 200
    
    return "Sender could not be verified to be expected coordinator", 404


def verify_sender(headers):
    logging.info("Verifying /update_cache command sender")
    global COORDINATOR_PUBLIC_KEY
    path = os.path.dirname(__file__)
    if not COORDINATOR_PUBLIC_KEY:
        with open(os.path.join(path, "public.pem"), "rb") as f:
            COORDINATOR_PUBLIC_KEY = rsa.PublicKey.load_pkcs1(f.read())
    msg = headers.environ["HTTP_MSG"]
    if "file" not in request.files:
        logging.info("Missing signature file")
        return False
    file = request.files["file"]
    filecont = file.read()
    
    try:
        rsa.verify(msg.encode(), filecont, COORDINATOR_PUBLIC_KEY)
        logging.info("/update_cache came from expeced coordinator")
        return True
    except rsa.VerificationError as e:
        logging.error(f"/update_cache sender verification failed {e}")
        return False



def load_recent_records(len_history):
    logging.info("Updating cache")
    db_conn = sqlite3.connect(DB_PATH)
    query = f"SELECT * FROM meas order by measurement_id desc limit {len_history}"
    cur = db_conn.cursor()
    measurements = cur.execute(query).fetchall()
    db_conn.close()
    return measurements



if __name__ == "__main__":
    while not os.path.exists(DB_PATH):
        logging.info("Waiting for databse to be created")
        time.sleep(1)
    #meas_cache = load_recent_records(500)
    if platform.system() == "Linux":
        app.run(debug=True, host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
    else:
        app.run(debug=True)
