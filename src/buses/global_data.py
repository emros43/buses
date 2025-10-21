""" Default global variables and general utility functions. """

import os
import numpy as np
import pandas as pd
from datetime import datetime
from pathlib import Path

MINUTES = 60  # minutes of bus data collection, > 1

COMPARISON_SPEED = 50  # base speed to compare buses, kmph
MAX_SPEED = 100  # kmph
MIN_SPEED = 1  # kmph
TOP_STREET_NUMBER = 20  # how many streets to print in summary

ZMT_API_URL = "https://api.um.warszawa.pl/api/action/"

ROOT_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"

####################################################################################################

def time_difference_in_hours(time1, time2):
    """Calculate what fraction of an hour passed from the first to the second string timestamp."""
    format_str = "%Y-%m-%d %H:%M:%S"
    dt1 = datetime.strptime(time1, format_str)
    dt2 = datetime.strptime(time2, format_str)

    delta = dt2 - dt1
    hours_difference = delta.total_seconds() / 3600
    return hours_difference

def haversine_distance(lat1, lon1, lat2, lon2):
    """ Calculates geographic distance in kilometres based on
    https://en.wikipedia.org/wiki/Haversine_formula. """
    r = 6371  # radius of the Earth in kilometres
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1
    a = np.sin(delta_lat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(delta_lon / 2.0) ** 2
    return r * 2 * np.arcsin(np.sqrt(a))

def time_difference_in_hours_vectorized(time1, time2):
    """Calculate what fraction of an hour passed between two pandas Series of timestamps."""
    dt1 = pd.to_datetime(time1)
    dt2 = pd.to_datetime(time2)

    # Subtracting two datetime Series results in a Timedelta Series
    delta = dt2 - dt1

    # Convert timedeltas to total seconds and then to hours
    hours_difference = delta.dt.total_seconds() / 3600
    return hours_difference

def haversine_distance_vectorized(lat1, lon1, lat2, lon2):
    """Calculates the Haversine distance between two points given as numpy arrays or pandas Series."""
    r = 6371  # Radius of the Earth in kilometres

    # Convert degrees to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    # Difference in coordinates
    delta_lat = lat2 - lat1
    delta_lon = lon2 - lon1

    # Haversine formula
    a = np.sin(delta_lat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(delta_lon / 2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))

    # Distance in kilometers
    distance = r * c
    return distance
