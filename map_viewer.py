import pandas as pd
import time
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import os

# Path to your ISS telemetry file
path = "data/iss_telemetry.csv"

# --- Initialize map ---
plt.ion()  # interactive mode on
fig = plt.figure(figsize=(10, 5))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.stock_img()
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS)
ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.set_title("ISS Ground Track - Live View")
line, = ax.plot([], [], color='red', linewidth=2, transform=ccrs.Geodetic())
plt.show(block=False)

# --- Main update loop ---
while True:
    try:
        if os.path.exists(path):
            df = pd.read_csv(path)

            # Ensure expected columns exist
            if not df.empty and {"lat_deg", "lon_deg"}.issubset(df.columns):
                lats = df["lat_deg"].values[-500:]   # show last 500 points max
                lons = df["lon_deg"].values[-500:]

                # Update plot data
                line.set_data(lons, lats)
                ax.set_title(f"ISS Ground Track - {len(df)} points")
                fig.canvas.draw_idle()
                plt.pause(1)
            else:
                print("map_viewer: CSV missing required columns (lat_deg, lon_deg).")
        else:
            print(f"map_viewer: File not found at {path}")

    except Exception as e:
        print("map error:", e)

    time.sleep(2)
