# Quickstart — 2.5vibe128

Extract the ZIP. No other 3Dvibe64 checkout is required. To play, use the
four demos/ PRGs without building. Select x128, Commodore 128 / VIC-IIe, stock machine
and PAL/NTSC video standard.

C128: native 40-column mode, **not GO64**, VIC-IIe output.
BASIC 7 PRG at $1C01, SYS 7181.

Hardware: load as BASIC at its native address, then RUN. For example
`LOAD"name",8` with a compatible device; check your loader procedure. Do not
force the C64 $0801 address. Hardware operation is not yet qualified.

```sh
python -B build.py --scene examples/demo2-original.json --validate-only
python -B build.py --scene examples/demo2-original.json --run auto --out ../2.5vibe128-original-auto
python -B build.py --scene examples/demo2-original.json --run interactive --out ../2.5vibe128-original-interactive
python -B build.py --scene examples/demo2-optimized.json --run auto --out ../2.5vibe128-optimized-auto
python -B build.py --scene examples/demo2-optimized.json --run interactive --out ../2.5vibe128-optimized-interactive
```

Output directories must be new and outside SDK. Build emits PRG, ASM,
labels, listing, log and scene; intermediates stay in output. Validation-only
requires no assembler and writes nothing. No GraphicsMode, FOV, palette,
viewport or camera-override options are exposed.
