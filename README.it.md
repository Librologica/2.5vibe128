# 2.5vibe128 1.0.0

SDK nativo **Commodore 128 / VIC-IIe**, derivato dalla sola pipeline 2.5D di 3Dvibe64.
Ambienti monolivello con due aperture statiche, architravi e spessore;
bitmap multicolor 128×144 logica (256×144 fisica), doppio buffer, UI/FPS,
PAL/NTSC, tour automatico e navigazione W/S+A/D, joystick porta 2.

Quattro demo in `demos`: originale/ottimizzata × auto/interattiva.
Sorgenti ASM completi in `demos/source`, JSON in `examples`, generatore in
`build.py` e `src`. Le due mappe hanno stesso avvio/percorso. La pipeline è
raycasting DDA, non un motore poligonale; nessuna texture attiva.

## Uso

Richiede Python 3.10+ e 64tass. PATH o `TASS64_EXE`; VICE non serve a compilare.
Output sempre in cartelle nuove esterne all’SDK.

```sh
python -B build.py --scene examples/demo2-optimized.json --run interactive --out ../2.5vibe128-build
x128 -default +go64 -40col -pal -autostartprgmode 1 ../2.5vibe128-build/2.5vibe128.prg
```

W/S avanti/indietro, A/D ruota. Automatica: `--run auto`. Reset per uscire.
Per provare NTSC sostituire `-pal` con `-ntsc`. Hardware reale non testato.

## Documentazione e licenze

[Quickstart](QUICKSTART.it.md) · [Pipeline](docs/PIPELINE.it.md) · [Mappe / maps](docs/MAPS.it.md) · [Assembly](docs/ASSEMBLY-GUIDE.it.md) · [Memoria / memory](docs/MEMORY.it.md) · [Test](TESTING.it.md) · [Release](RELEASE-NOTES.it.md).

Codice e dati: **PolyForm Noncommercial 1.0.0**, non MIT. Documentazione:
**CC BY-NC 4.0**. Copyright 2026 librologica.digital; attribuzioni conservate
in LICENSE, LICENSE-DOCUMENTATION.md e NOTICE.md. Nessuna pubblicazione
su GitHub automatica: questo è il pacchetto pronto per il repository.
