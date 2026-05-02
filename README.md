# Energy Twin

HVAC sensitivity & optimization toolkit for metro stations. Public data only.

## What this is

Early-stage data foundation. Currently: weather data pipeline, exploratory analysis on 30 years of Paris hourly weather, a thermal model layer driven by that weather and by real RATP occupancy data, and a first 2D sensitivity sweep on envelope and load parameters. The longer-term goal is a Python toolkit for HVAC sensitivity analysis and regulation optimization on metro stations, using only public data sources (Open-Meteo, Météo-France, IDFM, RATP, RTE, ADEME).

## Findings

### Monthly mean temperature, 1996–2025
![Monthly mean temperature, Paris 1996-2025](images/paris_monthly_trend.png)

30 sinusoidal cycles over 30 years — the seasonal signal dominates. Notable outliers: hot summer of 2003 (European heatwave), cold winter of 2010, and a cluster of warm summers in the 2020s.

### Yearly cycle, 30 years overlaid
![Yearly cycle overlay](images/paris_yearly_cycle.png)

Each line is one year, colored from blue (1996) to red (2025). Winter months show wider year-to-year spread than summer. Recent years (red) bias toward the upper edge of the summer envelope — the warming signal showing up on a seasonal view.

### Average daily cycle
![Average daily temperature cycle](images/paris_daily_cycle.png)

Averaged over 30 years: minimum at 5–6 AM (~8.7 °C), maximum at 2–3 PM (~15.4 °C). Diurnal swing of ~6.7 °C.

### Yearly mean temperature trend
![Yearly mean temperature trend](images/yearly_trend.png)

Linear regression on annual means: **+0.48 °C/decade**, p = 0.0002. Statistically significant warming, consistent with reported Western European trends. 30 data points, one per year.

### Temperature vs relative humidity
![Temperature vs relative humidity](images/paris_temp_humidity.png)

Moderate inverse correlation (r = -0.58). Cold air clusters at high humidity; hot air spans a wide humidity range. The shape of the cloud reflects Clausius-Clapeyron — air's water-holding capacity rises ~7%/°C, so at low temperatures even small amounts of water vapor saturate the air, while warm air can be dry. Directly relevant to HVAC dehumidification load: summer cooling is also water removal.

### Occupancy data — Pôle La Défense

