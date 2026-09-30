# Continuous infinite-world demo

## Build contract

This is a separately built, specialized demo, not an extension of the fixed-map
JSON parser. Use `build_infinite.py --run auto|interactive --out NEW_DIRECTORY`.
The output directory must be outside the SDK and must not exist.
Optional `--seed` accepts an integer in 0..4294967295, decimal or 0x hexadecimal.
Omitting it samples native timer/raster state at startup. This is not a source of
cryptographic randomness, and identical boot timing can repeat a seed.

The two published PRGs use the variable-startup-seed path. To compare platforms
or reproduce a world, build both with the same explicit seed. Seed and traversal
direction determine different parts of one coherent world; walking back regenerates
the same geometry. No archive of visited rooms is kept. Coordinates are 32 bits
per axis, with defined wrap: “infinite” means continuously generated exploration,
not a mathematically unbounded stored map.

## Geometry and navigation

- One level; orthogonal walls, static doors with lintels, full-height openings.
- Deterministic hashing of global coordinates and seed; no repeated fixed map.
- 16-cell blocks split independently by axis at 6, 8 or 10 cells.
- Clear room dimensions 5, 7 or 9 cells, with rectangular/L/T/cross variants.
- A three-cell central cross preserves access between shared entrances.
- Shared-boundary decisions agree from either side. Door width is one cell;
  full-height openings are two cells. The hash targets 75% doors / 25% openings;
  this is a global statistical rule, not an exact quota in each visible window.
- Resident window 40×40, 1,600 bytes, with safe solid border.
- Main-thread streaming shifts by one cell and applies the inverse local-camera
  adjustment, retaining the same global pose. Streaming precedes pose latching;
  no map rebuild occurs partway through a rendered view.
- The camera remains locally within [20,21) cells when latched. Fixed-point
  movement, collision checks and smooth automatic steering are inherited from
  the qualified C64 demo. Automatic movement prefers reachable room entrances.
- 18-cell raw DDA distance cutoff. This is not an 18-cell Euclidean view sphere.
  No distance-darkening stipple; the ceiling has a screen-anchored pattern.
- W/S moves and A/D turns in the interactive build; joystick port 2 is implemented.
  Reset exits. Input is consumed at logical ticks, not once per displayed image.

Viewport: 128×144 logical multicolor pixels, two bitmaps. 32 coarse rays plus
adaptive fine samples at discontinuities feed full/partial byte vertical fills.
The procedural path preserves the latest C64 multi-lintel composition and its
eight-event per-ray storage budget. This is not the simpler two-opening fixed-map
kernel. Do not import arbitrary maps or change its constants without requalification.

## Source and memory

`src/infinite/world.py` is the independent host generator. Runtime generation,
streaming and navigation are in `world-runtime.asm` / `world-navigation.asm`.
The renderer template is `endless-interactive.asm`, with lintel helpers.
`build_infinite.py` adapts bootstrap, video, input and native memory hazards.
Its neutral layout build is a same-pose renderer oracle; it is not the native PRG.
Complete native assembly snapshots are also distributed under `demos/source`.

| Area | Use |
|---|---|
| $0200-$07FF | lookup helpers, cosine/negative-sine tables; no KERNAL workspace |
| $0801-$2EFF | low runtime, bounded before renderer workspace |
| $2F00-$3BFF | descriptors and rendering scratch |
| $3C00-$3DDF | 480-byte row/address decode tables |
| $4000-$57FF | startup staged tables / platform-dependent screen and lookup areas |
| $5800-$5BFF | 1,024-byte UI font; only character codes below 128 |
| $5C00-$623F | 40×40 resident world, 1,600 bytes |
| $6288-$63BF | lintel compositor, bounded before bitmap clearing |
| $63C0-$7F3F | low bitmap and margins; viewport begins at $6660 |
| $8000-$97FF | UI data, projection/direction tables |
| $9800-$A7FF | world runtime/state; 3,350 bytes with startup seed |
| $A800-$AFFF | projection tables |
| $B000-$B1FF | two 256-byte permutations |
| $B200-$B27F | 128-byte steering angle table |
| $B280-$B363 | multiple-lintel scratch |
| $B380-$B9FF | native initialization/helpers |
| $BA00-$CDFF | exact projection/door tables, clear and layout helpers; staged data |
| high RAM | platform-specific video, I/O exclusions and vectors |

This is a use/lifetime map, not a claim that the whole address interval is free
or simultaneously occupied. C128 screen B reuses staged data after copying.
The assembler guards fixed boundaries; the build checks geometry label stability.
The world cache holds only current axis/coordinate decisions, not visited history.
The native PRGs contain a relocating BASIC bootstrap and load padding; file size
is not the amount of persistent renderer code.

## Verification and limits

Build tools: Python standard library + 64tass, documented 6502-family instructions.
Optional verification: py65; VICE x128/xplus4; Pillow for physical image checks.

```sh
python -B scripts/qualify_infinite.py --build ../YOUR-INFINITE-BUILD --standard pal
python -B scripts/qualify_infinite.py --build ../YOUR-INFINITE-BUILD --standard ntsc
python -B scripts/check_visual.py --build ../YOUR-INFINITE-BUILD --standard pal --frame 3
python -B scripts/check_input.py --build ../YOUR-INTERACTIVE-BUILD --standard pal
```

Qualification compares native captured world RAM against host generation, and
native bitmap against neutral renderer instructions at the captured pose. It
checks font, palette, UI, buffer publication and video registers. Physical
scanouts are checked separately: bitmap RAM alone cannot expose split artifacts.
Benchmarks count new buffer publications over 20 emulated seconds after two
seconds of warm-up, including UI, streaming and interrupts. Warp is only host
acceleration. Random-seed runs are not controlled cross-platform speed comparisons.

No textures, dynamic lights, animated doors, multilevel areas, perspective
correction, sound or external RAM/accelerator requirement. Cost varies with
doors, view complexity and streaming. No minimum FPS is promised.
VICE qualification is sampled, not proof for every seed or trajectory.
Real-hardware and physical-joystick tests remain unperformed.

## Native C128 details

Native BASIC 7 load $1C01, SYS 7181; no GO64, no VDC. VIC-IIe output.
Bootstrap uses MMU common RAM and restores the native $3E mapping.
$D030 enables 2 MHz only in the border; visible UI/body remain at 1 MHz.
The qualified four-phase IRQ uses slow line 46 and fast line 247.
UI font is mirrored at $D800-$DBFF behind Color RAM. The $FF00-$FF04 MMU
shadow is excluded from cold clear and its backing RAM cleared safely through
a temporary stack-page alias with interrupts disabled. Runtime IRQ does not
change the MMU or use renderer scratch. Native init/helpers: 452 bytes;
1,212 bytes remain in the $B380-$B9FF allocation. Public PRG: 51,712 bytes.
