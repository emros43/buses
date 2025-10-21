""" Class storing bus data and main analysis functions. """

import json
import os
import datetime
from collections import Counter
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import folium
from itertools import cycle

import global_data

class BusData:
    def __init__(self, directory):
        """ Prepares intervals from directory for further analysis. """

        self.minutes_data = {}  # {Brigade, Lat, Lines, Lon, Time, VehicleNumber}
        self.intervals_data = {}  # {speed, bus_stop, distance} intervals[i] for minutes[i]-[i+1]
        self.bus_stops = {}  # {zespol, slupek, nazwa_zespolu, id_ulicy, szer_geo, dlug_geo,
        # kierunek, obowiazuje_od}
        self.streets = {}  # streets[id] = name

        self.speeding_moments = []  # {Brigade, Lat, Lines, Lon, Time, VehicleNumber, street_name}

        self.start_time = ""
        self.end_time = ""
        self.all_moments = 0  # only uncorrupted
        self.min_buses = 50000
        self.max_buses = 0

        data_name = os.path.basename(directory)
        self.output_dir = os.path.join(global_data.OUTPUT_DIR, f"{data_name}-{int(global_data.COMPARISON_SPEED)}-report")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        self.load_static_data()
        self.load_real_time_moments(directory)
        self.fill_intervals()
        # print("Preprocessing finished.\n")

    def __str__(self) -> str:
        """ Prints meta data about buses. """

        format_str = "%Y-%m-%d %H:%M:%S"
        dt1 = datetime.datetime.strptime(self.start_time, format_str)
        dt2 = datetime.datetime.strptime(self.end_time, format_str)
        day_of_week1 = dt1.strftime("%A")
        day_of_week2 = dt2.strftime("%A")
        info = f"({self.min_buses}-{self.max_buses} buses were active)."
        if day_of_week1 == day_of_week2:
            info = f"Data for {day_of_week1}, from {dt1.strftime('%H:%M')} to {dt2.strftime('%H:%M')} " + info
        else:
            info = f"Data from {dt1.strftime('%H:%M')} {day_of_week1} to {dt2.strftime('%H:%M')} {day_of_week2} " + info
        return info

    def get_lines_for_vehicle(self, vehicle_number: str):
        """ Returns the line(s) that the given vehicle_number operated on
        across all collected minutes. """
        lines = set()
        for minute_df in self.minutes_data.values():
            if "VehicleNumber" not in minute_df.columns or "Lines" not in minute_df.columns:
                continue

            matches = minute_df[minute_df["VehicleNumber"] == vehicle_number]
            if not matches.empty:
                lines.update(matches["Lines"].astype(str).unique())

        if not lines:
            print(f"No line data found for bus {vehicle_number}.")
        return lines

    def new_speed_map(self):
        return folium.Map(location=[52.2297, 21.0122], zoom_start=12, tiles="CartoDB positron")

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
        # print("Real time moments loaded.")

    def load_static_data(self):
        """ Reads bus stops and city streets in json format. """

        bus_stops_path = os.path.join(global_data.DATA_DIR, "bus_stops.json")
        with open(bus_stops_path, "r") as file:
            bus_stops_data = json.load(file)
            self.bus_stops = pd.DataFrame(bus_stops_data['result'])
        # print("Bus stops loaded.")

        streets_path = os.path.join(global_data.DATA_DIR, "dictionary.json")
        with open(streets_path, "r") as file:
            streets_data = json.load(file)
            self.streets = streets_data['result']['ulice']
        # print("Streets loaded.")

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

            speeding_moments_df = merged_df[merged_df['speed'] >= global_data.COMPARISON_SPEED]
            self.speeding_moments.append(speeding_moments_df)

        valid_speed_count = 0
        for interval_df in self.intervals_data.values():
            valid_speeds = interval_df[(interval_df['speed'] <= global_data.MAX_SPEED) &
                                       (interval_df['speed'] >= global_data.MIN_SPEED)]
            valid_speed_count += len(valid_speeds)

        self.all_moments = valid_speed_count

    ################################################################################################

    def number_of_speeding_buses(self) -> int:
        """ Count unique buses that reached the speed of >= global_data.COMPARISON_SPEED. """

        all_speeding_moments = pd.concat(self.speeding_moments, ignore_index=True)
        high_speed_vehicle_count = all_speeding_moments['VehicleNumber'].nunique()
        return high_speed_vehicle_count

    def report_speeds(self):
        """ Plots frequencies of speeds. Prints how many times someone was speeding. """

        all_intervals_df = pd.concat(self.intervals_data.values())
        speeds_series = all_intervals_df['speed']
        high_speed_count = (speeds_series >= global_data.COMPARISON_SPEED).sum()
        high_speeds_series = speeds_series[speeds_series >= global_data.COMPARISON_SPEED]

        max_speed = speeds_series.max()
        interval = 2
        colour = "yellow"
        bins = range(interval, min(int(max_speed) + 5, 100), interval)

        plt.hist(speeds_series, bins=bins, edgecolor=colour, color="red", alpha=0.9)
        plt.hist(high_speeds_series, bins=bins, edgecolor="red", color=colour, alpha=0.9)

        plt.title("Speed Distribution of Vehicles Every Second")
        plt.xlabel(f"Average Speed (km/h)")
        plt.ylabel("Number of Moments")

        text = (
            f"{self}\n"
            f"{self.number_of_speeding_buses()} of all buses reached speeds of {global_data.COMPARISON_SPEED} km/h."
        )
        stats = speeds_series.describe()

        plt.text(0.95, 0.95, stats.to_string(), fontsize=10,
                 verticalalignment="top", horizontalalignment="right",
                 transform=plt.gca().transAxes,
                 bbox={"facecolor": "white", "alpha": 0.5})
        plt.text(0.04, 0.04, text, fontsize=9, transform=plt.gcf().transFigure)
        plt.subplots_adjust(bottom=0.22)

        # plt.show()
        plt.savefig(os.path.join(self.output_dir, f"graph-speed"), dpi=300)
        plt.close()

    ################################################################################################

    def get_speeding_places_df(self):
        """ Returns a DataFrame of all speeding moments with street names assigned. """

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

        return speeding_df

    def report_speeding_places(self):
        """ Prints out global_data.TOP_STREET_NUMBER bus stops near which drivers drove
        with speeds above global_data.COMPARISON_SPEED. """
        speeding_df = self.get_speeding_places_df()
        filename = os.path.join(self.output_dir, f"speeding-places.txt")
        
        if speeding_df.empty:
            output = "No speeding data available.\n"
            with open(filename, "w") as f:
                f.write(output)
            return

        street_name_counts = Counter(speeding_df["street_name"])
        top_street_names = street_name_counts.most_common(global_data.TOP_STREET_NUMBER)
        
        output_lines = [
            f"Top {global_data.TOP_STREET_NUMBER} bus stops near which a bus was going faster than {global_data.COMPARISON_SPEED} km/h:"
        ]
        for street_name, count in top_street_names:
            output_lines.append(f"{street_name}: {count} times")
        output_str = "\n".join(output_lines)
        with open(filename, "w") as f:
            f.write(output_str)

    def visualize_speeding_places(self):
        """ Plots speeding moments on a map as points with street names and speed. """
        speeding_df = self.get_speeding_places_df()
        speed_map = self.new_speed_map()
        filename = os.path.join(self.output_dir, f"map-speeding-places.html")
        
        if speeding_df.empty:
            # print("No speeding data available.")
            speed_map.save(filename)  # empty map
            return

        for _, row in speeding_df.iterrows():
            try:
                lat, lon = float(row["Lat"]), float(row["Lon"])
                street = row.get("street_name", "Unknown")
                speed = row.get("speed", 0)
                tooltip = f"{street} | {speed:.1f} km/h"
                folium.CircleMarker(
                    location=(lat, lon),
                    radius=2,
                    color="red",
                    fill=True,
                    fill_color="red",
                    fill_opacity=0.7,
                    tooltip=tooltip
                ).add_to(speed_map)
            except (KeyError, ValueError, TypeError):
                continue

        speed_map.save(filename)

    ################################################################################################

    def get_bus_points(self, vehicle_number: str):
        """ Returns all collected GPS points and timestamps for a given vehicle_number. """
        all_points = []
        all_timestamps = []
        for minute_df in self.minutes_data.values():
            if "VehicleNumber" not in minute_df.columns:
                continue

            bus_points = minute_df[minute_df["VehicleNumber"] == vehicle_number]
            if not bus_points.empty:
                for _, row in bus_points.iterrows():
                    try:
                        lat, lon = float(row["Lat"]), float(row["Lon"])
                        timestamp = row["Time"]
                        all_points.append((lat, lon))
                        all_timestamps.append(timestamp)
                    except (KeyError, ValueError, TypeError):
                        continue

        return all_points, all_timestamps


    def visualize_bus_path(self, vehicle_number: str):
        """ Visualizes the exact GPS path of a single bus (by VehicleNumber) on a map of Warsaw. """

        # collect all points for the specified bus across all minutes
        all_points, all_timestamps = self.get_bus_points(vehicle_number)
        if not all_points:
            print(f"No GPS data found for bus {vehicle_number}.")
            return

        bus_map = self.new_speed_map()

        folium.PolyLine(
            all_points, color="green", weight=3, opacity=0.5,
            tooltip=f"Path of bus {vehicle_number} (line {self.get_lines_for_vehicle(vehicle_number)})"
        ).add_to(bus_map)

        n_points = len(all_points)
        min_opacity = 0.25
        max_opacity = 1.0
        for i, ((lat, lon), timestamp) in enumerate(zip(all_points, all_timestamps)):
            fade_ratio = 1 - (i / (n_points - 1)) * (1 - min_opacity)

            folium.CircleMarker(
                location=(lat, lon),
                radius=3,
                color="orange",
                fill=True,
                fill_color="orange",
                opacity=fade_ratio,
                fill_opacity=fade_ratio,
                tooltip=f"{timestamp}"
            ).add_to(bus_map)

        folium.Marker(all_points[0], icon=folium.Icon(color="green"),
                      tooltip=f"Start: {all_timestamps[0]}").add_to(bus_map)
        folium.Marker(all_points[-1], icon=folium.Icon(color="red"),
                      tooltip=f"End: {all_timestamps[-1]}").add_to(bus_map)

        bus_map.save(os.path.join(self.output_dir, f"map-bus-{vehicle_number}-path.html"))

    def visualize_lines(self, line_numbers: str):
        """ Plots the paths of the first available bus for each line in line_numbers
        on a single html map. """

        bus_map = self.new_speed_map()
        colours = cycle(["red", "orange", "green", "blue", "purple", "darkred", "darkgreen", "darkblue", "darkpurple"])

        for line in line_numbers:
            # find the first bus with this line
            vehicle_number = None
            for minute_df in self.minutes_data.values():
                if "VehicleNumber" not in minute_df.columns or "Lines" not in minute_df.columns:
                    continue
                match = minute_df[minute_df["Lines"] == line]
                if not match.empty:
                    vehicle_number = str(match.iloc[0]["VehicleNumber"])
                    break

            if not vehicle_number:
                print(f"No bus found for line {line}. Skipping.")
                continue

            # collect points for this bus
            all_points, all_timestamps = self.get_bus_points(vehicle_number)
            if not all_points:
                continue

            colour = next(colours)
            folium.PolyLine(all_points, color=colour, weight=3, opacity=0.8, tooltip=f"Line {line}").add_to(bus_map)
            folium.Marker(all_points[0], icon=folium.Icon(color="green"), tooltip=f"{line} start: {all_timestamps[0]}").add_to(bus_map)
            folium.Marker(all_points[-1], icon=folium.Icon(color="red"), tooltip=f"{line} end: {all_timestamps[-1]}").add_to(bus_map)

        lines_str = "-".join(line_numbers)
        bus_map.save(os.path.join(self.output_dir, f"map-bus-lines-{lines_str}.html"))
