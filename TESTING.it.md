# Test e qualificazione

Build minima: Python 3.10+ e 64tass. Toolchain qualificata su Windows:
Python 3.13.14, 64tass 1.60.3243, VICE 3.10. Comandi senza percorsi privati:
PATH / TASS64_EXE, VICE_X128 o VICE_XPLUS4 per il rispettivo eseguibile.
Python/64tass/VICE non sono redistribuiti. Per prove opzionali:

```sh
python -m pip install -r requirements-tests.txt
python -B tests/test_release.py
python -B build.py --scene examples/demo2-original.json --run auto --out ../2.5vibe128-test
python -B scripts/check_cpu.py --build ../2.5vibe128-test
python -B scripts/qualify.py --build ../2.5vibe128-test --standard pal
python -B scripts/qualify.py --build ../2.5vibe128-test --standard ntsc
python -B scripts/check_visual.py --build ../2.5vibe128-test --standard pal --frame 3
```

Ripetere per mappa ottimizzata e interattiva. Gli strumenti rifiutano output
dentro l'SDK; usare cartelle nuove per ripetere le catture. unittest costruisce
in directory temporanee esterne. Il manifest identifica tutti i file permanenti
tranne se stesso; hash del manifest e dello ZIP sono nella consegna esterna.

Dopo qualify.py su una build interattiva, eseguire
`python -B scripts/check_input.py --build ../build-interattiva --standard pal`
e ripetere con ntsc. Inietta W/S/A/D e nessun tasto nella matrice tastiera
di VICE, poi controlla le letture hardware native senza patch al renderer.
Joystick presente nel codice ma non esercitato automaticamente nella release.

I livelli sono distinti: test parser/contratti; esecuzione CPU vs oracolo fixed;
VICE stock con contese video/IRQ/simulazione; pixel fisici da una scansione
completa con posa acquisita nello stesso run. py65 non produce FPS nativi.
La qualificazione usa 120 viste per ciascuna combinazione, bitmap, camera,
tick, ordine buffer, UI/font, palette, guardie e registri. Non confrontare
frame N di macchine con FPS differenti: confrontare la posa realmente acquisita.

Benchmark: 2 s warm-up, 20 s emulati, UI attiva, viste complete pubblicate.
Warp accelera solo l'host. C128 misura clock phi1; Plus/4 clock master TED.
Contatori grezzi non confrontabili come cicli CPU. FPS e p95 dipendono dal tratto;
non confondere la finestra iniziale con un intero giro o un minimo garantito.

## Hardware reale — non eseguito

Provare macchina stock PAL/NTSC, annotare revisione, loader e uscita video.
Caricare PRG nativo, verificare UI, bordi, palette, FPS, doppio buffer, W/S/A/D
e joystick; attraversare entrambe le porte, angoli e completare il tour.
Registrare difetti e foto/catture. L'emulatore non sostituisce tale prova.
Nessun PASS hardware viene dichiarato. Le suite poligonali C64 sono estranee
a questi SDK e non vengono presentate come prova dei port nativi.
