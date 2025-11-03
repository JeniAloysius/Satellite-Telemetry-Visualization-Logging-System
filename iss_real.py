from vpython import sphere, vector, color, rate, points
from sgp4.api import Satrec, jday
from datetime import datetime
import pandas as pd
import requests, math, os, time, random

# --------------------- CONFIG ---------------------
TLE_URL = "https://celestrak.org/NORAD/elements/gp.php?CATNR=25544"  # ISS
LOG_PATH = "data/iss_log.csv"
UPDATE_INTERVAL = 10  # seconds between position updates
# --------------------------------------------------

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Fetch live TLE data
def fetch_tle():
    print("Fetching latest TLE data for ISS...")
    resp = requests.get(TLE_URL)
    lines = resp.text.strip().splitlines()
    return lines[0], lines[1], lines[2]

name, line1, line2 = fetch_tle()
satellite = Satrec.twoline2rv(line1, line2)

# --------------------- 3D ENVIRONMENT ---------------------
earth = sphere(pos=vector(0,0,0), radius=6.4, texture="https://i.imgur.com/yoEzbtg.jpg")
iss_marker = sphere(radius=0.15, color=color.red, make_trail=True)
stars = points(pos=[vector((random()-0.5)*50, (random()-0.5)*50, (random()-0.5)*50) for _ in range(1000)],
               size=2*vector(1,1,1), color=color.white)

# --------------------- DATA LOGGER ---------------------
if not os.path.exists(LOG_PATH):
    pd.DataFrame(columns=["timestamp","lat","lon","alt"]).to_csv(LOG_PATH, index=False)

def log_telemetry(lat, lon, alt):
    df = pd.DataFrame([[datetime.utcnow(), lat, lon, alt]],
                      columns=["timestamp","lat","lon","alt"])
    df.to_csv(LOG_PATH, mode="a", index=False, header=False)

# --------------------- POSITION CALCULATION ---------------------
def get_iss_position():
    now = datetime.utcnow()
    jd, fr = jday(now.year, now.month, now.day, now.hour, now.minute, now.second)
    e, r, v = satellite.sgp4(jd, fr)
    if e != 0:
        return None
    x, y, z = r
    lat = math.degrees(math.asin(z / math.sqrt(x**2 + y**2 + z**2)))
    lon = math.degrees(math.atan2(y, x))
    alt = math.sqrt(x**2 + y**2 + z**2) - 6371
    return lat, lon, alt

# --------------------- MAIN LOOP ---------------------
print("Starting live ISS tracker...")
t0 = time.time()

while True:
    rate(2)
    pos = get_iss_position()
    if pos:
        lat, lon, alt = pos

        # Convert lat/lon to 3D coordinates on sphere
        phi = math.radians(lat)
        theta = math.radians(lon)
        x = earth.radius * math.cos(phi) * math.cos(theta)
        y = earth.radius * math.cos(phi) * math.sin(theta)
        z = earth.radius * math.sin(phi)
        iss_marker.pos = vector(x, y, z)

        # Periodically log data
        if time.time() - t0 > UPDATE_INTERVAL:
            log_telemetry(lat, lon, alt)
            print(f"Logged: lat={lat:.2f}, lon={lon:.2f}, alt={alt:.2f} km")
            t0 = time.time()
