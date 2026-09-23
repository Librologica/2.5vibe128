# Testing and qualification

Minimum build: Python 3.10+ and 64tass. Qualified Windows toolchain:
Python 3.13.14, 64tass 1.60.3243, VICE 3.10. No private paths required:
PATH / TASS64_EXE, VICE_X128 or VICE_XPLUS4 for the relevant executable.
Tools are not redistributed. Optional test dependencies:

```sh
python -m pip install -r requirements-tests.txt
python -B tests/test_release.py
python -B build.py --scene examples/demo2-original.json --run auto --out ../2.5vibe128-test
python -B scripts/check_cpu.py --build ../2.5vibe128-test
python -B scripts/qualify.py --build ../2.5vibe128-test --standard pal
python -B scripts/qualify.py --build ../2.5vibe128-test --standard ntsc
python -B scripts/check_visual.py --build ../2.5vibe128-test --standard pal --frame 3
```

Repeat for optimized map and interactive mode. Tools reject output inside SDK;
use new directories to repeat captures. unittest builds in external temporary
directories. Manifest lists every permanent file except itself; ZIP/manifest
hashes are supplied in the external delivery report.

After qualify.py on an interactive build, run
`python -B scripts/check_input.py --build ../interactive-build --standard pal`
and repeat with ntsc. This injects W/S/A/D and no-key states into VICE's
keyboard matrix, then checks actual native device reads without renderer
patches. Joystick support is present but not automatically exercised here.

Separate levels: parser/contracts; actual CPU instructions vs fixed oracle;
stock VICE with video contention/IRQ/simulation; physical pixels from complete
scanout with pose captured in the same run. py65 does not produce native FPS.
Qualification uses 120 views per combination, bitmap, camera, ticks, buffer
order, UI/font, palette, guards and registers. Do not match frame N across
different-FPS machines: match the actually latched pose.

Benchmark: 2 s warm-up, 20 emulated seconds, UI active, complete publications.
Warp accelerates host time only. C128 measures phi1 clocks; Plus/4 measures
TED master clocks. Raw counts are not comparable CPU cycles. FPS/p95 depend
on route segment; the initial window is not a whole tour or guaranteed minimum.

## Real hardware — not performed

Test stock PAL/NTSC hardware; record revision, loader and video output. Load
native PRG, check UI, borders, colors, FPS, double buffering, W/S/A/D and
joystick; cross both openings/corners and complete the tour. Record defects
and captures. Emulation is not a substitute; no hardware PASS is claimed.
C64 polygon suites are outside these SDKs and are not evidence for the ports.
