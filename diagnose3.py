from robodk.robolink import (Robolink, COLLISION_ON, COLLISION_OFF,
                             ITEM_TYPE_ROBOT, ITEM_TYPE_TOOL)

RDK = Robolink()
robot = RDK.Item('', ITEM_TYPE_ROBOT)
tool = RDK.Item('PaintGun', ITEM_TYPE_TOOL)
gun = RDK.Item('paint_gun')

print("Gun position in tool frame:", gun.Pose().Pos())

RDK.setCollisionActive(COLLISION_OFF)
robot.MoveJ(RDK.Item('R001'))
RDK.setCollisionActive(COLLISION_ON)

print("Collisions at R001:", RDK.Collisions(),
      [i.Name() for i in RDK.CollisionItems()])
print("Tool (TCP) absolute position:", tool.PoseAbs().Pos())
print("Gun absolute pose:")
print(gun.PoseAbs())