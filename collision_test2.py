from robodk.robolink import (Robolink, COLLISION_ON, COLLISION_OFF,
                             ITEM_TYPE_ROBOT)
from robodk.robomath import transl

RDK = Robolink()
robot = RDK.Item('', ITEM_TYPE_ROBOT)
car = RDK.Item('car')

car.setPose(transl(0, 0, 0))
RDK.setCollisionActive(COLLISION_OFF)
robot.MoveJ(RDK.Item('R010'))
RDK.setCollisionActive(COLLISION_ON)

for z in (0, 100, 250, 600):
    car.setPose(transl(0, 0, z))
    print("Car raised", z, "mm ->", RDK.Collisions(),
          [i.Name() for i in RDK.CollisionItems()])

car.setPose(transl(0, 0, 0))