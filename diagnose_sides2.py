from robodk.robolink import (Robolink, COLLISION_ON, COLLISION_OFF,
                             ITEM_TYPE_ROBOT, ITEM_TYPE_FRAME)
from robodk.robomath import transl

RDK = Robolink()
robot = RDK.Item('', ITEM_TYPE_ROBOT)
frame = RDK.Item('Car_Frame', ITEM_TYPE_FRAME)
home = robot.JointsHome().list()

frame.setPose(transl(0, 500, 0))       # same car shift as Paint_Side_Near
RDK.setCollisionActive(COLLISION_OFF)
robot.setJoints(home)

# 1) Which side targets collide, and with what?
bad, unreachable = {}, []
for i in range(1, 116):
    t = RDK.Item('Sn%03d' % i)
    try:
        robot.MoveJ(t)
    except Exception:
        unreachable.append(i)
        continue
    RDK.setCollisionActive(COLLISION_ON)
    if RDK.Collisions():
        bad[i] = sorted(set(x.Name() for x in RDK.CollisionItems()))
    RDK.setCollisionActive(COLLISION_OFF)

print("Unreachable targets:", unreachable)
print("Colliding targets:", sorted(bad))
print("Items involved:", sorted(set(n for v in bad.values() for n in v)))

# 2) Where does the swing from Home to Sn001 collide?
robot.setJoints(home)
RDK.setCollisionActive(COLLISION_OFF)
robot.MoveJ(RDK.Item('Sn001'))
goal = robot.Joints().list()
print("Home to Sn001 swing:")
for k in range(0, 11):
    f = k / 10.0
    robot.setJoints([a + (b - a) * f for a, b in zip(home, goal)])
    RDK.setCollisionActive(COLLISION_ON)
    print("  %3d%% ->" % (f * 100), RDK.Collisions(),
          sorted(set(x.Name() for x in RDK.CollisionItems())))
    RDK.setCollisionActive(COLLISION_OFF)

RDK.setCollisionActive(COLLISION_ON)
robot.setJoints(home)
frame.setPose(transl(0, 0, 0))