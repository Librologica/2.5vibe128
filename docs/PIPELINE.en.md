# 2.5D pipeline

## Version 1.0.0 scope

Standalone software renderer derived from the mono-portals backend of
3Dvibe64 1.4.0 Mode 8. This distribution promotes only the native single-level
demo-2 path with static openings. Polygon modes 1–7, unqualified multilevel
ports and VDC are not included. The historical `mode8` module/schema names
retain compatibility, not additional public graphics modes. There is no
`GraphicsMode=2.5` option.

## World to pixels

`tick → simulation → latched pose → DDA → profiles → back bitmap → publication`

1. IRQ accumulates ticks and updates FPS/text. Foreground consumes ticks,
   reads input and applies movement, collision or automatic waypoint pursuit.
2. One camera pose is latched per image; it cannot change during rendering.
   Simulation runs at approximately 50 logical ticks/s: one per PAL refresh,
   five per six NTSC refreshes. Real oscillators preserve a small difference
   from exactly 50 wall-clock ticks/s.
3. 32 primary rays traverse the map. Directions use 512 angles and offsets
   from a 60° perspective camera plane, not uncorrected uniform angular
   sampling. Camera is Q8.8; fixed-point DDA uses tabulated deltas, additions,
   comparisons and steps to the next X/Y grid boundary. Quadrant paths avoid
   repeated decisions. Corrected depth and projection lookups keep front
   walls straight; quantized angles have qualified geometric profile correction.
4. Wall owners/planes identify continuous surfaces. Group boundaries are
   interpolated/corrected; discontinuities and openings request adaptive fine
   samples. The 32 primary rays are not simply repeated over four columns:
   sloping edges are resolved at the final 128-logical-pixel width. Actual
   ray count depends on the pose.
5. For the supported openings, DDA finds upper-volume entry/exit and continues
   to the opaque wall. Front, lintel underside and wall beyond are projected.
   The map contract proves the supported layer bound; this is not a generic
   portal traversal renderer.
6. `select_strips` now prepares geometric bounds/profiles, not textures.
   `compose_screen` fills vertical bitmap bands. Logical columns are two
   physical pixels wide; four pigment samples occupy each byte. Full fills
   and exact masks handle partial edges. No mesh or triangle fill is performed.
7. Only a completed view becomes ready. IRQ publishes its back buffer at a
   safe boundary. Each FPS increment is a newly completed view, never a
   partial frame or an alternating-column update counted as a full image.

## Preserved optimizations

Layout-specialized generation, geometry/trigonometric tables, exact multiply
helpers/lookups, quadrant DDA, compatible sample reuse, discontinuity-only
refinement, owner-aware edge interpolation, direct ceiling stores and a
Y-register row counter. No Gouraud, normals, UV sampling or dynamic lighting.
Ceiling stipple is screen-anchored; wall pigment follows orientation.
Historical `strip`/`TEXTURED` labels do not describe active texture features.

Mathematical SMC belongs to foreground only; the renderer is not reentrant.
Handlers preserve A/X/Y and do not share geometry scratch. Do not render
from IRQ. Cost depends on crossings, discontinuities and visible openings,
not merely occupied-cell count. Average FPS is not a guaranteed minimum.
Independent simulation does not remove visual latency during long renders.

## Sources and changes

`src/mode8/asm/apertures-*.asm` are intentional complete source templates.
`src/mode8/build.py` validates/generates maps and owners; `src/native_builder.py`
adapts the platform; `src/native` contains bootstrap/IRQ; `src/kernels.py`
generates the two specialized fills. `mono.py` is the independent fixed oracle;
`trace.py` runs actual instructions through py65 without video contention.
Shared host helpers do not expose other backends: build accepts mono-portals
only. Complete per-demo ASM is also in `demos/source`. See MEMORY, MAPS,
ASSEMBLY-GUIDE and TESTING.

No textures, perspective-correct mapping, animated doors, 3D sprites,
mesh imports, dynamic lights, room-over-room or arbitrary slanted geometry.
Extending these limits requires separate implementation and qualification.
