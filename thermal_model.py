import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.integrate import solve_ivp


def load_data(csv_path):
    df = pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])
    df.set_index("time", inplace=True)
    return df


def style_axes(ax, title, xlabel, ylabel):
    ax.set_title(title, fontsize=16)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.tick_params(labelsize=11)
    ax.grid(True, alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def dT_dt(t, T, t_array, T_ext_array, Q_array, UA, C):
    """
    Slope of indoor temperature at instant t.

    Args:
        t (float): current time in seconds (since simulation start).
        T (float): current indoor temperature in °C.
        t_array (np.ndarray): time grid in seconds, shape (N,).
        T_ext_array (np.ndarray): outdoor temperature in °C at each
            point of t_array, shape (N,).
        Q_array (np.ndarray): internal heat load in W at each point
            of t_array, shape (N,).
        UA (float): overall heat transfer coefficient × area, in W/K.
        C (float): lumped thermal capacitance, in J/K.

    Returns:
        float: dT/dt in °C/s.
    """
    T_ext = np.interp(t, t_array, T_ext_array)
    Q = np.interp(t, t_array, Q_array)
    return (UA * (T_ext - T) + Q) / C


# Main
df = load_data("data/raw/paris_weather.csv")
df.sort_index(inplace=True)
df_sliced = df.loc["2003-07-01":"2003-07-07"]

t_array = np.arange(len(df_sliced)) * 3600
T_ext_array = df_sliced["temperature_2m"].values

hour_of_day = df_sliced.index.hour.values
Q_array = np.where((hour_of_day >= 7) & (hour_of_day < 22), 20_000, 5_000)

UA = 5e3
C = 5e7
T0 = [23]
t_span = (t_array[0], t_array[-1])

sol = solve_ivp(
    fun=dT_dt,
    t_span=t_span,
    y0=T0,
    t_eval=t_array,
    args=(t_array, T_ext_array, Q_array, UA, C),
)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(t_array / 3600, T_ext_array, label="T_ext (outdoor)")
ax.plot(t_array / 3600, sol.y[0], label="T_in (indoor)")
style_axes(ax, "Paris station thermal model — first week of July 2003",
           "Hours since start", "Temperature (°C)")
ax.legend(fontsize=12)
plt.tight_layout()
plt.savefig("images/thermal_model.png", dpi=150)
plt.close()