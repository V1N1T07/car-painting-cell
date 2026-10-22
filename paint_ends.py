import numpy as np
import trimesh
from robodk.robolink import (Robolink, ITEM_TYPE_ROBOT, ITEM_TYPE_FRAME,
                             ITEM_TYPE_TOOL, ITEM_TYPE_TARGET, COLLISION_ON)
from robodk.robomath import transl, rotx, rotz, pi

STANDOFF = 200
APPROACH = 80
SPACING = 120
STEP = 100
REGIONS = {            # name: (x_start, x_end) in car coordinates
    "Hood":  (1500, 2200),
    "Trunk": (-2200, -1500),
}

RDK = Robolink()
RDK.setCollisionActive(COLLISION_ON)
robot = RDK.Item('', ITEM_TYPE_ROBOT)
frame = RDK.Item('Car_Frame', ITEM_TYPE_FRAME)
tool = RDK.Item('PaintGun', ITEM_TYPE_TOOL)
v = trimesh.load("car_scaled.stl").vertices

# Joint target used as the start/end pose of every program
home_joints = robot.JointsHome()
home = RDK.Item('Home', ITEM_TYPE_TARGET)
if not home.Valid():
    home = RDK.AddTarget('Home', frame, robot)
home.setAsJointTarget()
home.setJoints(home_joints)

def surf_z(x, y):
    m = (np.abs(v[:, 0] - x) < 80) & (np.abs(v[:, 1] - y) < 80)
    return v[m, 2].max() if m.any() else None

def clean(prog_name, prefix):
    p = RDK.Item(prog_name)
    if p.Valid():
        p.Delete()
    i = 1
    while True:
        t = RDK.Item('%s%03d' % (prefix, i), ITEM_TYPE_TARGET)
        if not t.Valid():
            break
        t.Delete()
        i += 1

def build(name, prefix, xa, xb, y0, y1, frame_pose, tool_rot):
    clean(name, prefix)
    robot.setJoints(home_joints)          # robot at Home before the car moves
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
    prog.MoveJ(home)
    for k, y in enumerate(np.arange(y0, y1 + 1, SPACING)):
        xs = np.arange(xa, xb + 1, STEP)
        if k % 2:
            xs = xs[::-1]
        pts = []
        for x in xs:
            z = surf_z(x, y)
            if z is not None:
                pts.append((x, y, z + STANDOFF))
        if len(pts) < 2:
            continue
        prog.MoveJ(target(pts[0][0], pts[0][1], pts[0][2] + APPROACH))
        for p in pts:
            prog.MoveL(target(*p))
        prog.MoveL(target(pts[-1][0], pts[-1][1], pts[-1][2] + APPROACH))
    prog.MoveJ(home)
    robot.setJoints(home_joints)
    print(name, ":", n[0], "targets; frame pose", frame_pose.Pos())
    print("   check:", prog.Update(COLLISION_ON))

for label, (xa, xb) in REGIONS.items():
    xc = (xa + xb) / 2
    sel = v[(v[:, 0] > xa) & (v[:, 0] < xb)]
    ymax = min(abs(sel[:, 1].min()), sel[:, 1].max()) - 120
    build("Paint_%s_Near" % label, label[0] + "n", xa, xb, -ymax, 0,
          transl(-xc, 0, 0), rotx(pi))
    build("Paint_%s_Far" % label, label[0] + "f", xa, xb, 120, ymax,
          transl(xc, 0, 0) * rotz(pi), rotz(pi) * rotx(pi))

robot.setJoints(home_joints)
frame.setPose(transl(0, 0, 0))
print("Done. Robot at Home, Car_Frame reset to zero.")