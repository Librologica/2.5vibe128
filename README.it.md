# 2.5vibe128 1.1.0

SDK nativo **Commodore 128 / VIC-IIe**, derivato dalla sola pipeline 2.5D di 3Dvibe64.
Bitmap multicolor 128×144 logica (256×144 fisica), doppio buffer,
UI/FPS, PAL/NTSC, esplorazione automatica oppure navigazione W/S+A/D.

La 1.1.0 promuove le correzioni architravi C64 1.5.5: azzera lo stato
camera-interna all'uscita dal volume superiore e raffina i bordi quando
cambiano i piani frontali. Restano le strategie native di video, memoria e clock.

**Sei demo senza musica**: demo 2 originale, demo 2 ottimizzata e nuovo mondo
infinito continuo, ciascuna automatica e interattiva. PRG e snapshot ASM completi
in `demos`; generatori/template host in `src`. Le due mappe fisse condividono
avvio e percorso. La demo infinita genera continuamente stanze, porte e aperture
a tutta altezza, con seed iniziale variabile.

L'SDK a mappa fissa conserva il contratto rigoroso mono-portals (due aperture).
La demo infinita usa una build specializzata separata: non amplia implicitamente
quel contratto. È raycasting DDA, non un motore poligonale né un texture mapper.

## Compilazione e avvio

Servono Python 3.10+ e 64tass (PATH oppure `TASS64_EXE`).
Usare sempre una nuova cartella di output esterna all'SDK.

```sh
python -B build.py --scene examples/demo2-optimized.json --run interactive --out ../2.5vibe128-build
x128 -default +go64 -40col -pal -autostartprgmode 1 ../2.5vibe128-build/2.5vibe128.prg
python -B build_infinite.py --run auto --out ../2.5vibe128-infinite
x128 -default +go64 -40col -pal -autostartprgmode 1 ../2.5vibe128-infinite/2.5vibe128-infinite-auto.prg
```

W/S avanti/indietro, A/D ruota; joystick porta 2 implementato. Reset per uscire.
Usare `--run interactive` per esplorare a mano; `--seed 0x12345678` seleziona
un mondo infinito riproducibile. Per NTSC sostituire `-pal` con `-ntsc`.
Non sono distribuiti musica, player o file audio. Hardware reale non testato.

## Documentazione e licenze

[English](README.en.md) · [Quickstart](QUICKSTART.it.md) ·
[Pipeline](docs/PIPELINE.it.md) · [Mappe](docs/MAPS.it.md) ·
[Mondo infinito](docs/INFINITE.it.md) · [Assembly](docs/ASSEMBLY-GUIDE.it.md) ·
[Memoria](docs/MEMORY.it.md) · [Test](TESTING.it.md) · [Release](RELEASE-NOTES.it.md).

Codice/dati: **PolyForm Noncommercial 1.0.0**, non MIT.
Documentazione: **CC BY-NC 4.0**. Copyright 2026 librologica.digital.
Vedere LICENSE, LICENSE-DOCUMENTATION.md e NOTICE.md.
Il packaging non pubblica su GitHub.
