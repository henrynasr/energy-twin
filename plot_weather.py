# imports
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from scipy import stats

def load_data(csv_path):
    # read CSV, parse datetime, return df
    df=pd.read_csv(csv_path)
    df["time"] = pd.to_datetime(df["time"])
    return df

def compute_monthly_avg(df):
    df = df.copy()
    df["year"] = df["time"].dt.year
    df["month"] = df["time"].dt.month
    monthly_avg = df.groupby(["year", "month"])["temperature_2m"].mean().reset_index()
    monthly_avg["date"] = pd.to_datetime(monthly_avg[["year", "month"]].assign(day=1))
    return monthly_avg

def compute_yearly_avg(df):
    df = df.copy()
    df["year"] = df["time"].dt.year
    yearly_avg = df.groupby("year")["temperature_2m"].mean().reset_index()
    return yearly_avg

def style_axes(ax, title, xlabel, ylabel):
    ax.set_title(title, fontsize=16)
    ax.set_xlabel(xlabel, fontsize=14)
    ax.set_ylabel(ylabel, fontsize=14)
    ax.tick_params(labelsize=11)
    ax.grid(True, alpha=0.3)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

def plot_monthly_trend(monthly_avg, output_path):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(monthly_avg["date"], monthly_avg["temperature_2m"])
    style_axes(ax, "Paris temperature, 1996-2025", "Date", "Avg Temperature (°C)")
    plt.tight_layout()
    plt.savefig(output_path, dpi = 150)
    plt.close()  

def plot_yearly_cycle(monthly_avg, output_path):
    fig, ax = plt.subplots(figsize=(10, 6))
    cmap = matplotlib.colormaps["coolwarm"]
    years = sorted(monthly_avg["year"].unique())
    n = len(years)
    for i, year in enumerate(years):
        subset = monthly_avg[monthly_avg["year"] == year]
        color = cmap(i / (n - 1))   # i/(n-1) maps 0→1 across the years
        ax.plot(subset["month"], subset["temperature_2m"], color=color, alpha=0.7)   
    style_axes(ax, "Paris yearly cycle, 1996-2025 overlaid", "Month", "Avg Temperature (°C)")
    norm = mcolors.Normalize(vmin=years[0], vmax=years[-1])
    sm = cm.ScalarMappable(cmap=cmap, norm=norm)
    fig.colorbar(sm, ax=ax, label="Year")
    plt.tight_layout()
    plt.savefig(output_path, dpi = 150)
    plt.close()

def plot_daily_cycle(df, output_path):
    df = df.copy()
    df["hour"] = df["time"].dt.hour
    hourly_avg = df.groupby("hour")["temperature_2m"].mean().reset_index()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(hourly_avg["hour"], hourly_avg["temperature_2m"])
    style_axes(ax, "Paris hourly temperature, 1996-2025 averaged", "Hour", "Avg Temperature (°C)")
    plt.tight_layout()
    plt.savefig(output_path, dpi = 150)
    plt.close()

def plot_yearly_trend(yearly_avg, output_path):
    x = yearly_avg["year"]
    y = yearly_avg["temperature_2m"]

    slope, intercept, r, p, _ = stats.linregress(x, y)
    y_fit = slope * x + intercept

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(x, y)
    ax.plot(x, y_fit)

    style_axes(ax, "Paris Yearly Mean Temperature, 1996-2025", "Year", "Avg Temperature (°C)")

    ax.text( 0.05, 0.95, f"slope: {slope*10:.2f} °C/decade\np-value: {p:.4f}",
        transform=ax.transAxes,va="top",
        bbox=dict(facecolor="white", edgecolor="gray", alpha=0.8))

    plt.tight_layout()
    plt.savefig(output_path, dpi = 150)
    plt.close()

def plot_temp_humidity(df, output_path):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df["temperature_2m"], df["relative_humidity_2m"], alpha=0.05, s=2)
    corr = df["temperature_2m"].corr(df["relative_humidity_2m"])
    style_axes(ax, "Paris: temperature vs humidity, 1996-2025", "Temperature (°C)", "Relative humidity (%)")
    ax.text(0.95, 0.95, f"correlation: {corr:.2f}",
           transform=ax.transAxes, ha="right", va="top",
           bbox=dict(facecolor="white", edgecolor="gray", alpha=0.8))
    plt.tight_layout()
    plt.savefig(output_path, dpi = 150)
    plt.close()

# Main block — runs everything

df = load_data("data/raw/paris_weather.csv")

monthly_avg = compute_monthly_avg(df)
yearly_avg = compute_yearly_avg(df)

plot_monthly_trend(monthly_avg, "images/paris_monthly_temp.png")
plot_yearly_cycle(monthly_avg, "images/paris_yearly_cycle.png")
plot_daily_cycle(df, "images/paris_hourly_temperature.png")
plot_yearly_trend(yearly_avg, "images/yearly_trend.png")
plot_temp_humidity(df, "images/temp_humidity_corr.png")