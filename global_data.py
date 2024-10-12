""" Global variables and general utility functions. """

from datetime import datetime
import numpy as np
import pandas as pd

API_KEY = "1c565fe7-d16e-4384-be6e-e30383bbc0ec"
URL = "https://api.um.warszawa.pl/api/action/"
DATA_DIR = "./buses/bus_data/"
# CURRENT_DIR = DATA_DIR + "early_morning/"
# CURRENT_DIR = DATA_DIR + "morning/"
CURRENT_DIR = DATA_DIR + "evening/"
MINUTES = 60  # > 1
UNIMPLEMENTED = -1
MAX_SPEED = 100
MIN_SPEED = 1
TOP_STREET_NUMBER = 20


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
