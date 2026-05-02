"""
sweep.py — 2D sensitivity sweep on (UA, watts_per_person).
Runs the lumped-capacitance thermal model on a grid of parameter
combinations, records peak T_in for each, and plots the result
as a heatmap.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp

from utils import load_data, dT_dt, style_axes
from occupancy import load_profiles, build_Q_array


def run_sweep(UA_values, wpp_values, t_array, T_ext_array, profiles, dates, C, T0):
    """
    Run the thermal model for every (wpp, UA) combination.

    Returns
    -------
    peak_T_in : np.ndarray, shape (len(wpp_values), len(UA_values))
        peak_T_in[i, j] = peak indoor temperature for wpp_values[i],
        UA_values[j].
    """
    peak_T_in = np.zeros((len(wpp_values), len(UA_values)))
    t_span = (t_array[0], t_array[-1])

    # Outer loop on wpp: rebuild Q_array once per wpp (depends on it),
    # reuse across all UA values (UA does not affect Q).
    for i, wpp in enumerate(wpp_values):
        Q_array, _ = build_Q_array(dates, profiles, watts_per_person=wpp)
        for j, ua in enumerate(UA_values):
            sol = solve_ivp(
                fun=dT_dt,
                t_span=t_span,
                y0=T0,
                t_eval=t_array,
                args=(t_array, T_ext_array, Q_array, ua, C),
            )
            peak_T_in[i, j] = sol.y[0].max()

    return peak_T_in


# ---------------------------------------------------------------------
# 1. Inputs — weather and occupancy over the simulation window
# ---------------------------------------------------------------------

df = load_data("data/raw/paris_weather.csv").sort_index()
df_sliced = df.loc["2024-07-01":"2024-07-07"]

t_array     = np.arange(len(df_sliced)) * 3600       # seconds
T_ext_array = df_sliced["temperature_2m"].values     # °C
dates       = df_sliced.index

profiles = load_profiles("data/raw/Defense_Occupation_Normalised.xlsx")


# ---------------------------------------------------------------------
# 2. Sweep configuration
# ---------------------------------------------------------------------

# Baseline values (also used by thermal_model.py, sobol.py).
UA  = 5e3       # envelope conductance (W/K)
C   = 5e7       # thermal capacitance (J/K)
T0  = [23.0]    # initial indoor temperature (°C)
wpp = 100       # watts per person, used as anchor for sweep range

# Sweep ranges: ±40% on UA, +20%/-30% on wpp. 20×20 = 400 ODE solves.
UA_values  = np.linspace(UA  * 0.6, UA  * 1.4, 20)
wpp_values = np.linspace(wpp * 0.7, wpp * 1.2, 20)


# ---------------------------------------------------------------------
# 3. Run sweep, save raw results, log summary
# ---------------------------------------------------------------------

sweep_results = run_sweep(UA_values, wpp_values, t_array, T_ext_array,
                          profiles, dates, C, T0)

np.save("data/processed/sweep_results.npy", sweep_results)
print(f"Sweep done. Shape: {sweep_results.shape}, "
      f"min={sweep_results.min():.1f}°C, max={sweep_results.max():.1f}°C")


# ---------------------------------------------------------------------
# 4. Heatmap
# ---------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(9, 7))

# .T transposes so UA is on y-axis, wpp on x-axis.
# origin="lower" puts small UA at the bottom (matches physical intuition).
# extent labels axes with real values instead of pixel indices.
im = ax.imshow(
    sweep_results.T,
    origin="lower",
    extent=[wpp_values[0], wpp_values[-1], UA_values[0], UA_values[-1]],
    aspect="auto",
    cmap="hot",
)

cbar = fig.colorbar(im, ax=ax)
cbar.set_label("Peak T_in (°C)", fontsize=13)

style_axes(ax, "Sensitivity sweep — peak T_in over (UA, w/p)",
           "Watts per person (W/person)", "UA (W/K)")

plt.tight_layout()
plt.savefig("images/sweep_heatmap.png", dpi=150)
plt.close()