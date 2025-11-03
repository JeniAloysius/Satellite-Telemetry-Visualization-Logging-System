# iss_tracker_final.py
# Real-time ISS visualizer + CSV telemetry logger + solar wind overlay
from vpython import *
from skyfield.api import load, wgs84
import pandas as pd
import requests, os, math, time, random
from datetime import datetime

# ---------- CONFIG ----------
TLE_URL = "https://celestrak.org/NORAD/elements/stations.txt"
TLE_REFRESH_S = 1800
LOG_INTERVAL_S = 10
EARTH_RADIUS_KM = 6371.0
ORBIT_SCALE = 1.4
ISS_SCALE = 0.18
LOG_PATH = "data/iss_telemetry.csv"
os.makedirs("data", exist_ok=True)
# ----------------------------

# ---------- SKYFIELD SETUP ----------
ts = load.timescale()

def load_iss_tle():
    try:
        sats = load.tle_file(TLE_URL)
        for s in sats:
            if "ISS" in s.name:
                print("✅ TLE loaded:", s.name)
                return s
        raise RuntimeError("ISS not found")
    except Exception as e:
        print("❌ Error loading TLE:", e)
        return None

iss = load_iss_tle()
last_tle = time.time()

# ---------- VPYTHON SETUP ----------
scene = canvas(title="🌍 ISS RealTime Tracker",
               width=1200, height=800, background=color.black)
scene.camera.pos = vector(0, 0, 6)
scene.camera.axis = vector(0, 0, -1)
scene.range = 2.2

stars = points(
    pos=[vector((random.random()-0.5)*50,
                (random.random()-0.5)*50,
                (random.random()-0.5)*50) for _ in range(600)],
    size=vector(2,2,2), color=color.white
)

earth = sphere(radius=1, texture=textures.earth, shininess=0.8)
local_light(pos=vector(10, 0, 0), color=color.white)
orbit_ring = ring(pos=vector(0,0,0), axis=vector(0,1,0),
                  radius=1.15, thickness=0.015, color=color.gray(0.6))

iss_marker = sphere(radius=ISS_SCALE, color=color.yellow, emissive=True,
                    make_trail=True, trail_color=color.cyan, retain=2000)
arrow_iss = arrow(color=color.red, shaftwidth=0.03, opacity=0.9)
alt_label = label(text='', pos=vector(0,0,0), height=14,
                  box=False, color=color.white, opacity=0)
sw_label = label(text='SW: N/A', pos=vector(-1.6, 1.1, 0),
                 height=12, box=True, color=color.white, opacity=0.2)

# ---------- CSV SETUP ----------
if not os.path.exists(LOG_PATH):
    pd.DataFrame(columns=["timestamp_utc","lat_deg","lon_deg","alt_km","speed_km_s"]).to_csv(LOG_PATH, index=False)

def append_telemetry(ts_utc, lat, lon, alt, speed):
    """Safely append telemetry to CSV."""
    try:
        df = pd.DataFrame([[ts_utc, lat, lon, alt, speed]],
                          columns=["timestamp_utc","lat_deg","lon_deg","alt_km","speed_km_s"])
        df.to_csv(LOG_PATH, mode="a", header=False, index=False)
    except PermissionError:
        print("⚠️ CSV file locked — skipping write (maybe open in Excel?)")

# ---------- SOLAR WIND ----------
def fetch_solar_wind():
    try:
        r = requests.get("https://services.swpc.noaa.gov/json/solar-wind/near-real-time.json", timeout=8)
        data = r.json()
        if data:
            last = data[-1]
            return {
                "speed": last.get("speed"),
                "density": last.get("density"),
                "bt": last.get("bt"),
                "time_tag": last.get("time_tag")
            }
    except Exception:
        return None

# ---------- GET SUBPOINT ----------
def get_iss_data(sat):
    if not sat: return None
    t = ts.now()
    geoc = sat.at(t)
    sub = wgs84.subpoint(geoc)
    lat, lon, alt = sub.latitude.degrees, sub.longitude.degrees, sub.elevation.km
    try:
        v = geoc.velocity.km_per_s
        speed = math.sqrt(sum([vi**2 for vi in v]))
    except Exception:
        speed = 0.0
    pos = vector(*[p/EARTH_RADIUS_KM for p in geoc.position.km])
    return {"lat": lat, "lon": lon, "alt": alt, "speed": speed, "pos": pos}

# ---------- MAIN LOOP ----------
print("🚀 Starting ISS tracker (no map)...")

last_log = last_sw = 0
SW_CACHE = None

while True:
    rate(20)
    # Refresh TLE every 30 minutes
    if time.time() - last_tle > TLE_REFRESH_S:
        new = load_iss_tle()
        if new: iss = new
        last_tle = time.time()

    # Update solar wind every 2 min
    if time.time() - last_sw > 120:
        SW_CACHE = fetch_solar_wind()
        if SW_CACHE:
            sw_label.text = f"SW speed={SW_CACHE['speed']} km/s  dens={SW_CACHE['density']}  Bt={SW_CACHE['bt']}"
        last_sw = time.time()

    # Get ISS position
    data = get_iss_data(iss)
    if not data: continue

    # Update visuals
    pos = data["pos"] * ORBIT_SCALE
    iss_marker.pos = pos
    arrow_iss.pos = pos
    arrow_iss.axis = norm(pos) * 0.35
    alt_label.pos = pos + vector(0, 0.12, 0)
    alt_label.text = f"Alt: {data['alt']:.0f} km\nSpeed: {data['speed']:.2f} km/s"

    # Log telemetry
    if time.time() - last_log > LOG_INTERVAL_S:
        ts_utc = datetime.utcnow().isoformat()
        append_telemetry(ts_utc, data["lat"], data["lon"], data["alt"], data["speed"])
        print(f"🛰 {ts_utc} | lat={data['lat']:.2f} lon={data['lon']:.2f} alt={data['alt']:.0f} km spd={data['speed']:.2f}")
        last_log = time.time()
