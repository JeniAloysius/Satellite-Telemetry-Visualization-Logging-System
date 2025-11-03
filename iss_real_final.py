# iss_real_final.py
# Final enhanced ISS tracker:
# - 3D VPython globe + real ISS via Skyfield TLE
# - 3D ground-dot (sub-satellite point)
# - Live lat/lon readout in VPython
# - Solar-wind + Kp fetch, color-coded trail + alert
# - CSV telemetry with solar data
# - 2D ground-track matplotlib plot

from vpython import *
from skyfield.api import load, wgs84
import time, math, os, random, requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# ------------------- CONFIG -------------------
TLE_URL = "https://celestrak.org/NORAD/elements/stations.txt"
TLE_REFRESH_S = 60 * 30     # refresh TLE every 30 min
LOG_INTERVAL_S = 10         # seconds between telemetry writes
MAP_UPDATE_S = 5            # seconds between 2D map updates
SW_FETCH_S = 120            # seconds between solar-wind fetches
EARTH_RADIUS_KM = 6371.0
ORBIT_SCALE = 1.4
ISS_SCALE = 0.18
LOG_PATH = "data/iss_telemetry.csv"
# ----------------------------------------------

# ensure folders
os.makedirs("data", exist_ok=True)

# ------------------- Skyfield / TLE loader -------------------
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

# ------------------- VPython Scene -------------------
scene = canvas(title="🌍 ISS Tracker — Final", width=1200, height=800, background=color.black)
scene.camera.pos = vector(0, 0, 6)
scene.camera.axis = vector(0, 0, -1)
scene.range = 2.2

# stars
stars = points(
    pos=[vector((random.random()-0.5)*50, (random.random()-0.5)*50, (random.random()-0.5)*50) for _ in range(600)],
    size=vector(2,2,2),
    color=color.white
)

# Earth
earth = sphere(radius=1, texture=textures.earth, shininess=0.8)

# lighting
local_light(pos=vector(10, 0, 0), color=color.white)

# orbit ring
orbit_ring = ring(pos=vector(0,0,0), axis=vector(0,1,0), radius=1.15, thickness=0.015, color=color.gray(0.6))

# ISS marker + trail
iss_marker = sphere(radius=ISS_SCALE, color=color.yellow, emissive=True, make_trail=True, trail_color=color.cyan, retain=2000)
arrow_iss = arrow(color=color.red, shaftwidth=0.03, opacity=0.9)

# sub-satellite ground dot on globe (red)
ground_dot = sphere(radius=0.03, color=color.red, emissive=True)

# text labels in VPython
alt_label = label(text='', pos=vector(0,0,0), height=14, box=False, color=color.white, opacity=0)
latlon_label = label(text='', pos=vector(-1.6, 1.0, 0), height=12, box=True, color=color.white, opacity=0.3)
sw_label = label(text='SW: N/A', pos=vector(-1.6, 0.85, 0), height=12, box=True, color=color.white, opacity=0.2)
kp_alert_label = label(text='', pos=vector(-1.6, 0.7, 0), height=12, box=True, color=color.yellow, opacity=0.15)

# ------------------- CSV Telemetry Setup -------------------
if not os.path.exists(LOG_PATH):
    pd.DataFrame(columns=["timestamp_utc","lat_deg","lon_deg","alt_km","speed_km_s","sw_speed_km_s","sw_density","kp_index"]).to_csv(LOG_PATH, index=False)

def append_telemetry_row(ts_utc, lat, lon, alt_km, speed_km_s, sw_speed, sw_density, kp):
    df = pd.DataFrame([[ts_utc, lat, lon, alt_km, speed_km_s, sw_speed, sw_density, kp]],
                      columns=["timestamp_utc","lat_deg","lon_deg","alt_km","speed_km_s","sw_speed_km_s","sw_density","kp_index"])
    df.to_csv(LOG_PATH, mode="a", header=False, index=False)

# ------------------- Ground-track (matplotlib) -------------------
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
    lon = ((lon_deg + 180) % 360) - 180
    track_lons.append(lon)
    track_lats.append(lat_deg)
    max_pts = 500
    xs = track_lons[-max_pts:]
    ys = track_lats[-max_pts:]
    track_plot.set_data(xs, ys)
    fig.canvas.draw()
    fig.canvas.flush_events()

# ------------------- Solar data fetching -------------------
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
    except Exception:
        return None

def fetch_kp_index():
    try:
        url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
        r = requests.get(url, timeout=8)
        arr = r.json()
        if not arr:
            return None
        last = arr[-1]
        # last is like [ "2023-10-...T00:00:00Z", 1, ... ] — kp is at index 1 usually
        kp = None
        if len(last) > 1:
            try:
                kp = float(last[1])
            except:
                kp = None
        return kp
    except Exception:
        return None

