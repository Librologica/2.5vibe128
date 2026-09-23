# Preparing maps

Start from complete examples: demo2-original (96 owners) or demo2-optimized
(44 owners). Same route and starting pose; different geometry. The latter
is not random. Each map is a complete 32×32 array, indexed by `32*y+x`,
origin at the upper left, X rightward and Y downward. PLANS.md is generated
from the same data.

The JSON root contains exactly `scene` and `navigation`. Duplicate/unknown
keys, null arrays and booleans used as integers are rejected.

| scene field | Contract |
|---|---|
| schema | `3dvibe64-mode8-map-v1` |
| size | `[32,32]` |
| solid | 1024 integers, 0 empty / 1 solid; all boundary cells solid |
| floor | 1024 zeroes |
| ceiling | 1024 integers: 96 except the four opening cells at 64 |
| initial | `[5939,2509,469,32,0]`, fixed |
| eyeHeight | 32 |
| playerHeight | optional, default and only accepted value 48 |
| heightUnit | optional, only `1/32 cell` |
| doors | exactly `[[10,14,11,14],[22,14,23,14]]` |
| ramps | `[]` |
| notes | optional string, no runtime effect |

Row y=14 is solid except x=10,11,22,23. Openings are two cells wide, one
cell deep and 64/32=2 cells tall; room ceiling is 96/32=3 cells, eye height
32/32=1 cell. Lintels remain visible. Openings are static, not animated doors.
Do not alter these slots, elevations or thickness to bypass validation.
At most 96 contiguous exposed boundary segments/owners plus a sentinel are
supported. Owners/planes are generated from solid, not authored manually.

Camera/waypoints are already integer Q8.8 in JSON: one cell is 256; cell
center `(x,y)` is `(256*x+128,256*y+128)`. Yaw 0..511: 0=+Y,128=+X,
256=−Y,384=−X. Fixed 60° FOV/horizon, no pitch. The last two initial values
are integer eye elevation and fraction/256. `navigation` contains camera
equal to the first three initial values and nodes as Q8.8 pairs. This release
requires the original camera and all 193 waypoints unchanged; it is not a
general editor or pathfinder.

Solid/empty cells may change away from borders, separator, start and route.
The builder simulates 30,000 ticks and rejects a blocked/incomplete automatic
tour, also when building interactive mode. Auto collision radius is 224/256
cell, manual 48/256 with X/Y sliding. Manual movement has no 70%-wall-view cap.

Workflow: copy demo2-optimized.json outside SDK, edit solid while preserving
constraints, then run `build.py --scene ../my-map.json --validate-only`.
Validation PASS is not exhaustive coverage of every camera pose. Test the
interactive PRG, corners and every opening too.

Main errors: DOCUMENT/FORMAT/SCHEMA (format), BORDER (open boundary),
INITIAL_POSE/TEMPLATE_CAMERA (camera), MONO_NAV (changed route),
MONO_APERTURES/MONO_SEPARATOR/MONO_QUOTE (openings/heights), OWNER_CAPACITY
(too many segments), AUTO_COLLISION/AUTO_TOUR (route), NATIVE_BACKEND
(unsupported backend), LOW_BUDGET (memory overlap). Quality/precision is
never silently reduced. Palette, FOV and viewport are not public scene fields.
