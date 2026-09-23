# Guida assembly

Python istanzia template e dati; 64tass assembla istruzioni documentate 6502
compatibili con la CPU nativa. Non viene compilato C. ABI privato, non
rientrante: non cambiare ZP, stack, ordine delle fasi o indirizzi senza test.

Label principali: init_video_standard, consume_video_ticks, simulation_tick,
latch_pose, raycast_layers, select_strips, compose_screen, render_frame_begin,
render_frame_end, fps_frame_done, presentation_done. init e IRQ sono specifici
della piattaforma; show-buffer non va copiato tra VIC-IIe e TED.

`src/native_builder.py` applica hook a lunghezza/indirizzi controllati e
controlla code_end e le label geometriche. `src/kernels.py` genera scritture
assolute del soffitto e usa Y per il conteggio righe. Nessuna approssimazione
numerica nuova. I budget sono assertion dell'assembler, non suggerimenti.

Per un PRG già incluso, ricompilare lo snapshot ASM completo:

```sh
python -B scripts/assemble_demo.py --source demos/source/demo2-original-auto --out ../asm-demo-build
```

Lo script copia gli ASM e gli asset nell’output, assembla engine.prg,
estrae payload.bin senza l’indirizzo di caricamento e assembla il bootstrap.
Il risultato deve corrispondere a source.json. Per creare mappe, usare invece
build.py: modificare un ASM di snapshot non aggiorna il generatore.
Tool qualificato: 64tass 1.60.3243, `-a -B --m6502`.
