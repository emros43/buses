""" Class storing bus data and main analysis functions. """

import json
import os
import datetime
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import global_data


class BusData:
    """ Class storing bus data and main analysis functions. """

    def __init__(self, directory):
        """ Initialization of entire structure, including data processing. """

        self.minutes_data = {}  # {Brigade, Lat, Lines, Lon, Time, VehicleNumber}
        self.intervals_data = {}  # {speed, bus_stop, distance}
        self.bus_stops = {}  # {zespol, slupek, nazwa_zespolu, id_ulicy, szer_geo, dlug_geo,
        # kierunek, obowiazuje_od}
        self.streets = {}  # streets[id] = name
        self.speeding_moments = []  # {Brigade, Lat, Lines, Lon, Time, VehicleNumber, street_name}

        self.start_time = ""
        self.end_time = ""
        self.all_moments = 0  # only uncorrupted
        self.min_buses = 50000
        self.max_buses = 0

        self.load_static_data()
        self.load_real_time_moments(directory)
        self.fill_intervals()
        print("Preprocessing finished.\n")

    def __str__(self) -> str:
        """ Prints meta data about buses. """

        format_str = "%Y-%m-%d %H:%M:%S"
        dt1 = datetime.datetime.strptime(self.start_time, format_str)
        dt2 = datetime.datetime.strptime(self.end_time, format_str)
        return (
            f"Data for time from {dt1.strftime('%H:%M')} to {dt2.strftime('%H:%M')} "
            f"({self.min_buses}-{self.max_buses} buses were active)"
        )

    ################################################################################################

    def load_real_time_moments(self, directory):
        """ Reads a directory of previously downloaded files to minutes_data in json format.
            Saves first and last timestamp, and the total numbers of buses and moments. """

        files = sorted(os.listdir(directory))

        for i, file_name in enumerate(files):
            file_path = os.path.join(directory, file_name)

            with open(file_path, "r"):
                self.minutes_data[i] = pd.read_json(file_path)
                self.minutes_data[i] = pd.DataFrame(self.minutes_data[i]['result'].tolist())

                self.all_moments += len(self.minutes_data[i])
                self.max_buses = max(self.max_buses, len(self.minutes_data[i]))
                self.min_buses = min(self.min_buses,
                                     len(self.minutes_data[i]) if len(self.minutes_data[i]) > 0
                                     else self.min_buses)

        self.start_time = self.minutes_data[0]['Time'].min()
        self.end_time = self.minutes_data[len(files) - 1]['Time'].max()
        print("Real time moments loaded.")

    def load_static_data(self):
        """ Reads bus stops and city streets in json format. """

        bus_stops_path = os.path.join(global_data.DATA_DIR, "bus_stops.json")
        with open(bus_stops_path, "r") as file:
            bus_stops_data = json.load(file)
            self.bus_stops = pd.DataFrame(bus_stops_data['result'])
        print("Bus stops loaded.")

        streets_path = os.path.join(global_data.DATA_DIR, "dictionary.json")
        with open(streets_path, "r") as file:
            streets_data = json.load(file)
            self.streets = streets_data['result']['ulice']
        print("Streets loaded.")

    def fill_intervals(self):
        """ Calculates speeds of every bus between every position measurement. Updates all_moments
        to store the number of uncorrupted moments. """

        for i in range(len(self.minutes_data) - 1):
            if ('VehicleNumber' not in self.minutes_data[i].columns or 'VehicleNumber' not in
                    self.minutes_data[i + 1].columns):
                continue

            # remove rows where VehicleNumber is None (corrupted data)
            current_df = self.minutes_data[i].dropna(subset=['VehicleNumber'])
            next_df = self.minutes_data[i + 1].dropna(subset=['VehicleNumber'])
            if current_df.empty or next_df.empty:  # nothing to compare
                continue

            next_df = next_df.set_index('VehicleNumber')
            merged_df = current_df.merge(next_df[['Lat', 'Lon', 'Time']], left_on='VehicleNumber',
                                         right_index=True, suffixes=('', '_next'))

            merged_df['time_diff'] = global_data.time_difference_in_hours_vectorized(
                merged_df['Time'],
                merged_df['Time_next'])
            merged_df['distance'] = global_data.haversine_distance_vectorized(merged_df['Lat'],
                                                                              merged_df['Lon'],
                                                                              merged_df['Lat_next'],
                                                                              merged_df['Lon_next'])

            # calculate speed and filter out unrealistic (and corrupted) values
            merged_df['speed'] = np.where(merged_df['time_diff'] > 0, merged_df['distance']
                                          / merged_df['time_diff'], 0)
            valid_speed_mask = (merged_df['speed'] <= global_data.MAX_SPEED) & (
                    merged_df['speed'] >= global_data.MIN_SPEED)

            self.intervals_data[i] = merged_df[valid_speed_mask][['VehicleNumber', 'speed',
                                                                  'distance', 'time_diff']]

            speeding_moments_df = merged_df[merged_df['speed'] >= 50]
            self.speeding_moments.append(speeding_moments_df)

        valid_speed_count = 0
        for interval_df in self.intervals_data.values():
            valid_speeds = interval_df[(interval_df['speed'] <= global_data.MAX_SPEED) &
                                       (interval_df['speed'] >= global_data.MIN_SPEED)]
            valid_speed_count += len(valid_speeds)

        self.all_moments = valid_speed_count

    ################################################################################################

    def number_of_speeding_buses(self) -> int:
        """ Count unique buses that reached the speed of >= 50. """

        all_speeding_moments = pd.concat(self.speeding_moments, ignore_index=True)
        high_speed_vehicle_count = all_speeding_moments['VehicleNumber'].nunique()
        return high_speed_vehicle_count

    def report_speeds(self):
        """ Plots frequencies of speeds. Prints how many times someone was speeding. """

        all_intervals_df = pd.concat(self.intervals_data.values())
        speeds_series = all_intervals_df['speed']

        high_speed_count = (speeds_series >= 50).sum()

        max_speed = speeds_series.max()
        interval = 2
        colour = "yellow"
        bins = range(interval, min(int(max_speed) + 5, 100), interval)

        # histograms for slow and fast speeds
        plt.hist(speeds_series, bins=bins, edgecolor=colour, color="red", alpha=0.9)
        high_speeds_series = speeds_series[speeds_series >= 50]
        plt.hist(high_speeds_series, bins=bins, edgecolor="red", color=colour, alpha=0.9)

        plt.title("Speed Distribution of Vehicles Every Second")
        plt.xlabel(f"Speed (in intervals of {interval})")
        plt.ylabel("Number of Moments This Speed Was Average")

        stats = speeds_series.describe()
        plt.text(0.95, 0.95, stats.to_string(), fontsize=10,
                 verticalalignment="top", horizontalalignment="right",
                 transform=plt.gca().transAxes,
                 bbox={"facecolor": "white", "alpha": 0.5})

        plt.show()

        print(self)
        print(f"There were {self.number_of_speeding_buses()} buses that reached the average "
              f"speed of >= 50 kmph")
        print(f"{high_speed_count} is the number of times a speed of >= 50 was recorded "
              f"({colour} boxes on the graph), which is approx. "
              f"{round(high_speed_count / self.all_moments * 100, 3)}% of all moments "
              f"with uncorrupted data.")
        print(f"The results do not show speeds lower than {global_data.MIN_SPEED} "
              f"(corrupted data or buses standing still) or higher than {global_data.MAX_SPEED} "
              f"(corrupted data).")
        print()

    ################################################################################################

    def report_speeding_places(self):
        """ Prints out several streets on which drivers drove fastest. """

        speeding_df = self.speeding_moments
        bus_stops_df = self.bus_stops

        bus_stops_df["Lat"] = bus_stops_df["values"].apply(lambda x: float(x[4]["value"]))
        bus_stops_df["Lon"] = bus_stops_df["values"].apply(lambda x: float(x[5]["value"]))
        bus_stops_df["street_name"] = bus_stops_df["values"].apply(lambda x: x[3]["value"])
        speeding_df = pd.concat(speeding_df, ignore_index=True)

        def find_closest_bus_stop(row):
            distances = global_data.haversine_distance(row["Lat"], row["Lon"], bus_stops_df["Lat"],
                                                       bus_stops_df["Lon"])
            closest_index = distances.idxmin()
            return bus_stops_df.at[closest_index, "street_name"]

        speeding_df["closest_stop_id"] = speeding_df.apply(find_closest_bus_stop, axis=1)
        speeding_df["street_name"] = speeding_df["closest_stop_id"].map(self.streets)

        self.print_top_street_names(speeding_df, global_data.TOP_STREET_NUMBER)

    def print_top_street_names(self, speeding_df, number):
        """ Prints out provided names. """

        street_name_counts = Counter(speeding_df["street_name"])
        top_street_names = street_name_counts.most_common(number)

        print(f"Top {number} streets where a bus was going faster than 50 kmph:")
        for street_name, count in top_street_names:
            print(f"{street_name}: {count} times")
