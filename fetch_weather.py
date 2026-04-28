import requests
import pandas as pd
url = "https://archive-api.open-meteo.com/v1/archive?latitude=48.85&longitude=2.35&start_date=1996-01-12&end_date=2025-12-31&hourly=temperature_2m,relative_humidity_2m"
response = requests.get(url)
print(response.status_code)
data = response.json()
df = pd.DataFrame(data["hourly"])
print(df.shape)
print(df.head())
df.to_csv("data/raw/paris_weather.csv", index=False)