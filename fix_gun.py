from robodk.robolink import Robolink
from robodk.robomath import transl

RDK = Robolink()
gun = RDK.Item('paint_gun')
print("Gun position before:", gun.Pose().Pos())
gun.setPose(transl(0, 0, -300))
print("Gun position after:", gun.Pose().Pos())