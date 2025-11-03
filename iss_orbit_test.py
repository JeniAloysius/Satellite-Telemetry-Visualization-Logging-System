from skyfield.api import load, EarthSatellite
from vpython import sphere, vector, color, rate, points

# Load ISS TLE from the internet
stations_url = 'https://celestrak.org/NORAD/elements/stations.txt'
satellites = load.tle_file(stations_url)
iss = [sat for sat in satellites if 'ISS' in sat.name][0]

ts = load.timescale()

# Create Earth
earth = sphere(
    pos=vector(0,0,0),
    radius=6371e3,
    color=color.blue,
    shininess=0.8
)



# ISS point
iss_point = sphere(radius=100, color=color.red, make_trail=True)

while True:
    t = ts.now()
    geo = iss.at(t).subpoint()
    lat, lon = geo.latitude.radians, geo.longitude.radians

    # Convert lat/lon to 3D coords
    from math import cos, sin
    x = 6371 * cos(lat) * cos(lon)
    y = 6371 * cos(lat) * sin(lon)
    z = 6371 * sin(lat)

    iss_point.pos = vector(x, y, z)
    rate(15)
