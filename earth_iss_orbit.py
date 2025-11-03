from vpython import *
from math import sin, cos

scene = canvas(title="Earth + ISS Orbit Demo",
               width=900, height=700, background=color.black)

# 🌍 Earth with correct texture
earth = sphere(
    pos=vector(0,0,0),
    radius=1,
    texture=textures.earth  # built-in VPython texture
)

# 💡 Sun light
distant_light(direction=vector( 1, 1, 1))
distant_light(direction=vector(-1,-1,-1))

# 🛰️ ISS satellite
iss = sphere(
    radius=0.04,
    color=color.red,
    make_trail=True,
    trail_color=color.yellow,
    trail_type="curve",
    interval=5,
    retain=500
)

# Orbit settings
orbit_radius = 1.2
angle = 0
inclination = radians(51.6)  # Real ISS 51.6° inclination

while True:
    rate(60)

    # Earth rotation
    earth.rotate(angle=0.01, axis=vector(0,1,0))

    # Satellite orbit math with inclination
    x = orbit_radius * cos(angle)
    z = orbit_radius * sin(angle)
    y = orbit_radius * sin(inclination) * sin(angle)

    iss.pos = vector(x, y, z)

    angle += 0.03
