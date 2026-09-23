# 2.5vibe128 1.0.0

Native **Commodore 128 / VIC-IIe** SDK derived solely from the 3Dvibe64 2.5D pipeline.
Single-level environments with two static openings, lintels and thickness;
128×144 logical (256×144 physical) multicolor bitmap, double buffering,
UI/FPS, PAL/NTSC, automatic tour and W/S+A/D navigation, joystick port 2.

Four demos in `demos`: original/optimized × auto/interactive. Complete ASM
in `demos/source`, JSON in `examples`, generator in `build.py` and `src`.
Both maps share start/route. This is DDA raycasting, not a polygon engine;
there is no active texture mapping.

## Usage

Requires Python 3.10+ and 64tass, on PATH or via `TASS64_EXE`. VICE is not
required to build. Always use a new output directory outside the SDK.

```sh
python -B build.py --scene examples/demo2-optimized.json --run interactive --out ../2.5vibe128-build
x128 -default +go64 -40col -pal -autostartprgmode 1 ../2.5vibe128-build/2.5vibe128.prg
```

W/S move, A/D turn. Automatic: `--run auto`. Reset to exit. Replace `-pal`
with `-ntsc` to test NTSC. Real hardware has not been tested.

## Documentation and licenses

[Quickstart](QUICKSTART.en.md) · [Pipeline](docs/PIPELINE.en.md) · [Mappe / maps](docs/MAPS.en.md) · [Assembly](docs/ASSEMBLY-GUIDE.en.md) · [Memoria / memory](docs/MEMORY.en.md) · [Test](TESTING.en.md) · [Release](RELEASE-NOTES.en.md).

Code/data: **PolyForm Noncommercial 1.0.0**, not MIT. Documentation:
**CC BY-NC 4.0**. Copyright 2026 librologica.digital; attribution retained
in LICENSE, LICENSE-DOCUMENTATION.md and NOTICE.md. No automatic GitHub
upload: this is the repository-ready distribution.
