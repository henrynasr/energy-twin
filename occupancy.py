"""
occupancy.py — internal heat gain Q(t) for one metro station zone,
driven by RATP normalised occupancy profiles (Pôle La Défense).
"""

import numpy as np
import pandas as pd


# Default occupancy parameters. Overridable per call to build_Q_array,
# also used as Sobol sweep baseline.
PEOPLE_PEAK = 400          # peak headcount in the studied corridor
WATTS_PER_PERSON = 100     # sensible heat per occupant (W)
BASELINE_W = 10_000        # lighting + equipment baseline (W)


def load_profiles(path):
    """
    Read the normalised occupancy Excel and return hourly profiles.

    Returns
    -------
    dict
        {"JOHV": np.ndarray(24), "JOVS": np.ndarray(24), "WKD": np.ndarray(24)}
        Each array is the hourly occupancy fraction (0.0 to 1.0),
        indexed by hour-of-day (0 = 00h, 23 = 23h).
    """
    df = pd.read_excel(path, sheet_name="Sheet1")
    df.columns = ["heure", "JOHV", "JOVS", "WKD"]

    return {
        "JOHV": df["JOHV"].to_numpy(),
        "JOVS": df["JOVS"].to_numpy(),
        "WKD":  df["WKD"].to_numpy(),
    }


def build_Q_array(dates, profiles, people_peak=PEOPLE_PEAK,
                  watts_per_person=WATTS_PER_PERSON,
                  baseline_w=BASELINE_W):
    """
    Build internal heat gain Q(t) and headcount n(t) over a simulation window.

    Parameters
    ----------
     dates : pd.DatetimeIndex
        One timestamp per element of t_array.
    profiles : dict
        Output of load_profiles().

    Returns
    -------
    Q_array : np.ndarray  (W)
    n_people : np.ndarray  (persons)
    """
    n_people = np.empty(len(dates))
    for i, ts in enumerate(dates):
        profile = profiles["WKD"] if ts.weekday() >= 5 else profiles["JOVS"]
        n_people[i] = profile[ts.hour] * people_peak

    Q_array = n_people * watts_per_person + baseline_w
    return Q_array, n_people


if __name__ == "__main__":
    # Smoke test: load profiles, build a week of Q and n, print stats.

    p = load_profiles("data/raw/Defense_Occupation_Normalised.xlsx")
    for k, v in p.items():
        print(f"{k}: peak={v.max():.3f} at hour {v.argmax()}, mean={v.mean():.3f}")

    # Test window: 1 week starting Mon 2024-07-01 (matches thermal_model.py).
    dates = pd.date_range("2024-07-01", periods=168, freq="h")
    Q, n = build_Q_array(dates, p)

    print(f"\nWeek 2024-07-01 to 2024-07-07:")
    print(f"  Q range : {Q.min():.0f} W  →  {Q.max():.0f} W")
    print(f"  n_people: {n.min():.1f}    →  {n.max():.1f}")
    print(f"  Peak at : {dates[Q.argmax()]}")