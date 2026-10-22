import numpy as np
import trimesh
from robodk.robolink import (Robolink, ITEM_TYPE_ROBOT, ITEM_TYPE_FRAME,
                             ITEM_TYPE_TOOL, ITEM_TYPE_TARGET, COLLISION_ON)
from robodk.robomath import transl, rotx, rotz, pi

STANDOFF = 200
APPROACH = 100
VIA_OUT = 400                  # extra distance from the car for the via-point
VIA_UP = 300                   # extra height for the via-point
SPACING = 100
STEP = 100
X_RANGE = (-1000, 1000)
Z_RANGE = (650, 950)           # lower strokes hit the pedestal, so start at 650

RDK = Robolink()
RDK.setCollisionActive(COLLISION_ON)
robot = RDK.Item('', ITEM_TYPE_ROBOT)
frame = RDK.Item('Car_Frame', ITEM_TYPE_FRAME)
tool = RDK.Item('PaintGun', ITEM_TYPE_TOOL)
v = trimesh.load("car_scaled.stl").vertices
home_joints = robot.JointsHome()
home = RDK.Item('Home', ITEM_TYPE_TARGET)
if not home.Valid():
    home = RDK.AddTarget('Home', frame, robot)
    home.setAsJointTarget()
    home.setJoints(home_joints)

def side_y(x, z, sign):
    m = (np.abs(v[:, 0] - x) < 60) & (np.abs(v[:, 2] - z) < 60)
    if not m.any():
        return None
    return v[m, 1].min() if sign < 0 else v[m, 1].max()

def clean(prog_name, prefix):
    p = RDK.Item(prog_name)
    if p.Valid():
        p.Delete()
    t = RDK.Item(prefix + 'Via', ITEM_TYPE_TARGET)
    if t.Valid():
        t.Delete()
    i = 1
    while True:
        t = RDK.Item('%s%03d' % (prefix, i), ITEM_TYPE_TARGET)
        if not t.Valid():
            break
        t.Delete()
        i += 1

def build(name, prefix, sign, frame_pose, tool_rot):
    clean(name, prefix)
    robot.setJoints(home_joints)
    frame.setPose(frame_pose)
    robot.setPoseFrame(frame)
    robot.setPoseTool(tool)
    prog = RDK.AddProgram(name, robot)
    prog.setPoseFrame(frame)
    prog.setPoseTool(tool)
    n = [0]
    def target(x, y, z):
        n[0] += 1
        t = RDK.AddTarget('%s%03d' % (prefix, n[0]), frame, robot)
        t.setPose(transl(x, y, z) * tool_rot)
        t.setAsCartesianTarget()
        return t
    strokes = []
    for k, z in enumerate(range(Z_RANGE[0], Z_RANGE[1] + 1, SPACING)):
        xs = np.arange(X_RANGE[0], X_RANGE[1] + 1, STEP)
        if k % 2:
            xs = xs[::-1]
        pts = []
        for x in xs:
            y = side_y(x, z, sign)
            if y is not None:
                pts.append((x, y + sign * STANDOFF, z))
        if len(pts) >= 2:
            strokes.append(pts)
    a = strokes[0][0]
    via = RDK.AddTarget(prefix + 'Via', frame, robot)
    via.setPose(transl(a[0], a[1] + sign * (APPROACH + VIA_OUT), a[2] + VIA_UP)
                * tool_rot)
    via.setAsCartesianTarget()
    prog.MoveJ(home)
    prog.MoveJ(via)
    for pts in strokes:
        a, b = pts[0], pts[-1]
        prog.MoveJ(target(a[0], a[1] + sign * APPROACH, a[2]))
        for p in pts:
            prog.MoveL(target(*p))
        prog.MoveL(target(b[0], b[1] + sign * APPROACH, b[2]))
    prog.MoveJ(via)
    prog.MoveJ(home)
    robot.setJoints(home_joints)
    print(name, ":", n[0], "targets")
    print("   check:", prog.Update(COLLISION_ON))

build("Paint_Side_Near", "Sn", -1, transl(0, 500, 0), rotx(-pi / 2))
build("Paint_Side_Far", "Sf", +1, transl(0, 500, 0) * rotz(pi),
      rotz(pi) * rotx(-pi / 2))

robot.setJoints(home_joints)
frame.setPose(transl(0, 0, 0))
print("Done. Robot at Home, Car_Frame reset to zero.")