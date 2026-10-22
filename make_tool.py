import os
import trimesh
from trimesh.transformations import translation_matrix as T
from robodk.robolink import Robolink, ITEM_TYPE_ROBOT
from robodk.robomath import transl

# Gun body: cylinder from Z=0 to 200, then a cone narrowing to the nozzle at Z=300
body = trimesh.creation.cylinder(radius=40, height=200, transform=T([0, 0, 100]))
nozzle = trimesh.creation.cone(radius=40, height=100, transform=T([0, 0, 200]))
gun = trimesh.util.concatenate([body, nozzle])
gun.export("paint_gun.stl")

RDK = Robolink()
robot = RDK.Item('', ITEM_TYPE_ROBOT)

# Tool with its TCP at the nozzle tip (300 mm along the flange Z axis)
tool = robot.AddTool(transl(0, 0, 300), 'PaintGun')

# Load the gun geometry into the tool
geo = RDK.AddFile(os.path.abspath("paint_gun.stl"), tool)
geo.setColor([0.9, 0.1, 0.1, 1.0])
print("Paint gun added")