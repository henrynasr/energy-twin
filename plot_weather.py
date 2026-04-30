# imports
import pandas as pd 
import matplotlib.pyplot as plt

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

def plot_monthly_trend(monthly_avg, output_path):
    plt.plot(monthly_avg["date"], monthly_avg["temperature_2m"])
    plt.xlabel("Date")
    plt.ylabel("Avg Temperature (°C)")
    plt.title("Paris temperature, 1996-2025")
    plt.savefig(output_path)
    plt.close()

def plot_yearly_cycle(monthly_avg, output_path):
    for year in monthly_avg["year"].unique():
        subset = monthly_avg[monthly_avg["year"] == year]
        plt.plot(subset["month"], subset["temperature_2m"])
    plt.xlabel("Month")
    plt.ylabel("Avg Temperature (°C)")
    plt.title("Paris yearly cycle, 30 years overlaid")
    plt.savefig(output_path)
    plt.close()

def plot_daily_cycle(df, output_path):
    df = df.copy()
    df["hour"] = df["time"].dt.hour
    hourly_avg = df.groupby("hour")["temperature_2m"].mean().reset_index()
    plt.plot(hourly_avg["hour"], hourly_avg["temperature_2m"])
    plt.xlabel("Hour")
    plt.ylabel("Avg Temperature (°C)")
    plt.title("Paris hourly temperature, 30 years average")
    plt.savefig(output_path)
    plt.close()

# Main block — runs everything
df = load_data("data/raw/paris_weather.csv")
monthly_avg = compute_monthly_avg(df)
plot_monthly_trend(monthly_avg, "data/processed/paris_temp.png")
plot_yearly_cycle(monthly_avg, "data/processed/paris_yearly_cycle.png")
plot_daily_cycle(df, "data/processed/paris_hourly_temperature.png")