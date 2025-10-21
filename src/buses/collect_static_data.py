""" Collects bus lines, streets and bus stops. """

import os
import requests

import global_data
import config

def download_to_file(url, file_name):
    """ Save data from url as json file with file_name. """
    timeout_duration = 30  # seconds
    try:
        response = requests.get(url, params={"apikey": config.API_KEY},
                                timeout=timeout_duration)

        if response.status_code == 200:
            data = response.text
            with open(file_name, "w") as f:
                f.write(data)

            print(f"Saved to file '{file_name}'.")
        else:
            print(f"No data downloaded: {response.status_code}")
    except requests.Timeout:
        print(f"Request timed out after {timeout_duration} seconds.")
    except requests.RequestException as e:
        print(f"An error occurred: {e}")

def fetch_bus_lines():
    """ Save bus lines as json file. """
    url = global_data.ZMT_API_URL + "public_transport_routes"
    file_name = os.path.join(global_data.DATA_DIR, "bus_lines.json")
    download_to_file(url, file_name)

def fetch_vocab_dictionary():
    """ Save streets as json file. """
    url = global_data.ZMT_API_URL + "public_transport_dictionary"
    file_name = os.path.join(global_data.DATA_DIR, "dictionary.json")
    download_to_file(url, file_name)

def fetch_bus_stops_today():
    """ Save bus stops as json file. """
    url = (global_data.ZMT_API_URL +
           "dbtimetable_get?id=ab75c33d-3a26-4342-b36a-6e5fef0a3ac3&apikey=" +
           config.API_KEY)
    file_name = os.path.join(global_data.DATA_DIR, "bus_stops.json")
    download_to_file(url, file_name)

####################################################################################################

if __name__ == "__main__":
    fetch_bus_lines()
    fetch_vocab_dictionary()
    fetch_bus_stops_today()
    print("Fetched bus lines, streets and bus stops.")
