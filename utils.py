import pandas as pd
import numpy as np


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

