import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp
from utils import load_data, dT_dt, style_axes
from occupancy import load_profiles, build_Q_array

# Main
df = load_data("data/raw/paris_weather.csv")
df.sort_index(inplace=True)
df_sliced = df.loc["2024-07-01":"2024-07-07"]

t_array = np.arange(len(df_sliced)) * 3600
T_ext_array = df_sliced["temperature_2m"].values
dates = df_sliced.index

# Real occupancy-driven Q (replaces the old square wave)
profiles = load_profiles("data/raw/Defense_Occupation_Normalised.xlsx")
Q_array, n_people = build_Q_array(t_array, dates, profiles)

UA = 5e3
C = 5e7
T0 = [23]
wpp = 100
UA_values = np.linspace(UA*0.6, UA*1.4, 20)
wpp_values = np.linspace(wpp*0.7, wpp*1.2, 20)
t_span = (t_array[0], t_array[-1])

sol = solve_ivp(
    fun=dT_dt,
    t_span=t_span,
    y0=T0,
    t_eval=t_array,
    args=(t_array, T_ext_array, Q_array, UA, C),
)

# Three-panel plot: T_ext + T_in / Q / headcount
hours = t_array / 3600
fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(11, 10), sharex=True)

ax1.plot(hours, T_ext_array, label="T_ext (outdoor)")
ax1.plot(hours, sol.y[0], label="T_in (indoor)")
style_axes(ax1, "Paris station thermal model — first week of July 2024",
           "", "Temperature (°C)")
ax1.legend(fontsize=12)

ax2.plot(hours, Q_array / 1000, color="tab:orange")
style_axes(ax2, "", "", "Q internal (kW)")

ax3.plot(hours, n_people, color="tab:green")
style_axes(ax3, "", "Hours since start", "Headcount (persons)")

plt.tight_layout()
plt.savefig("images/thermal_model.png", dpi=150)
plt.close()
