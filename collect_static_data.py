""" Collects bus lines, streets and bus stops. """

import os
import requests
import global_data


def download_to_file(url, file_name):
    """ Save data from url as json file with file_name. """
    timeout_duration = 30
    try:
        response = requests.get(url, params={"apikey": global_data.API_KEY},
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
    url = global_data.URL + "public_transport_routes/"
    file_name = global_data.DATA_DIR + "bus_lines.json"
    download_to_file(url, file_name)


def fetch_vocab_dictionary():
    """ Save streets as json file. """
    url = global_data.URL + "public_transport_dictionary/"
    file_name = global_data.DATA_DIR + "dictionary.json"
    download_to_file(url, file_name)


def fetch_bus_stops_today():
    """ Save bus stops as json file. """
    url = (global_data.URL + "dbstore_get?id=1c08a38c-ae09-46d2-8926-4f9d25cb0630&apikey="
           + global_data.API_KEY)
    file_name = global_data.DATA_DIR + "bus_stops.json"
    download_to_file(url, file_name)


def prepare_static_data():
    """ Prepare all static jsons. """
    if not os.path.exists(global_data.DATA_DIR):
        os.makedirs(global_data.DATA_DIR)
    fetch_vocab_dictionary()
    fetch_bus_lines()
    fetch_bus_stops_today()


####################################################################################################


prepare_static_data()
