import numpy as np
import trimesh
from robodk.robolink import (Robolink, ITEM_TYPE_ROBOT, ITEM_TYPE_FRAME,
                             ITEM_TYPE_TOOL, ITEM_TYPE_TARGET, COLLISION_ON)
from robodk.robomath import transl, rotx, rotz, pi

STANDOFF = 200
APPROACH = 80
SPACING = 120
STEP = 100

RDK = Robolink()
RDK.setCollisionActive(COLLISION_ON)

# Remove any previous attempt of this program
old = RDK.Item('Paint_Roof_Far')
if old.Valid():
    old.Delete()
i = 1
while True:
    t = RDK.Item('F%03d' % i, ITEM_TYPE_TARGET)
    if not t.Valid():
        break
    t.Delete()
    i += 1

# Roof shape from the scaled model
mesh = trimesh.load("car_scaled.stl")
v = mesh.vertices
zmax = v[:, 2].max()
roof = v[v[:, 2] > 0.93 * zmax]
x_min, x_max = roof[:, 0].min() + 150, roof[:, 0].max() - 150
y_max = roof[:, 1].max() - 100
y_min = 120                      # the half not painted by Paint_Roof
xc = (x_min + x_max) / 2

def roof_z(x, y):
    m = (np.abs(v[:, 0] - x) < 80) & (np.abs(v[:, 1] - y) < 80)
    return v[m, 2].max() if m.any() else zmax

robot = RDK.Item('', ITEM_TYPE_ROBOT)
frame = RDK.Item('Car_Frame', ITEM_TYPE_FRAME)
tool = RDK.Item('PaintGun', ITEM_TYPE_TOOL)

# Turntable pose: rotate the car 180 deg and shift it so the unpainted
# half of the roof sits where the first half was
frame.setPose(transl(2 * xc, 0, 0) * rotz(pi))

robot.setPoseFrame(frame)
robot.setPoseTool(tool)
prog = RDK.AddProgram('Paint_Roof_Far', robot)
prog.setPoseFrame(frame)
prog.setPoseTool(tool)

n = [0]
def target(x, y, z):
    n[0] += 1
    t = RDK.AddTarget('F%03d' % n[0], frame, robot)
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

print("Paint_Roof_Far created with", n[0], "targets; car shift X =", round(2 * xc))
print("Check result:", prog.Update(COLLISION_ON))