# Assembly guide

Python instantiates templates/data; 64tass assembles documented 6502
instructions compatible with the native CPU. No C compiler is involved.
Private, non-reentrant ABI: do not change ZP, stack, phase order or addresses
without tests.

Main labels: init_video_standard, consume_video_ticks, simulation_tick,
latch_pose, raycast_layers, select_strips, compose_screen, render_frame_begin,
render_frame_end, fps_frame_done, presentation_done. Init/IRQ are platform
specific; do not copy show-buffer logic between VIC-IIe and TED.

src/native_builder.py applies bounded/address-checked hooks and verifies
code_end/geometric labels. src/kernels.py emits absolute ceiling stores and
uses Y for row counting. No new numeric approximation. Memory budgets are
assembler assertions, not suggestions.

Rebuild an included PRG from its complete ASM snapshot:

```sh
python -B scripts/assemble_demo.py --source demos/source/demo2-original-auto --out ../asm-demo-build
```

The script copies ASM/assets into output, assembles engine.prg, extracts
payload.bin without its load address, and assembles the bootstrap. Result
must match source.json. Use build.py to create maps: changing a snapshot ASM
does not update the generator. Qualified assembler: 64tass 1.60.3243,
`-a -B --m6502`.
