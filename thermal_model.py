"""
thermal_model.py — single-run lumped-capacitance thermal model
for one metro station zone, driven by Paris weather and RATP
occupancy. Produces a three-panel diagnostic plot.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

from utils import load_data, dT_dt, style_axes
from occupancy import load_profiles, build_Q_array


# ---------------------------------------------------------------------
# 1. Inputs — weather and occupancy over the simulation window
# ---------------------------------------------------------------------

df = load_data("data/raw/paris_weather.csv").sort_index()
df_sliced = df.loc["2024-07-01":"2024-07-07"]

t_array     = np.arange(len(df_sliced)) * 3600       # seconds
T_ext_array = df_sliced["temperature_2m"].values     # °C
dates       = df_sliced.index

profiles = load_profiles("data/raw/Defense_Occupation_Normalised.xlsx")
Q_array, n_people = build_Q_array(dates, profiles)


# ---------------------------------------------------------------------
# 2. Physics parameters and ODE solve
# ---------------------------------------------------------------------

UA = 5e3       # envelope conductance (W/K)
C  = 5e7       # lumped thermal capacitance (J/K)
T0 = [23.0]    # initial indoor temperature (°C)

sol = solve_ivp(
    fun=dT_dt,
    t_span=(t_array[0], t_array[-1]),
    y0=T0,
    t_eval=t_array,
    args=(t_array, T_ext_array, Q_array, UA, C),
)


# ---------------------------------------------------------------------
# 3. Three-panel diagnostic plot
#    Top    : T_ext vs T_in
#    Middle : internal heat load Q
#    Bottom : occupant headcount n
# ---------------------------------------------------------------------

if __name__ == "__main__":

    hours = t_array / 3600
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(11, 10), sharex=True)

    # Top panel — outdoor vs indoor temperature
    ax1.plot(hours, T_ext_array, label="T_ext (outdoor)")
    ax1.plot(hours, sol.y[0],    label="T_in (indoor)")
    style_axes(ax1, "Paris station thermal model — first week of July 2024",
            "", "Temperature (°C)")
    ax1.legend(fontsize=12)

    # Middle panel — internal heat load
    ax2.plot(hours, Q_array / 1000, color="tab:orange")
    style_axes(ax2, "", "", "Q internal (kW)")

    # Bottom panel — headcount
    ax3.plot(hours, n_people, color="tab:green")
    style_axes(ax3, "", "Hours since start", "Headcount (persons)")

    plt.tight_layout()
    plt.savefig("images/thermal_model.png", dpi=150)
    plt.close()