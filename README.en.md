# 2.5vibe128 1.1.0

Native **Commodore 128 / VIC-IIe** SDK, derived solely from the 3Dvibe64 2.5D pipeline.
128×144 logical (256×144 physical) multicolor bitmap, double buffering,
UI/FPS, PAL/NTSC, automatic exploration or W/S+A/D navigation.

Version 1.1.0 promotes the C64 1.5.5 lintel corrections: reset camera-inside
state after upper-volume exit and refine edges when front planes differ.
The native video, memory and clock strategy is retained.

**Six silent demos**: original demo 2, optimized demo 2 and the new continuous
infinite world, each automatic and interactive. PRGs and complete ASM snapshots
are in `demos`; host generators/templates in `src`. The two fixed maps share
their starting point/route. The infinite demo continuously generates rooms,
doors and full-height openings, with a variable startup seed.

The fixed-map SDK retains its strict mono-portals contract (two openings).
The infinite demo uses a separate specialized build; it does not implicitly
relax that contract. This is DDA raycasting, not a polygon engine or texture mapper.

## Build and run

Python 3.10+ and 64tass are required (PATH or `TASS64_EXE`).
Always use a new output directory outside the SDK.

```sh
python -B build.py --scene examples/demo2-optimized.json --run interactive --out ../2.5vibe128-build
x128 -default +go64 -40col -pal -autostartprgmode 1 ../2.5vibe128-build/2.5vibe128.prg
python -B build_infinite.py --run auto --out ../2.5vibe128-infinite
x128 -default +go64 -40col -pal -autostartprgmode 1 ../2.5vibe128-infinite/2.5vibe128-infinite-auto.prg
```

W/S forward/back, A/D turn; joystick port 2 is implemented. Reset to exit.
Use `--run interactive` for manual exploration; `--seed 0x12345678` selects
a reproducible infinite world. Replace `-pal` with `-ntsc` for NTSC.
No music, player or audio asset is distributed. Real hardware is untested.

## Documentation and licenses

[Italiano](README.it.md) · [Quickstart](QUICKSTART.en.md) ·
[Pipeline](docs/PIPELINE.en.md) · [Maps](docs/MAPS.en.md) ·
[Infinite world](docs/INFINITE.en.md) · [Assembly](docs/ASSEMBLY-GUIDE.en.md) ·
[Memory](docs/MEMORY.en.md) · [Tests](TESTING.en.md) · [Release](RELEASE-NOTES.en.md).

Code/data: **PolyForm Noncommercial 1.0.0**, not MIT.
Documentation: **CC BY-NC 4.0**. Copyright 2026 librologica.digital.
See LICENSE, LICENSE-DOCUMENTATION.md and NOTICE.md.
Packaging does not publish to GitHub.
