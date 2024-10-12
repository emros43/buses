""" Collects hour of current bus positions. """

import os
import datetime
import time
import json
import requests
import global_data


def fetch_bus_positions(start_time):
    """Returns string of data about all buses active right now, filtering out entries
    older than start_time. """

    url = (global_data.URL + "busestrams_get?type=1&resource_id=f2e5503e927d-4ad3-9500"
                             "-4ab9e55deb59&apikey=") + global_data.API_KEY
    timeout_duration = 30
    try:
        response = requests.get(url, timeout=timeout_duration)

        if response.status_code == 200:
            data = response.json()
            if isinstance(data["result"], str):  # ignore api's connection errors
                print(f"Downloading error: {data['result']}")
                return None

            filtered_results = []
            curr_time_str = start_time.strftime("%Y-%m-%d %H:%M:%S")

            for item in data["result"]:
                if item["Time"] >= curr_time_str:
                    filtered_results.append(item)

            data["result"] = filtered_results
            return data

        print(f"Downloading error: {response.status_code}")
        return None
    except requests.Timeout:
        print(f"Request timed out after {timeout_duration} seconds.")
        return None
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def collect_hour_of_data(start_hour=-1, start_minute=0):
    """ Collects data about current buses for global.MINUTES, beginning at the given hour
    and minute, into global.MINUTES files in directory ./bus_data/new_data. """

    print("Setting up the download...")

    if start_hour == -1:
        start_hour = datetime.datetime.now().hour
        start_minute = datetime.datetime.now().minute

    start_time = datetime.datetime.now().replace(hour=start_hour, minute=start_minute, second=0)
    current_time = datetime.datetime.now()
    interval_seconds = 60

    if current_time < start_time:
        print(f"Time is {current_time.strftime('%H:%M:%S')}, "
              f"not yet {start_time.strftime('%H:%M:%S')}. Waiting for start time")
        while current_time < start_time:
            time.sleep(interval_seconds)
            current_time = datetime.datetime.now()
            print(". ", end="")

    new_data_dir = global_data.DATA_DIR + "new_data/"
    if not os.path.exists(new_data_dir):
        os.makedirs(new_data_dir)

    for _ in range(global_data.MINUTES):
        file_name = new_data_dir + f"bus_positions_{current_time.strftime('%H-%M-%S')}.txt"

        print(f"Downloading data - time: {current_time.strftime('%H:%M:%S')}")
        records = fetch_bus_positions(start_time)
        if records:
            with open(file_name, "w") as f:
                json.dump(records, f, ensure_ascii=False, indent=4)
        else:
            time.sleep(5)
            records = fetch_bus_positions(start_time)
            if records:
                with open(file_name, "w") as f:
                    json.dump(records, f, ensure_ascii=False, indent=4)
            else:
                time.sleep(5)
                records = fetch_bus_positions(start_time)
                if records:
                    with open(file_name, "w") as f:
                        json.dump(records, f, ensure_ascii=False, indent=4)
        time.sleep(interval_seconds)
        current_time = datetime.datetime.now()

    print("Downloading ended.")


####################################################################################################


collect_hour_of_data()
