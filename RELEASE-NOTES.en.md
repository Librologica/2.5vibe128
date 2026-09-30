# 2.5vibe128 1.1.0 — release notes

C64 1.5.5 lintel fixes promoted into the fixed-map renderer; native video/clock
retained. Six silent demos, PRGs and complete assembly sources: original demo 2,
optimized demo 2 and infinite world, each auto/interactive. Infinite generation
has a separate build entry, not a relaxed fixed-map contract. Previous releases
and C64 sources remain intact.

## Packaged PRGs: measured results

| Map | Run | Video | FPS | Images / 20 s |
|---|---|---|---:|---:|
| original | auto | PAL | 6.55 | 131 |
| original | auto | NTSC | 6.20 | 124 |
| original | interactive | PAL | 5.05 | 101 |
| original | interactive | NTSC | 4.60 | 92 |
| optimized | auto | PAL | 7.45 | 149 |
| optimized | auto | NTSC | 7.05 | 141 |
| optimized | interactive | PAL | 4.55 | 91 |
| optimized | interactive | NTSC | 4.30 | 86 |
| infinite | auto | PAL | 3.80 | 76 |
| infinite | auto | NTSC | 3.30 | 66 |
| infinite | interactive | PAL | 4.55 | 91 |
| infinite | interactive | NTSC | 6.00 | 120 |

Stock VICE 3.10. Twenty emulated seconds after two-second warm-up; UI active,
only new complete publications counted. Interactive is stationary at start,
not a manual-tour benchmark. Infinite startup seeds vary with boot timing:
these worlds differ across platforms/standards, so do not derive controlled
speedup percentages or guaranteed minimum FPS from this table.

## Controlled seed: infinite automatic

Seed `0x12345678`, same 18-cell raw cutoff and 128×144 viewport.

| Video | FPS | Images / 20 s |
|---|---:|---:|
| PAL | 3.20 | 64 |
| NTSC | 2.95 | 59 |

Seed fixes geometry; differing native frame cadence still samples different
poses. C128 measures phi1 clocks, Plus/4 TED master clocks, not directly
comparable CPU instruction cycles. Raw evidence is kept outside the SDK.

## Qualification

Per SDK: **1,440 native views** (six demos × PAL/NTSC × 120), plus **240**
fixed-seed views, **128** instruction/model fixed-map views, **24** complete
physical scanouts and **30** keyboard cases. Zero bitmap differences at matched
poses and zero physical viewport/margin differences. Infinite world RAM matches
host generation. Fonts, palette, UI, split, native registers and buffer order
checked. Reproducible builds/source snapshots and package manifests are checked.

Physical tests found a Plus/4-only infinite-demo margin artifact: the reclaimed
font half could be read before the bitmap split. Zeroing unused color-matrix
rows below the UI fixes it without changing the active viewport or geometry.

No music/player/audio assets. Sampled qualification is not exhaustive over all
seeds/trajectories. **Real hardware and physical joystick untested.**
No unrelated renderer optimization. Packaging does not publish to GitHub.
