# 2.5vibe128 demos / demo

| PRG | Scene / Scena | Controls / Comandi |
|---|---|---|
| demo2-original-auto.prg | Original demo 2 / Demo 2 originale | automatic tour / giro automatico |
| demo2-original-interactive.prg | Original demo 2 / Demo 2 originale | W/S, A/D |
| demo2-optimized-auto.prg | Balanced map / Mappa bilanciata | automatic tour / giro automatico |
| demo2-optimized-interactive.prg | Balanced map / Mappa bilanciata | W/S, A/D |
| infinite-auto.prg | Continuous world / Mondo continuo | exploration / esplorazione |
| infinite-interactive.prg | Continuous world / Mondo continuo | W/S, A/D |

All six PRGs are silent. Native PAL/NTSC detection. W/S move; A/D turn.
Joystick port 2 implemented, physical joystick untested. Reset exits.
Four fixed-map demos share start/route. Infinite uses a variable startup seed;
build_infinite.py --seed makes a world reproducible.
Complete native ASM/assets: source/<PRG stem>. Rebuild via scripts/assemble_demo.py.
Generators: build.py + examples for fixed maps; build_infinite.py + src/infinite
for procedural worlds. See source.json hashes and QUICKSTART for native loading.
No GO64 on C128. Plus/4 needs 64 KB. Real hardware untested.

Tutti i sei PRG sono senza musica. Rilevamento PAL/NTSC nativo.
W/S muove; A/D ruota. Joystick porta 2 implementato, fisicamente non testato.
Reset per uscire. Le quattro mappe fisse condividono avvio/percorso.
L'infinita usa seed variabile all'avvio; build_infinite.py --seed riproduce il mondo.
ASM/asset nativi completi: source/<nome PRG>. Ricompilare con scripts/assemble_demo.py.
Generatori: build.py + examples per mappe fisse; build_infinite.py + src/infinite
per mondi procedurali. Hash in source.json, caricamento nativo nel QUICKSTART.
Niente GO64 su C128. Plus/4 richiede 64 KB. Hardware reale non testato.
