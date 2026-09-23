# 2.5vibe128 1.0.0 — note di release

Prima distribuzione autonoma della pipeline nativa mono-portals.
Demo 2 originale e nuova mappa, auto/interattiva, PRG e sorgenti completi.
Riferimenti precedenti preservati; nessuna ottimizzazione nuova durante packaging.

## Risultati misurati

| Map | Run | Standard | FPS | Images / 20 s |
|---|---|---|---:|---:|
| original | auto | PAL | 6.55 | 131 |
| original | auto | NTSC | 6.20 | 124 |
| original | interactive | PAL | 5.05 | 101 |
| original | interactive | NTSC | 4.60 | 92 |
| optimized | auto | PAL | 7.45 | 149 |
| optimized | auto | NTSC | 7.05 | 141 |
| optimized | interactive | PAL | 4.55 | 91 |
| optimized | interactive | NTSC | 4.30 | 86 |

VICE stock, finestra iniziale di 20 secondi emulati dopo 2 secondi warm-up.
Interattiva immobile alla partenza, non un percorso manuale benchmarkato.
Misure del pacchetto attuale, non riciclate dai prototipi. 960 viste native
confrontate per SDK: zero differenze bitmap rispetto al modello della posa.
Sorgenti e ricompilazioni deterministiche verificate. La qualificazione è
campionata, non prova ogni traiettoria possibile. Hardware reale non testato.

La distribuzione è pronta per un repository GitHub, non è stata caricata.
La geometria è volutamente limitata ai contratti descritti in MAPS.
L'ASM completo delle demo è incluso su richiesta, non sono inclusi dump,
profiler, screenshot, directory temporanee o archivi dei vecchi esperimenti.
