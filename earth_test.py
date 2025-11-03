from vpython import sphere, vector, rate, textures

earth = sphere(
    pos=vector(0,0,0),
    radius=1,
    texture=textures.earth
)

while True:
    rate(60)
    earth.rotate(angle=0.01, axis=vector(0,1,0))