# ------------------- Helper: subpoint + speed + vpos -------------------
def get_iss_subpoint_and_speed(sat):
    if sat is None:
        return None
    t = ts.now()
    geoc = sat.at(t)
    sub = wgs84.subpoint(geoc)
    lat = sub.latitude.degrees
    lon = sub.longitude.degrees
    alt_km = sub.elevation.km
    try:
        # Skyfield geocentric velocity in km/s accessible via velocity.km_per_s
        # geoc.position.km and geoc.velocity.km_per_s available
        v = geoc.velocity.km_per_s
        speed = math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])
    except Exception:
        speed = 0.0
    pos_km = geoc.position.km
    pos_vpy = vector(pos_km[0]/EARTH_RADIUS_KM, pos_km[1]/EARTH_RADIUS_KM, pos_km[2]/EARTH_RADIUS_KM)
    return {
        "lat": lat, "lon": lon, "alt_km": alt_km, "speed_km_s": speed,
        "pos_v": pos_vpy
    }

# ------------------- MAIN LOOP -------------------
print("✅ Starting final ISS tracker...")
last_log = 0.0
last_map = 0.0
last_sw = 0.0
last_tle = time.time()
SW_CACHE = None
KP_CACHE = None

while True:
    rate(20)

    # TLE refresh
    if time.time() - last_tle > TLE_REFRESH_S:
        new = load_iss_tle()
        if new:
            iss = new
            print("🔄 TLE refreshed")
        last_tle = time.time()

    # solar fetch
    if time.time() - last_sw > SW_FETCH_S:
        SW_CACHE = fetch_solar_wind()
        KP_CACHE = fetch_kp_index()
        if SW_CACHE:
            sw_label.text = f"SW speed={SW_CACHE['speed']} km/s density={SW_CACHE['density']} ({SW_CACHE['time_tag']})"
            print("🔆 Solar wind:", SW_CACHE)
        if KP_CACHE is not None:
            kp_alert_label.text = f"Kp = {KP_CACHE}"
            print("🔔 Kp index:", KP_CACHE)
        last_sw = time.time()

    data = get_iss_subpoint_and_speed(iss)
    if data is None:
        continue

    # visual pos
    pos = data["pos_v"] * ORBIT_SCALE
    iss_marker.pos = pos

    # ground dot: compute sub-satellite surface point (lat/lon -> unit sphere)
    phi = math.radians(data["lat"])
    theta = math.radians(data["lon"])
    gx = math.cos(phi) * math.cos(theta)
    gy = math.cos(phi) * math.sin(theta)
    gz = math.sin(phi)
    ground_dot.pos = vector(gx, gy, gz)  # on unit sphere (earth radius = 1)

    # arrow & labels
    arrow_iss.pos = pos
    arrow_iss.axis = norm(pos) * 0.35
    alt_label.pos = pos + vector(0, 0.12, 0)
    alt_label.text = f"Alt: {data['alt_km']:.0f} km\nSpeed: {data['speed_km_s']:.2f} km/s"
    latlon_label.text = f"Lat: {data['lat']:.3f}°\nLon: {data['lon']:.3f}°"

    # color-code trail and marker based on Kp (geomagnetic)
    kp_val = KP_CACHE if KP_CACHE is not None else 0
    if kp_val >= 6:
        iss_marker.trail_color = color.red
        iss_marker.color = color.red
        kp_alert_label.color = color.red
        kp_alert_label.box = True
    elif kp_val >= 4:
        iss_marker.trail_color = color.orange
        iss_marker.color = color.orange
        kp_alert_label.color = color.orange
    else:
        iss_marker.trail_color = color.cyan
        iss_marker.color = color.yellow
        kp_alert_label.color = color.yellow

    # telemetry log (with solar values)
    if time.time() - last_log > LOG_INTERVAL_S:
        ts_utc = datetime.utcnow().isoformat()
        sw_speed = SW_CACHE['speed'] if (SW_CACHE and 'speed' in SW_CACHE) else None
        sw_density = SW_CACHE['density'] if (SW_CACHE and 'density' in SW_CACHE) else None
        kp_val_write = KP_CACHE
        append_telemetry_row(ts_utc, data["lat"], data["lon"], data["alt_km"], data["speed_km_s"], sw_speed, sw_density, kp_val_write)
        print(f"🛰 Logged {ts_utc} lat={data['lat']:.2f} lon={data['lon']:.2f} alt={data['alt_km']:.0f} km Kp={kp_val_write}")
        last_log = time.time()

    # update 2D ground track
    if time.time() - last_map > MAP_UPDATE_S:
        update_ground_track(data["lat"], data["lon"])
        last_map = time.time()
