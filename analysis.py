""" Pre-prepared analysis functions using argparse to pick data set. """

import argparse
import global_data
from models import BusData

parser = argparse.ArgumentParser(description="Run the Bus App.")
parser.add_argument("--current-dir", help="Set the bus data directory "
                                          "(currently early_morning/, morning/ or evening/)")
args = parser.parse_args()

if args.current_dir:
    global_data.CURRENT_DIR = global_data.DATA_DIR + args.current_dir

print(f"Using data in directory: {global_data.CURRENT_DIR}...")


def full_analysis():
    """ Points 1.1), 1.2) and 2). """
    data = BusData(global_data.CURRENT_DIR)
    data.report_speeds()
    data.report_speeding_places()


def point_one_analysis():
    """ Points 1.1) and 1.2). """
    data = BusData(global_data.CURRENT_DIR)
    data.report_speeds()
    data.report_speeding_places()


def speed_only_analysis():
    """ Point 1.1) only. """
    data = BusData(global_data.CURRENT_DIR)
    data.report_speeds()


####################################################################################################

full_analysis()
