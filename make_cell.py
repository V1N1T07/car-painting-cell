import os
import trimesh
from trimesh.transformations import translation_matrix as T
from robodk.robolink import Robolink

# Floor: top surface at Z = 0
floor = trimesh.creation.box(extents=[10000, 6000, 100],
                             transform=T([0, 0, -50]))
floor.export("floor.stl")

# Two long side walls (ends left open for car entry/exit)
w1 = trimesh.creation.box(extents=[10000, 100, 3500],
                          transform=T([0, 3050, 1750]))
w2 = trimesh.creation.box(extents=[10000, 100, 3500],
                          transform=T([0, -3050, 1750]))
walls = trimesh.util.concatenate([w1, w2])
walls.export("walls.stl")

RDK = Robolink()
f = RDK.AddFile(os.path.abspath("floor.stl"))
f.setName("Floor")
f.setColor([0.55, 0.55, 0.58, 1.0])

w = RDK.AddFile(os.path.abspath("walls.stl"))
w.setName("Walls")
w.setColor([0.8, 0.85, 0.9, 0.3])
print("Cell added")