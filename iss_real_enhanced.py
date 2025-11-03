# iss_real_enhanced.py
# Real-time ISS visualizer (VPython) + CSV telemetry + live ground-track + simple solar-weather overlay

from vpython import *
from skyfield.api import load, wgs84
import time, math, os, random, requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime


# ------------------- CONFIG -------------------
TLE_URL = "https://celestrak.org/NORAD/elements/stations.txt"
TLE_REFRESH_S = 60 * 30     # refresh TLE every 30 minutes
LOG_INTERVAL_S = 10         # seconds between telemetry writes
MAP_UPDATE_S = 5            # seconds between 2D map updates
EARTH_RADIUS_KM = 6371.0
ORBIT_SCALE = 1.4
ISS_SCALE = 0.18
LOG_PATH = "data/iss_telemetry.csv"
# ----------------------------------------------

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# ------------------- Skyfield / TLE -------------------
ts = load.timescale()

def load_iss_tle():
    try:
        sats = load.tle_file(TLE_URL)
        for s in sats:
            if "ISS" in s.name:
                print("✅ Loaded ISS TLE:", s.name)
                return s
        raise RuntimeError("ISS not present in TLE list")
    except Exception as e:
        print("❌ TLE load error:", e)
        return None

iss = load_iss_tle()
last_tle_time = time.time()

# ------------------- VPYTHON SCENE -------------------
scene = canvas(title="🌍 ISS RealTime Tracker — Enhanced", width=1200, height=800, background=color.black)
scene.camera.pos = vector(0, 0, 6)
scene.camera.axis = vector(0, 0, -1)
scene.range = 2.2

# stars background
stars = points(
    pos=[vector((random.random()-0.5)*50, (random.random()-0.5)*50, (random.random()-0.5)*50) for _ in range(600)],
    size=vector(2,2,2),
    color=color.white
)

# Earth (built-in texture stable)
earth = sphere(radius=1, texture=textures.earth, shininess=0.8)

# lighting
local_light(pos=vector(10, 0, 0), color=color.white)

# orbit ring
orbit_ring = ring(pos=vector(0,0,0), axis=vector(0,1,0), radius=1.15, thickness=0.015, color=color.gray(0.6))

# ISS marker + arrow + label
iss_marker = sphere(radius=ISS_SCALE, color=color.yellow, emissive=True, make_trail=True, trail_color=color.cyan, retain=2000)
arrow_iss = arrow(color=color.red, shaftwidth=0.03, opacity=0.9)
alt_label = label(text='', pos=vector(0,0,0), height=14, box=False, color=color.white, opacity=0)

# solar weather label (top-left of canvas)
sw_label = label(text='SW: N/A', pos=vector(-1.6, 1.1, 0), height=12, box=True, color=color.white, opacity=0.2)

# ------------------- CSV Telemetry Setup -------------------
if not os.path.exists(LOG_PATH):
    pd.DataFrame(columns=["timestamp_utc","lat_deg","lon_deg","alt_km","speed_km_s"]).to_csv(LOG_PATH, index=False)

def append_telemetry_row(ts_utc, lat, lon, alt_km, speed_km_s):
    df = pd.DataFrame([[ts_utc, lat, lon, alt_km, speed_km_s]],
                      columns=["timestamp_utc","lat_deg","lon_deg","alt_km","speed_km_s"])
    df.to_csv(LOG_PATH, mode="a", header=False, index=False)

# ------------------- Simple Matplotlib Ground Track -------------------
plt.ion()
fig, ax = plt.subplots(figsize=(9,4.5))
ax.set_title("ISS Ground Track (plate carrée)")
ax.set_xlim(-180, 180)
ax.set_ylim(-90, 90)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.grid(True, linestyle=':', color='gray', alpha=0.5)
track_lons, track_lats = [], []
track_plot, = ax.plot([], [], 'o-', color='yellow', markersize=4)

def update_ground_track(lat_deg, lon_deg):
    # keep lon normalized -180..180
    lon = ((lon_deg + 180) % 360) - 180
    track_lons.append(lon)
    track_lats.append(lat_deg)
    # limit trail length
    max_pts = 500
    xs = track_lons[-max_pts:]
    ys = track_lats[-max_pts:]
    track_plot.set_data(xs, ys)
    fig.canvas.draw()
    fig.canvas.flush_events()

