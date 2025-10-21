# Warsaw Public Transport – Bus Data Platform

Analyze and visualize Warsaw’s public bus network using live and historical data from the [Warsaw Open Data API](https://api.um.warszawa.pl/).

---

## Features

- **Data Discovery:** Fetch all Warsaw bus stops, routes, and streets used by public buses.
- **Live Data Collection:** Collect real-time bus location data for a selected time window - either starting immediately or scheduled for a later time.
- **Activity Analysis:** Analyze bus movement to summarize speeds and detect speeding patterns.
- **Visualization:** Generate graphs, maps and summaries.

---

## Installation

Make sure you have **Python 3.6+** installed, then install the package locally:

```bash
pip install /path_to/buses
```

---

## Usage

### Data Collection

1. Create an account at the [Warsaw Open Data API](https://api.um.warszawa.pl/).
2. Replace the example `API_KEY` value in `api_key.env` with your own key.

To collect bus lines, streets and today's bus stops:

```bash
python collect_static_data.py
```

Collect live bus positions for a specified duration:

```bash
python collect_real_time_data.py [-t [TIME]] [-m [MINUTES]]
```

- -t TIME - optional start time in HH:MM (default: now)
- -m MINUTES - optional minutes of duration to collect data (default: 60)

### Data Analysis

```bash
python analysis.py [-s SPEED] [--top_streets TOP_STREETS] [-l LINES] dataset/
```

- -l LINES - optional comma-separated list of bus lines to map
- -s SPEED - optional speed threshold in km/h (default: 50)
- --top_streets TOP_STREETS - optional number of streets to list (default: 20)
- dataset/ - path to a collected data folder

Available example datasets:

- data/morning/
- data/evening/

With their example reports:

- output/morning-20-report/
- output/morning-50-report/

---

## License

[MIT](https://choosealicense.com/licenses/mit/)
