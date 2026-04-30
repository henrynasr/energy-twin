# Energy Twin

HVAC sensitivity & optimization toolkit for metro stations, public data only.

## What this is

Early-stage data foundation — currently weather data fetch + analysis.

## Data

Open-Meteo API, 30 years of Paris hourly weather (1996-2025). Fetched by `fetch_weather.py`. Raw CSV not committed (in `.gitignore`).

## Scripts

- `fetch_weather.py` — pulls 30 years of hourly Paris weather from the Open-Meteo API, saves to `data/raw/paris_weather.csv`.
- `inspect_weather.py` — loads the CSV and prints shape, types, summary stats, missing values.
- `plot_weather.py` — generates 3 plots: monthly trend (1996-2025), yearly cycle overlay, average daily cycle.

## Setup

​```bash
git clone <repo-url>
cd energy-twin
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python fetch_weather.py         # run this first — pulls the data
python inspect_weather.py
python plot_weather.py
​```

## Status

Week 1 — local environment, data pipeline, first plots done. Next: refine plots, add more weather variables.