# ------------------- Solar Weather Fetch (simple) -------------------
def fetch_solar_wind():
    try:
        url = "https://services.swpc.noaa.gov/json/solar-wind/near-real-time.json"
        r = requests.get(url, timeout=8)
        data = r.json()
        if not data:
            return None
        last = data[-1]
        return {
            "time_tag": last.get("time_tag"),
            "density": last.get("density"),
            "speed": last.get("speed"),
            "bt": last.get("bt"),
        }
    except Exception as e:
        # non-fatal
        return None

# ------------------- Helper: get subpoint lat,lon,alt,speed -------------------
def get_iss_subpoint_and_speed(sat):
    if sat is None:
        return None
    t = ts.now()
    geoc = sat.at(t)
    sub = wgs84.subpoint(geoc)   # latitude, longitude, elevation
    lat = sub.latitude.degrees
    lon = sub.longitude.degrees
    alt_km = sub.elevation.km
    # speed: compute magnitude of velocity vector (km/s)
    try:
        r, v = geoc.position.km, geoc.velocity.km_per_s
        speed = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    except Exception:
        speed = 0.0
    # position in ECEF-like units scaled to Earth radius=1 (for VPython)
    pos_km = geoc.position.km  # x,y,z km from Earth center
    pos_vpy = vector(pos_km[0]/EARTH_RADIUS_KM, pos_km[1]/EARTH_RADIUS_KM, pos_km[2]/EARTH_RADIUS_KM)
    return {
        "lat": lat, "lon": lon, "alt_km": alt_km, "speed_km_s": speed,
        "pos_v": pos_vpy
    }

# ------------------- Main Loop -------------------
print("✅ Starting enhanced ISS tracker...")
last_log = 0.0
last_map = 0.0
last_sw = 0.0
last_tle = time.time()

SW_CACHE = None

while True:
    rate(20)  # VPython frame rate

    # refresh TLE periodically (non-blocking)
    if time.time() - last_tle > TLE_REFRESH_S:
        new = load_iss_tle()
        if new:
            iss = new
            print("🔄 TLE refreshed")
        last_tle = time.time()

    # fetch solar wind every 120s
    if time.time() - last_sw > 120:
        SW_CACHE = fetch_solar_wind()
        if SW_CACHE:
            sw_label.text = f"SW: speed={SW_CACHE['speed']} km/s density={SW_CACHE['density']} /{SW_CACHE['time_tag']}"
            print("🔆 Solar wind:", SW_CACHE)
        last_sw = time.time()

    data = get_iss_subpoint_and_speed(iss)
    if data is None:
        continue

    # visual ISS pos (scaled)
    pos = data["pos_v"] * ORBIT_SCALE
    iss_marker.pos = pos

    # arrow and label
    arrow_iss.pos = pos
    arrow_iss.axis = norm(pos) * 0.35
    alt_label.pos = pos + vector(0, 0.12, 0)
    alt_label.text = f"Alt: {data['alt_km']:.0f} km\nSpeed: {data['speed_km_s']:.2f} km/s"

    # telemetry log
    if time.time() - last_log > LOG_INTERVAL_S:
        ts_utc = datetime.utcnow().isoformat()
        append_telemetry_row = None  # placeholder to silence linter in some environments
        # append CSV via pandas (append mode)
        append_telemetry_row = pd.DataFrame([{
            "timestamp_utc": ts_utc,
            "lat_deg": data["lat"],
            "lon_deg": data["lon"],
            "alt_km": data["alt_km"],
            "speed_km_s": data["speed_km_s"]
        }])
        append_telemetry_row.to_csv(LOG_PATH, mode='a', header=False, index=False)
        print(f"🛰 Logged {ts_utc} lat={data['lat']:.2f} lon={data['lon']:.2f} alt={data['alt_km']:.0f} km")
        last_log = time.time()

    # update 2D ground track plot periodically (not every frame)
    if time.time() - last_map > MAP_UPDATE_S:
        update_ground_track(data["lat"], data["lon"])
        last_map = time.time()
