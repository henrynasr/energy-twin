import pandas as pd

df = pd.read_csv("data/raw/paris_weather.csv")

print("shape:")
print(df.shape)

print("\ndtypes:")
print(df.dtypes)

print("\nhead:")
print(df.head())

print("\ntail:")
print(df.tail())

print("\ndescribe:")
print(df.describe())

print("\nnulls:")
print(df.isnull().sum())