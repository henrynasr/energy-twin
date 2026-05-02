"""Sobol sensitivity analysis on the thermal model.

6 parameters swept: UA, C, watts_per_person, baseline_W, PEOPLE_PEAK, T0.
2 metrics computed per run: peak T_in, % hours T_in > 26 °C.
"""

import time
import numpy as np
from scipy.integrate import solve_ivp
from tqdm import tqdm
from SALib.sample import sobol as sobol_sample
from SALib.analyze import sobol as sobol_analyze

from utils import load_data, dT_dt
from occupancy import load_profiles, build_Q_array

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from utils import style_axes

def plot_sobol(Si, metric_name, filename):
    names = problem["names"]
    x = np.arange(len(names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(x - width/2, Si["S1"], width, yerr=Si["S1_conf"],
           label="S1 (alone)", capsize=4, color="steelblue")
    ax.bar(x + width/2, Si["ST"], width, yerr=Si["ST_conf"],
           label="ST (with interactions)", capsize=4, color="firebrick")

    ax.set_xticks(x)
    ax.set_xticklabels(names)
    ax.legend()
    style_axes(ax, title=f"Sobol sensitivity — {metric_name}", ylabel="Sobol index")

    plt.tight_layout()
    plt.savefig(filename, dpi=120)
    plt.close()
    print(f"Saved {filename}")

# ---- Problem definition --------------------------------------------------

problem = {
    "num_vars": 6,
    "names": ["UA", "C", "wpp", "baseline_W", "PEOPLE_PEAK", "T0"],
    "bounds": [
        [3000, 7000],      # UA  [W/K]
        [2.5e7, 7.5e7],    # C   [J/K]
        [70, 120],         # wpp [W/person]
        [5000, 15000],     # baseline_W [W]
        [300, 500],        # PEOPLE_PEAK [persons]
        [18, 28],          # T0  [°C]
    ],
}

N = 512
samples = sobol_sample.sample(problem, N)
print(f"Samples shape: {samples.shape}")  # expect (7168, 6)


# ---- Scenario inputs (fixed across all runs) -----------------------------

df = load_data("data/raw/paris_weather.csv")
df_week = df.loc["2024-07-01":"2024-07-07"]

t_array = np.arange(len(df_week)) * 3600           # seconds
T_ext_array = df_week["temperature_2m"].values
dates = df_week.index

profiles = load_profiles("data/raw/Defense_Occupation_Normalised.xlsx")


# ---- Single-run evaluator ------------------------------------------------

def eval_model(row, t_array, T_ext_array, dates, profiles):
    """Run one ODE for one parameter set. Return (peak_T_in, pct_hours_over_26)."""
    UA, C, wpp, baseline_W, peak, T0 = row

    Q_array, _ = build_Q_array(
        t_array, dates, profiles,
        watts_per_person=wpp,
        baseline_w=baseline_W,
        people_peak=peak,
    )

    sol = solve_ivp(
        dT_dt,
        t_span=(t_array[0], t_array[-1]),
        y0=[T0],
        t_eval=t_array,
        args=(t_array, T_ext_array, Q_array, UA, C),
    )

    T_in = sol.y[0]
    peak_T = T_in.max()
    pct_over = (T_in > 26).sum() / len(T_in) * 100
    return peak_T, pct_over


# ---- Main loop -----------------------------------------------------------

N_total = samples.shape[0]
Y_peak = np.zeros(N_total)
Y_pct = np.zeros(N_total)

t0 = time.perf_counter()
for i, row in enumerate(tqdm(samples)):
    Y_peak[i], Y_pct[i] = eval_model(row, t_array, T_ext_array, dates, profiles)
elapsed = time.perf_counter() - t0

print(f"\nLoop done in {elapsed:.1f} s")
print(f"First 5 Y_peak: {Y_peak[:5]}")
print(f"First 5 Y_pct:  {Y_pct[:5]}")

Si_peak = sobol_analyze.analyze(problem, Y_peak, print_to_console=True)
Si_pct = sobol_analyze.analyze(problem, Y_pct, print_to_console=True)

plot_sobol(Si_peak, "Peak T_in", "images/sobol_peak.png")
plot_sobol(Si_pct, "% hours > 26 °C", "images/sobol_pct.png")