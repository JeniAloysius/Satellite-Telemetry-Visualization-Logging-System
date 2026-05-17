from vpython import sphere, vector, rate, color, label
from skyfield.api import load
import math

# -----------------------------
# CONFIG: satellites to track
# -----------------------------
TARGET_SATS = [
    "ISS (ZARYA)",
    "HUBBLE SPACE TELESCOPE",
    "NOAA 19"
]

# -----------------------------
# Load TLE Data
# -----------------------------
ts = load.timescale()
sats = load.tle_file("https://celestrak.org/NORAD/elements/active.txt")

selected = []
for sat in sats:
    if sat.name.upper() in [t.upper() for t in TARGET_SATS]:
        selected.append(sat)

print(f"Tracking {len(selected)} satellites...")

# -----------------------------
# VPython Scene Setup
# -----------------------------
earth = sphere(radius=6371, texture={"file": "https://i.imgur.com/8bX6ZzR.jpeg"})

colors = [color.yellow, color.cyan, color.green, color.red, color.blue]

objects = []

# Create satellite markers
for i, sat in enumerate(selected):
    sat_color = colors[i % len(colors)]
    marker = sphere(
        pos=vector(0, 0, 0),
        radius=150,
        color=sat_color,
        make_trail=True,
        retain=300
    )
    lbl = label(text=sat.name, xoffset=20, yoffset=20, space=30)
    objects.append({"sat": sat, "marker": marker, "label": lbl, "color": sat_color})

# -----------------------------
# Update Loop
# -----------------------------
while True:
    t = ts.now()

    for obj in objects:
        sat = obj["sat"]
        geo = sat.at(t).subpoint()

        lat = math.radians(geo.latitude.degrees)
        lon = math.radians(geo.longitude.degrees)
        alt = geo.elevation.m

        R = 6371 + alt / 1000

        x = R * math.cos(lat) * math.cos(lon)
        y = R * math.cos(lat) * math.sin(lon)
        z = R * math.sin(lat)

        obj["marker"].pos = vector(x, y, z)
        obj["label"].pos = obj["marker"].pos

    rate(20)
