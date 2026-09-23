# Avvio rapido — 2.5vibe128

Estrarre lo ZIP in una cartella. Non servono altri checkout di 3Dvibe64.
Per giocare usare i quattro PRG in demos, senza compilare. Scegliere x128,
Commodore 128 / VIC-IIe, configurazione stock e standard PAL/NTSC.

C128: modalità nativa 40 colonne, **non GO64**, uscita VIC-IIe.
PRG BASIC 7 a $1C01, SYS 7181.

Hardware: caricare come programma BASIC al suo indirizzo nativo, quindi RUN.
Per esempio `LOAD"nome",8` con dispositivo compatibile; verificare la procedura
del proprio loader. Non forzare l’indirizzo C64 $0801. Prova hardware non eseguita.

```sh
python -B build.py --scene examples/demo2-original.json --validate-only
python -B build.py --scene examples/demo2-original.json --run auto --out ../2.5vibe128-original-auto
python -B build.py --scene examples/demo2-original.json --run interactive --out ../2.5vibe128-original-interactive
python -B build.py --scene examples/demo2-optimized.json --run auto --out ../2.5vibe128-optimized-auto
python -B build.py --scene examples/demo2-optimized.json --run interactive --out ../2.5vibe128-optimized-interactive
```

Le cartelle output devono essere nuove ed esterne all’SDK. La build produce
PRG, ASM, label, listing, log e scena; gli intermedi restano nell’output.
`--validate-only` non richiede assembler e non crea file. Nessuna opzione
GraphicsMode, FOV, palette, viewport o override della camera.
