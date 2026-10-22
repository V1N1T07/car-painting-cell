from robodk.robolink import (Robolink, COLLISION_ON, COLLISION_OFF,
                             ITEM_TYPE_ROBOT, ITEM_TYPE_FRAME)

RDK = Robolink()
robot = RDK.Item('', ITEM_TYPE_ROBOT)
car = RDK.Item('car')
frame = RDK.Item('Car_Frame', ITEM_TYPE_FRAME)

print("Car pose in frame:", car.Pose().Pos())
print("Car_Frame pose:", frame.Pose().Pos())

def report(label):
    RDK.setCollisionActive(COLLISION_ON)
    n = RDK.Collisions()
    names = [i.Name() for i in RDK.CollisionItems()]
    print(label, "->", n, names)
    RDK.setCollisionActive(COLLISION_OFF)

RDK.setCollisionActive(COLLISION_OFF)     # allow moving anywhere

robot.setJoints(robot.JointsHome())
report("Home pose")

for name in ["R001", "R010", "R043"]:
    t = RDK.Item(name)
    print(name, "target position in Car_Frame:", t.Pose().Pos())
    robot.MoveJ(t)
    report("At " + name)

RDK.setCollisionActive(COLLISION_ON)