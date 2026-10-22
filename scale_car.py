import numpy as np
import trimesh

# Load the GLB as a single mesh
mesh = trimesh.load("tesla_2018_model_3.glb", force="mesh")
print("Original size:", mesh.extents)

# GLB is Y-up, RoboDK is Z-up: rotate 90 degrees about X
mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))

# Make sure the length runs along X
if mesh.extents[1] > mesh.extents[0]:
    mesh.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 0, 1]))

# Scale so the length is 4800 mm
mesh.apply_scale(4800.0 / mesh.extents[0])

# Centre on X/Y and put the wheels on the floor (Z = 0)
mesh.apply_translation([
    -(mesh.bounds[0][0] + mesh.bounds[1][0]) / 2,
    -(mesh.bounds[0][1] + mesh.bounds[1][1]) / 2,
    -mesh.bounds[0][2],
])

print("New size (X length, Y width, Z height) in mm:", mesh.extents)
mesh.export("car_scaled.stl")
print("Saved car_scaled.stl")