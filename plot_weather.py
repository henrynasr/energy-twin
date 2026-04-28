import pandas as pd 
import matplotlib.pyplot as plt
df=pd.read_csv("data/raw/paris_weather.csv")
df["time"] = pd.to_datetime(df["time"])
plt.plot(df["time"], df["temperature_2m"])
plt.xlabel("Date")
plt.ylabel("Temperature (°C)")
plt.title("Paris temperature, 1996-2025")
plt.savefig("data/processed/paris_temp.png")
plt.show()