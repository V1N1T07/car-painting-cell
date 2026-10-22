# Robotic Car Painting Cell (RoboDK)

- **Name:** Vinit Agarwal
- **Software used:** RoboDK (Windows) with Python 3.13 and the RoboDK API
- **Robot selected:** ABB IRB 4600-20/2.50

This is my submission for the Yuktii AI Labs Robotics Simulation Intern practical assessment. One industrial robot paints a Tesla Model 3 mesh (scaled to 4,800 mm long) inside a small painting cell. The station, the paths and the checks are all built with Python scripts, so the project can be rebuilt from this repository.

## What it does

- A cell with a floor, two side walls, a pedestal, the robot, a spray gun and the car.
- Six painting programs: roof, hood and trunk, each split into a near half and a far half.
- Zigzag strokes that follow the shape of the car body: 200 mm stand-off, 120 mm between strokes, tool pointing straight down.
- RoboDK collision checking, tested by lifting the car into the gun (collision at 250 mm, none at 0 and 100 mm).
- All six programs report a valid ratio of 1.0 and no collisions in RoboDK's program check.

The side panels are not finished. See "Known issues" below.

## Repository contents

```
scripts/
  scale_car.py          prepares the car: rotates, scales to 4800 mm, centres, saves car_scaled.stl
  make_cell.py          creates the floor and the two walls
  make_tool.py          creates the paint gun and its tool point (run once)
  fix_gun.py            moves the gun model 300 mm back along the tool axis
  paint_roof.py         adds the pedestal and builds Paint_Roof
  paint_roof_far.py     builds Paint_Roof_Far
  paint_ends.py         builds the four hood and trunk programs
  paint_sides.py        side panel attempt (not verified, see Known issues)
  check_collisions.py   runs the RoboDK program check on Paint_Roof
  collision_test2.py    lifts the car in steps and prints the collisions
  diagnostics/         scripts used to find the problems (kept as a record, not meant to be re-run)
screenshots/
docs/Technical_Report.pdf
requirements.txt
```

The car mesh (`car_scaled.stl`), the original GLB file and the `.rdk` station are too large for this repository. They are in the Google Drive folder from my submission email, under `Simulation_Files/`.

## Requirements

- RoboDK for Windows, with a license that allows API calls
- Python 3.13

```
pip install -r requirements.txt
```

## How to rebuild the station

1. Put your car file in the scripts folder, named `tesla_2018_model_3.glb`, and run `python scale_car.py`. It creates `car_scaled.stl` (about 4800 x 2235 x 1440 mm).
2. In RoboDK, load the **ABB IRB 4600-20/2.50** from the online library. Set its base frame to X 0, Y -1900, Z 500, Rz 90.
3. Add a reference frame named **Car_Frame** at the origin. Drag `car_scaled.stl` into RoboDK, rename it `car` and place it under Car_Frame.
4. Run `python make_cell.py`. Drag **Floor** and **Walls** to the station root so they do not move with Car_Frame.
5. Run `python make_tool.py` once, then `python fix_gun.py`. The last line it prints should be `Gun position after: [0.0, 0.0, -300.0]`.
6. Open Tools, then Collision map. Tick the gun against the car, floor, walls, pedestal and robot joints 1 to 4. Leave the base against the pedestal, and the gun against joints 5 and 6, switched off. These pairs are in contact by design.
7. Run `python paint_roof.py` (it also adds the pedestal), then `python paint_roof_far.py`, then `python paint_ends.py`.
8. Run `python check_collisions.py` to check Paint_Roof. Each build script prints its own check result for the program it creates.

RoboDK must be open with the station loaded while the scripts run.

## Programs and car positions

Each program expects Car_Frame in a certain place. Set the X value and the Rz rotation in Car_Frame, then run the program.

| Program | Car_Frame X (mm) | Car_Frame Rz | Targets | Valid ratio | Collisions |
|---|---|---|---|---|---|
| Paint_Roof | 0 | 0 | 85 | 1.0 | none |
| Paint_Roof_Far | 977 | 180 | 68 | 1.0 | none |
| Paint_Hood_Near | -1850 | 0 | 80 | 1.0 | none |
| Paint_Hood_Far | 1850 | 180 | 70 | 1.0 | none |
| Paint_Trunk_Near | 1850 | 0 | 80 | 1.0 | none |
| Paint_Trunk_Far | -1850 | 180 | 70 | 1.0 | none |

## How the paths are made

For every stroke the script takes each (x, y) point, finds the highest mesh vertex inside an 80 mm window and adds the 200 mm stand-off. Strokes run back and forth, with an approach and retreat 80 mm above the ends. The 120 mm spacing is my own choice and is not based on a real spray pattern. The hood and trunk programs begin and end at a Home joint position.

## Known issues

- **Side panels are not completed.** With the gun pointing sideways, the arm hits its own pedestal around the middle of the door, and the swing from Home passes through the car. `paint_sides.py` is a newer version (strokes start at 650 mm and a via-point is added) that I could not run, because RoboDK's free license started blocking API calls. Treat it as untested.
- The tool points straight down everywhere, so on the sloped hood and trunk it is not normal to the surface.
- The car does not change colour and paint thickness is not simulated.
- The free RoboDK license allows only a few saves of the station, so the scripts are the main record of the project.

## Credits

- Car model: Tesla Model 3 mesh (https://sketchfab.com/3d-models/tesla-2018-model-3-5ef9b845aaf44203b6d04e2c677e444f).
- Simulation: RoboDK. Scripts use numpy and trimesh.