Source: RATP open data, "Fréquentation du pôle La Défense" CSV from [data.iledefrance.fr](https://data.iledefrance.fr/explore/dataset/frequentation-du-pole-de-la-defense-experimentation-de-lissage-des-heures-de-poi/), entries on the corridor of Pôle La Défense.

Pre-processing pipeline (Excel-side, before the Python project picks it up):

1. **Filter to post-COVID years** to remove the pandemic anomaly from the typical-day signal.
2. **Group by day-type and hour**, compute the mean count for each: JOHV (working day, school in session), JOVS (working day, school holidays), SA (Saturday), DIJFP (Sunday + public holidays).
3. **Merge SA and DIJFP into WKD** (weekend) by taking the hourly maximum across the two columns. We want the envelope of weekend traffic, not the average — sizing on the busier of the two.
4. **Normalise** by setting the highest value of the dataset (JOHV at 18h) as 100%. All other cells become percentages of that peak. The resulting profile is dimensionless.
5. **Calibrate to absolute headcount** by anchoring 100% to **400 persons** in the studied corridor. Multiplying the percentage profile by 400 gives an instantaneous headcount.

Result: three normalised hourly profiles (JOHV, JOVS, WKD), 24 values each, in `data/raw/Defense_Occupation_Normalised.xlsx`. Read by `occupancy.py`.

### Thermal model — first week of July 2024
![Thermal model output](images/thermal_model.png)

Lumped-capacitance model of one metro station zone — `C·dT_in/dt = UA·(T_ext - T_in) + Q_internal` — driven by real Paris weather and real RATP occupancy. The synthetic square-wave Q from the previous version is gone; Q is now computed from the headcount profile:

`Q(t) = n_people(t) × 100 W/person + 10 kW (lighting + equipment baseline)`

Project scope is July 2024, so weekdays are dispatched to JOVS (summer school holidays) and Saturday/Sunday to WKD.

Three panels, top to bottom: T_ext vs T_in, Q internal, headcount n. Five weekday peaks at 18h (~395 people, ~50 kW) and two flatter weekend humps at 17h (~340 people, ~43 kW) are clearly visible.

The three behaviors from the synthetic version still hold:
- **Offset.** T_in sits ~3 °C above T_ext at peak — `Q/UA = 50000/5000 = 10 °C` is the theoretical maximum offset, damped down by thermal inertia.
- **Lag.** T_in peaks ~5 h after T_ext, consistent with `τ = C/UA ≈ 2.8 h`.
- **Damping.** T_in is markedly smoother than the occupancy spikes — the thermal mass low-pass-filters the load.

Compared to the synthetic version, peak T_in is ~5 °C higher (50 kW vs 20 kW peak Q). Parameters (UA, C) remain order-of-magnitude estimates, **not calibrated**.

### Sensitivity sweep — UA × watts per person
![Sensitivity sweep heatmap](images/sweep_heatmap.png)

400 thermal model runs over the same week of July 2024, sweeping two parameters:
- **UA** (envelope conductance) from 3000 to 7000 W/K — ±40% around the baseline of 5000 W/K.
- **Watts per person** from 70 to 120 W — covering seated to active occupancy.

Each pixel is one full simulation; the color is the peak T_in reached during the week.

Findings:
- Peak T_in ranges from ~28 °C (high UA, low w/p — leaky envelope, light load) to ~35 °C (low UA, high w/p — sealed envelope, heavy load). A ~7 °C spread across realistic parameter ranges.
- The gradient is **diagonal**, not horizontal or vertical. Neither parameter dominates the other on this window — both contribute comparably to the peak temperature response. If one dominated, the heatmap would show horizontal or vertical bands.
- Under the operational case (w/p = 100, UA = 5000), peak T_in lands around 31 °C — consistent with a buried, unventilated station in summer. The model's ~30 °C July peak is physically plausible without active cooling.

This visual sweep is a precursor to a proper Sobol sensitivity analysis (next session), which will quantify the first-order and total-order indices for UA, w/p, and other parameters across the full HVAC system.

## Data

- **Open-Meteo Historical Weather API** (ERA5 reanalysis), 30 years of Paris hourly weather (1996–2025). Variables: 2 m temperature, 2 m relative humidity. Raw CSV not committed (`.gitignore`).
- **RATP — Fréquentation du pôle La Défense** (Île-de-France Mobilités open data). Filtered to post-COVID years, aggregated to hourly profiles by day-type, normalised on JOHV-18h = 100%. Processed file tracked in the repo: `data/raw/Defense_Occupation_Normalised.xlsx`.

## Scripts

- `fetch_weather.py` — pulls 30 years of hourly Paris weather from the Open-Meteo API, saves to `data/raw/paris_weather.csv`.
- `inspect_weather.py` — loads the CSV, prints shape, dtypes, summary stats, missing values.
- `plot_weather.py` — generates the 5 weather plots into `images/`.
- `occupancy.py` — reads the RATP normalised profiles, builds `(Q_array, n_people)` from a datetime index. Used by `thermal_model.py` and `sweep.py`.
- `utils.py` — shared functions: `load_data`, `dT_dt` (thermal ODE slope), `style_axes` (matplotlib styling helper).
- `thermal_model.py` — single-run lumped-capacitance ODE driven by the weather CSV and `occupancy.py`. Three-panel plot saved to `images/thermal_model.png`.
- `sweep.py` — 20×20 sensitivity sweep on (UA, watts_per_person), heatmap saved to `images/sweep_heatmap.png`.

## Setup

```bash
git clone https://github.com/henrynasr/energy-twin
cd energy-twin
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
python fetch_weather.py         # run this first — pulls the data
python inspect_weather.py
python plot_weather.py
python thermal_model.py
python sweep.py
```

## Status

Week 1 — local environment, data pipeline, weather plots, thermal model with real RATP occupancy profiles, and first 2D sensitivity sweep. Next: proper Sobol sensitivity analysis (SALib) on UA, w/p, C, baseline load.
