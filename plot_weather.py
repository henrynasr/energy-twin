import pandas as pd 
import matplotlib.pyplot as plt
df=pd.read_csv("data/raw/paris_weather.csv")
df["time"] = pd.to_datetime(df["time"])
# df["year"] = df["time"].dt.year
# df["month"] = df["time"].dt.month
# monthly_avg = df.groupby(["year", "month"])["temperature_2m"].mean()
# monthly_avg = monthly_avg.reset_index()
# monthly_avg["date"] = pd.to_datetime(monthly_avg[["year", "month"]].assign(day=1))
# plt.plot(monthly_avg["date"], monthly_avg["temperature_2m"])
# plt.xlabel("Date")
# plt.ylabel("Avg Temperature (°C)")
# plt.title("Paris temperature, 1996-2025")
# plt.savefig("data/processed/paris_temp.png")
# plt.close()
# for year in monthly_avg["year"].unique():
#     subset = monthly_avg[monthly_avg["year"] == year]
#     plt.plot(subset["month"], subset["temperature_2m"])

# plt.xlabel("Month")
# plt.ylabel("Avg Temperature (°C)")
# plt.title("Paris yearly cycle, 30 years overlaid")
# plt.savefig("data/processed/paris_yearly_cycle.png")
# plt.close()

df["hour"]=df["time"].dt.hour
hourly_avg = df.groupby(df["hour"])["temperature_2m"].mean().reset_index()
plt.plot(hourly_avg["hour"],hourly_avg["temperature_2m"])
plt.xlabel("Hour")
plt.ylabel("AVg Temperature (°C)")
plt.title("Paris hourly temperature, 30 years average")
plt.savefig("data/processed/paris_hourly_temperature.png")
plt.close()