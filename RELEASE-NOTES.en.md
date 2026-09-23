# 2.5vibe128 1.0.0 — release notes

First standalone native mono-portals distribution. Original/new demo 2,
auto/interactive, PRGs and complete sources. Previous baselines preserved;
no new renderer optimization during packaging.

## Measured results

| Map | Run | Standard | FPS | Images / 20 s |
|---|---|---|---:|---:|
| original | auto | PAL | 6.55 | 131 |
| original | auto | NTSC | 6.20 | 124 |
| original | interactive | PAL | 5.05 | 101 |
| original | interactive | NTSC | 4.60 | 92 |
| optimized | auto | PAL | 7.45 | 149 |
| optimized | auto | NTSC | 7.05 | 141 |
| optimized | interactive | PAL | 4.55 | 91 |
| optimized | interactive | NTSC | 4.30 | 86 |

Stock VICE, initial 20-emulated-second window after 2-second warm-up.
Interactive is stationary at start, not a benchmarked manual tour. Values
belong to this package, not recycled prototype figures. 960 native views
compared per SDK: zero bitmap differences against the pose model. Source
and deterministic rebuilds verified. Sampled qualification does not cover
every possible trajectory. Real hardware has not been tested.

Ready for a GitHub repository, not uploaded. Geometry deliberately follows
the MAPS contracts. Complete demo ASM is included as requested; no dumps,
profilers, screenshots, temporary directories or historical experiments.
