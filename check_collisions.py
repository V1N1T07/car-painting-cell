from robodk.robolink import Robolink, COLLISION_ON

RDK = Robolink()
RDK.setCollisionActive(COLLISION_ON)
prog = RDK.Item('Paint_Roof')
print("Collision check:", prog.Update(COLLISION_ON))