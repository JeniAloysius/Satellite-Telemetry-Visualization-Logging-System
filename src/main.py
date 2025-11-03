import matplotlib
matplotlib.use("TkAgg")   # Use backend that does NOT need Tk
import pandas as pd
import requests

# NOAA GOES X-ray real-time feed
url = "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"
print("Downloading data from:", url)

data = requests.get(url).json()
df = pd.DataFrame(data)

print("\nFirst few rows of real solar flare data:")
print(df.head())

import matplotlib.pyplot as plt


# Convert time column to datetime
df['time_tag'] = pd.to_datetime(df['time_tag'])

# Plot X-ray flux vs. time
plt.figure(figsize=(10,5))
for energy_band in df['energy'].unique():
    subset = df[df['energy'] == energy_band]
    plt.plot(subset['time_tag'], subset['flux'], label=energy_band)

plt.xlabel("Time (UTC)")
plt.ylabel("X-ray Flux (W/m^2)")
plt.title("Real-Time Solar Flare Intensity")
plt.legend()
plt.grid(True)
plt.show()

