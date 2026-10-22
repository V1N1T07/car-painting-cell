import numpy as np
import trimesh
from trimesh.transformations import translation_matrix as T
from robodk.robolink import (Robolink, ITEM_TYPE_ROBOT, ITEM_TYPE_FRAME,
                             ITEM_TYPE_TOOL, ITEM_TYPE_TARGET)
from robodk.robomath import transl, rotx, pi
import os

STANDOFF = 200     # mm between nozzle and paint surface
APPROACH = 80      # mm above the stroke for approach/retreat
SPACING = 120      # mm between strokes
STEP = 100         # mm between points along a stroke

RDK = Robolink()

# --- Remove the previous attempt so nothing is duplicated ---
old = RDK.Item('Paint_Roof')
if old.Valid():
    old.Delete()
i = 1
while True:
    t = RDK.Item('R%03d' % i, ITEM_TYPE_TARGET)
    if not t.Valid():
        break
    t.Delete()
    i += 1

# --- Pedestal under the robot (500 mm high) ---
if not RDK.Item('Pedestal').Valid():
    ped = trimesh.creation.box(extents=[700, 700, 500],
                               transform=T([0, -1900, 250]))
    ped.export("pedestal.stl")
    p = RDK.AddFile(os.path.abspath("pedestal.stl"))
    p.setName("Pedestal")
    p.setColor([0.35, 0.35, 0.4, 1.0])

# --- Read the real roof shape from the scaled model ---
mesh = trimesh.load("car_scaled.stl")
v = mesh.vertices
zmax = v[:, 2].max()
roof = v[v[:, 2] > 0.93 * zmax]
x_min, x_max = roof[:, 0].min() + 150, roof[:, 0].max() - 150
y_min = roof[:, 1].min() + 100
y_max = 0
print("Roof height:", round(zmax), "mm; X:", round(x_min), round(x_max),
      "; Y:", round(y_min), round(y_max))

def roof_z(x, y):
    m = (np.abs(v[:, 0] - x) < 80) & (np.abs(v[:, 1] - y) < 80)
    return v[m, 2].max() if m.any() else zmax

robot = RDK.Item('', ITEM_TYPE_ROBOT)
frame = RDK.Item('Car_Frame', ITEM_TYPE_FRAME)
tool = RDK.Item('PaintGun', ITEM_TYPE_TOOL)
robot.setPoseFrame(frame)
robot.setPoseTool(tool)

prog = RDK.AddProgram('Paint_Roof', robot)
prog.setPoseFrame(frame)
prog.setPoseTool(tool)

n = [0]
def target(x, y, z):
    n[0] += 1
    t = RDK.AddTarget('R%03d' % n[0], frame, robot)
    t.setPose(transl(x, y, z) * rotx(pi))
    t.setAsCartesianTarget()
    return t

ys = np.arange(y_min, y_max + 1, SPACING)
for k, y in enumerate(ys):
    xs = np.arange(x_min, x_max + 1, STEP)
    if k % 2:
        xs = xs[::-1]
    pts = [(x, y, roof_z(x, y) + STANDOFF) for x in xs]
    prog.MoveJ(target(pts[0][0], pts[0][1], pts[0][2] + APPROACH))
    for pt in pts:
        prog.MoveL(target(*pt))
    prog.MoveL(target(pts[-1][0], pts[-1][1], pts[-1][2] + APPROACH))

print("Program Paint_Roof created with", n[0], "targets")
print("Check result:", prog.Update())