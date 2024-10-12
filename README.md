# Warsaw's public transport - buses

https://api.um.warszawa.pl/

## Features

- fetch all bus stops, bus lines and streets used by buses in Warsaw
- collect bus real-time location for an hour, either beginning now or at a set time in the future
- bus activity analysis - summary of speeds reached and speeding patterns

## Installation

```
pip install ./path_to/buses
```

## Usage
```
python ./buses/analysis.py
```
or
```
python ./buses/analysis.py --current-dir bus_data_directory/
```
currently available bus_data_directory/:
- early_morning/
- morning/
- evening/
