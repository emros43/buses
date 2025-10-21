""" Collects global_data.MINUTES of current bus positions. """

import argparse
import datetime
import json
import os
import requests
import time

import config
import global_data

RIGHT_NOW = -1

def fetch_bus_positions(start_time):
    """ Returns string of data about all buses active right now, filtering out entries
    older than start_time. """

    url = (global_data.ZMT_API_URL +
           "busestrams_get?type=1&resource_id=f2e5503e927d-4ad3-9500-4ab9e55deb59&apikey=" +
           config.API_KEY)
    timeout_duration = 5  # seconds

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

def collect_data(start_hour=RIGHT_NOW, start_minute=RIGHT_NOW):
    """ Collects data about current buses for global_data.MINUTES, beginning at the given hour
    and minute, into global_data.MINUTES files in directory
    global_data.DATA_DIR/year-month-day_hour:minute:second. """

    print("Setting up the download...")

    start_time = datetime.datetime.now()
    current_time = datetime.datetime.now()
    interval_seconds = 60

    if start_hour != RIGHT_NOW:
        target_time = start_time.replace(hour=start_hour, minute=start_minute, second=0, microsecond=0)
        if target_time < start_time:  # force next 24h
            target_time += datetime.timedelta(days=1)
        start_time = target_time

        if current_time < start_time:
            print(f"Waiting for start time {start_time}...", end="", flush=True)
            while current_time < start_time:
                time.sleep(interval_seconds)
                current_time = datetime.datetime.now()
                print(".", end="", flush=True)
            print()

    new_data_dir = os.path.join(global_data.DATA_DIR, current_time.strftime('%Y-%m-%d_%H-%M-%S'))
    if not os.path.exists(new_data_dir):
        os.makedirs(new_data_dir)

    print(f"Starting download in {new_data_dir}; ends in {global_data.MINUTES} minutes.")

    for i in range(global_data.MINUTES):
        current_time = datetime.datetime.now()
        file_name = os.path.join(new_data_dir, f"{current_time.strftime('%H-%M-%S')}.txt")

        for _ in range(3):  # max 3 tries to get this minute's data
            records = fetch_bus_positions(start_time)
            if records:
                with open(file_name, "w") as f:
                    json.dump(records, f, ensure_ascii=False, indent=4)
                print(f"File created: {current_time.strftime('%H:%M:%S')}")
                break
            time.sleep(1)  # retry in a second
            print(f"Request failed: {current_time.strftime('%H:%M:%S')}")

        if i != global_data.MINUTES - 1:
            time.sleep(interval_seconds)

    print("Downloading ended.")

####################################################################################################

if __name__ == "__main__":
    start_hour = RIGHT_NOW
    start_minute = RIGHT_NOW

    parser = argparse.ArgumentParser(
        description=f"Collect live bus positions."
    )

    def hour_minute(datestr):
        return datetime.datetime.strptime(datestr, '%H:%M').time()
    def minutes(i):
        try:
            i = int(i)
            if i <= 1:
                raise argparse.ArgumentTypeError(f"{i} is not an integer of 2 or higher")
        except ValueError:
            raise Exception(f"{i} is not an integer")
        return i
    
    parser.add_argument("-t", "--time", type=hour_minute, nargs='?',
                        help="Scheduled start time in HH:MM (24-hour format) within the next 24 hours (default now)")
    parser.add_argument("-m", "--minutes", type=minutes, nargs='?',
                        help="Number of minutes to collect data. Must be an integer of at least 2 to collect any changes in bus positions (default 60)")

    args = parser.parse_args()
    if args.time:
        start_hour = args.time.hour
        start_minute = args.time.minute
    if args.minutes:
        global_data.MINUTES = args.minutes
    
    collect_data(start_hour, start_minute)
