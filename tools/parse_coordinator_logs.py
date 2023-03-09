import pathlib
import statistics
from datetime import datetime
import os
import matplotlib.pyplot as plt


BASE_PATH = r"C:\Users\lauri\Desktop\YO\hajajärjestelmät\DistributedSystems_project\node_1_sensors"




"""
How many measurements was sent for each receiver by the dummy sensor
"""
def get_num_measurements_per_receiver(file):
    p_o = pathlib.Path(file)
    num_sensors = int(p_o.stem.split("_")[0])
    print(f"\nNumber of measurements sent per receiver using {num_sensors} sensors/receivers")
    res = {}
    for i in range(num_sensors):
        res[f"Sensor-{i}"] = 0
    with open(p_o, "r") as f:
        for line in f.readlines():
            if "Sending dummy data as sensor" in line:
                sensor = line.split(" ")[-1].strip("\n")
                res[sensor] = res[sensor] + 1
    asd = sorted(res.items())
    print(res)
    times = res.values()
    print("Average measurements per receiver:", statistics.mean(times))
    return statistics.mean(times)


"""
How many measurements each receiver had in cache befor being able to dump them
"""
def get_cahce_len_statistics(file):
    p_o = pathlib.Path(file)
    num_sensors = int(p_o.stem.split("_")[0])
    print("\nCahce len statistics when using {num_sensors} sensors")
    res = {}
    for i in range(num_sensors):
        res[f"Thread-{i + 1}"] = []
    with open(p_o, "r") as f:
        cont = f.readlines()
    i = 0
    counting = False
    count = 0
    thread = None
    for i in range(len(cont)):
        if "Dumping cache" in cont[i]:
            counting = True
            thread = cont[i].split(" ")[0]
        if "db_access_event returned" in cont[i]:
            tmp = res[thread]
            tmp.append(count)
            res[thread] = tmp
            counting = False
            count = 0
            thread = None
        if counting and thread and "Dumping item from cache" in cont[i]:
            count += 1
        i += 1
    print("Items dumped to db by each thread", res)

    all_amounts = []
    for key, value in res.items():
        for item in value:
            all_amounts.append(item)
    print("Average:", statistics.mean(all_amounts))
    print("Median:", statistics.median(all_amounts))
    return statistics.mean(all_amounts), statistics.median(all_amounts)


"""
How long did it take from giving token to getting it back
"""
def get_token_wait_time_statistics(file):
    p_o = pathlib.Path(file)
    num_sensors = int(p_o.stem.split("_")[0])
    print(f"\nToken wait time statistics using {num_sensors} sensors")
    res = []
    with open(p_o, "r") as f:
        send_timestamp, recv_timestamp = None, None
        for line in f.readlines():
            if "Setting db_access_event" in line:
                send_timestamp = line.split(" - ")[1].split(": ")[0]
            if "db_access_event returned from" in line:
                recv_timestamp = line.split(" - ")[1].split(": ")[0]
            if send_timestamp and recv_timestamp:
                s_t = datetime.strptime(send_timestamp, "%Y-%m-%d %H:%M:%S,%f")
                r_t = datetime.strptime(recv_timestamp, "%Y-%m-%d %H:%M:%S,%f")
                diff = r_t - s_t
                res.append(diff.total_seconds())
                send_timestamp, recv_timestamp = None, None
        print(res)
        print("Average:", statistics.mean(res))
        print("Median:", statistics.median(res))
        return statistics.mean(res), statistics.median(res)


"""
How often did server get to update its statistics, goal is 5s
(time it takes for it to update is not of intereset since it will always take last 1000 records
which will take approximately the same time every time)
"""
def server_cache_update_statistics(file):
    p_o = pathlib.Path(file)
    num_sensors = int(p_o.stem.split("_")[0])
    print(f"\nHow often servers cahce was updated using {num_sensors} sensors")
    update_times = []
    with open(p_o, "r") as f:
        for line in f.readlines():
            if "Giving token to flask server" in line:
                update_times.append(datetime.strptime(line.split(" - ")[1].split(": ")[0], "%Y-%m-%d %H:%M:%S,%f"))
    diffs = []
    for i in range(len(update_times) - 1):
        time_1 = update_times[i]
        time_2 = update_times[i+1]
        diff = time_2 - time_1
        diffs.append(diff.total_seconds())
    print("Times updated:", len(update_times))
    print("Average time between update:", statistics.mean(diffs))
    print("Median time between update:", statistics.median(diffs))
    return len(update_times), statistics.mean(diffs), statistics.median(diffs)



if __name__ == "__main__":
    paths = []
    #This is very messy but get logs in order of receiver amount:
    i = 1
    while i <= 20:
        for file in os.listdir(BASE_PATH):
            if file.endswith(".log") and file.startswith(f"{i}_coordinator"):
                path = BASE_PATH + "\\" + file
                paths.append(path)
                break
        i += 1

    meas_per_sensor = {}
    cache_len_statistics = {}
    token_wait_statistics = {}
    server_update_statistics = {}
    i = 1
    for path in paths:
        avg_measurements_per_sensor = get_num_measurements_per_receiver(path)
        meas_per_sensor[i] = avg_measurements_per_sensor 
        average, median = get_cahce_len_statistics(path)
        cache_len_statistics[i] = (average, median)
        average, median = get_token_wait_time_statistics(path)
        token_wait_statistics[i] = (average, median)
        num, average, median = server_cache_update_statistics(path)
        server_update_statistics[i] = (num, average, median)
        i += 1
    
    #Plot measurement statistics
    plt.plot(meas_per_sensor.keys(), meas_per_sensor.values(), label="Num measurements/receiver")
    plt.xticks(list(meas_per_sensor.keys()))
    plt.xlabel("Number of sensors/receivers")
    plt.ylabel("Number of measurements per receiver")
    plt.legend(loc=1)
    plt.show()

    #Plot cahce length statistics
    y_avg = []
    y_median = []
    for y in cache_len_statistics.values():
        y_avg.append(y[0])
        y_median.append(y[1])
    plt.plot(cache_len_statistics.keys(), y_avg, label="Average")
    plt.plot(cache_len_statistics.keys(), y_median, label="Median")
    plt.xticks(list(meas_per_sensor.keys()))
    plt.xlabel("Number of sensors/receivers")
    plt.ylabel("Cache length on dump")
    plt.legend(loc=2)
    plt.show()

    #Plot token wait statistics
    y_avg = []
    y_median = []
    for y in token_wait_statistics.values():
        y_avg.append(y[0])
        y_median.append(y[1])
    plt.plot(cache_len_statistics.keys(), y_avg, label="Average")
    plt.plot(cache_len_statistics.keys(), y_median, label="Median")
    plt.xticks(list(meas_per_sensor.keys()))
    plt.xlabel("Number of sensors/receivers")
    plt.ylabel("Time spent waiting for token")
    plt.legend(loc=2)
    plt.show()

    #Plot server statistics
    y_num = []
    y_avg = []
    y_median = []
    for y in server_update_statistics.values():
        y_num.append(y[0])
        y_avg.append(y[1])
        y_median.append(y[2])
    plt.plot(cache_len_statistics.keys(), y_avg, label="Average")
    plt.plot(cache_len_statistics.keys(), y_median, label="Median")
    plt.plot(cache_len_statistics.keys(), y_num, label="Update times in 30s")
    plt.xticks(list(meas_per_sensor.keys()))
    plt.xlabel("Number of sensors/receivers")
    plt.ylabel("Time spent waiting for token")
    plt.legend(loc=2)
    plt.show()