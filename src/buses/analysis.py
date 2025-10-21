""" Pre-prepared analysis functions using argparse to pick data set. """

import argparse
import os
from models import BusData
from pathlib import Path

import global_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run analysis on a specified bus data directory."
    )

    def check_positive(i):
        try:
            i = float(i)
            if i <= 0:
                raise argparse.ArgumentTypeError(f"{i} is not a positive integer")
        except ValueError:
            raise Exception(f"{i} is not a number")
        return i
    def parse_lines(arg):
        lines = [x.strip() for x in arg.split(",") if x.strip()]
        if not lines:
            raise argparse.ArgumentTypeError("At least one bus line must be provided.")
        return lines

    parser.add_argument("data_dir", help="Path to the bus data directory.")
    parser.add_argument("-s", "--speed", type=check_positive, nargs='?',
                        help="Average speed to compare statistics. Must be a positive number (default 50)")
    parser.add_argument("--top_streets", type=check_positive,
                        help="Number of streets to print in summary. Must be a positive number (default 20)")
    parser.add_argument("-l", "--lines", type=parse_lines,
                        help="Comma-separated list of bus lines to map (e.g., 123,220,401)")

    args = parser.parse_args()
    if args.speed:
        global_data.COMPARISON_SPEED = args.speed
    if args.top_streets:
        global_data.TOP_STREET_NUMBER = int(args.top_streets)

    data_path = Path(args.data_dir).resolve()
    if not data_path.is_dir():
        raise FileNotFoundError(f"Provided path does not exist or is not a directory: {data_path}")

    # print(f"Using data in directory: {data_path}")

    data = BusData(data_path)
    # data.visualize_bus_path("2210")  # specific physical vehicle, not line
    if args.lines:
        data.visualize_lines(args.lines)
        print(f"Bus lines mapped.")
    data.report_speeds()
    print(f"Speeds calculated.")
    data.report_speeding_places()
    print(f"Speeding places reported.")
    data.visualize_speeding_places()
    print(f"Speeding places mapped.")
    print(f"Report finished successfully. Can be found in {data.output_dir}")
