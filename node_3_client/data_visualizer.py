from urllib.request import urlopen
import logging
import json
import matplotlib.pyplot as plt
import platform
from datetime import datetime


SEVER_URL = "http://127.0.0.1:5000/get_measurements/"
start_time = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
if platform.platform() == "Linux":
    logging.basicConfig(level=logging.INFO, format="%(threadName)s - %(asctime)s: %(message)s", 
        handlers=[logging.FileHandler(f"/data/data_visualizer_{start_time}.log"), logging.StreamHandler()])
else:
    logging.basicConfig(level=logging.INFO, format="%(threadName)s - %(asctime)s: %(message)s", 
        handlers=[logging.FileHandler(f"data_visualizer_{start_time}.log"), logging.StreamHandler()])

# Draw plot
def draw_plot():
    measurements = get_meas(60)
    data = prepare_data(measurements)

    if data == {}:
        logging.warn("Server gave empty response -> can't plot")
        exit()
    else:
        logging.info(f"Got data from server containing {len(data)} sensors")
    
    i = 0
    fig, ax1 = plt.subplots(len(data), 1)
    
    for sensor in data:
        #plt.xticks(np.arange(0, len(data["Sensor-0"].get("timestamps")) + 1, 5))
        ax1[i].plot(data[sensor].get("timestamps"), data[sensor].get("humidities"), label="humidity")
        ax1[i].plot(data[sensor].get("timestamps"), data[sensor].get("temps"), label="temperature")
        ax1[i].plot(data[sensor].get("timestamps"), data[sensor].get("batteries"), label="battery")
        ax1[i].legend(loc=2)
        #plt.setp( ax1[i].xaxis.get_majorticklabels(), rotation=20)
        ax2 = ax1[i].twinx()
        ax2.plot(data[sensor].get("timestamps"), data[sensor].get("pressures"), label="pressure", color="red")
        ax2.legend(loc=1)
        i += 1
        plt.gcf().autofmt_xdate()
    plt.show()
    pass



# Query measurements from flask server
def get_meas(amount):
    page = urlopen(SEVER_URL + str(amount))
    if page.code == 200:
        cont = json.loads(page.read().decode())
    return cont


# Make data into more easily plottable format
def prepare_data(data):
    res = {}
    for item in data.get("measurements"):
        if item[1] not in res.keys():
            res[item[1]] = {
                "humidities": [],
                "temps": [],
                "pressures": [],
                "batteries": [],
                "timestamps": []
            }
        res[item[1]]["humidities"].append(item[2])
        res[item[1]]["temps"].append(item[3])
        res[item[1]]["pressures"].append(item[4])
        res[item[1]]["batteries"].append(item[5])
        res[item[1]]["timestamps"].append(item[6])
    return res


if __name__ == "__main__":
    draw_plot()