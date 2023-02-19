from flask import Flask
import sqlite3
import os
import logging
import time
import json


DB_PATH = os.path.join(__file__, "../..", "db", "database.db")
app = Flask(__name__)
meas_cache = []
logging.basicConfig(level=logging.INFO, format="%(threadName)s - %(asctime)s: %(message)s")


@app.route("/get_measurements/<int:len_history>")
def get_measurements(len_history):
    ret_meas = {}
    ret_meas["measurements"] = meas_cache[:min(len(meas_cache), len_history)]
    return json.dumps(ret_meas)


#TODO: implement checking sender through key management
@app.route("/update_cache")
def update_cache():
    global meas_cache
    try:
        meas_cache = load_recent_records(500)
    except Exception as e:
        logging.error(f"Failed to update cache: {e}")
    return "Cache updated", 200


def load_recent_records(len_history):
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
    app.run(debug=True)
