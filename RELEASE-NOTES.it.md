# 2.5vibe128 1.1.0 — note di release

Correzioni architravi C64 1.5.5 nel renderer a mappa fissa; video/clock nativi
conservati. Sei demo senza musica, PRG e sorgenti assembly completi: demo 2
originale, demo 2 ottimizzata e mondo infinito, ciascuna auto/interattiva.
La generazione infinita ha una build separata, non amplia il contratto delle
mappe fisse. Release precedenti e sorgenti C64 intatti.

## PRG distribuiti: misure

| Map | Run | Video | FPS | Images / 20 s |
|---|---|---|---:|---:|
| original | auto | PAL | 6.55 | 131 |
| original | auto | NTSC | 6.20 | 124 |
| original | interactive | PAL | 5.05 | 101 |
| original | interactive | NTSC | 4.60 | 92 |
| optimized | auto | PAL | 7.45 | 149 |
| optimized | auto | NTSC | 7.05 | 141 |
| optimized | interactive | PAL | 4.55 | 91 |
| optimized | interactive | NTSC | 4.30 | 86 |
| infinite | auto | PAL | 3.80 | 76 |
| infinite | auto | NTSC | 3.30 | 66 |
| infinite | interactive | PAL | 4.55 | 91 |
| infinite | interactive | NTSC | 6.00 | 120 |

VICE 3.10 stock. Venti secondi emulati dopo due secondi di riscaldamento, UI
attiva, conteggio delle sole nuove viste complete. Interattiva ferma all'avvio,
non benchmark di navigazione manuale. I seed infiniti variano con l'avvio:
i mondi differiscono tra piattaforme/standard, quindi non ricavare percentuali
di accelerazione controllate o minimi FPS garantiti da questa tabella.

## Seed controllato: infinita automatica

Seed `0x12345678`, cutoff grezzo 18 celle e viewport 128×144 invariati.

| Video | FPS | Images / 20 s |
|---|---:|---:|
| PAL | 3.20 | 64 |
| NTSC | 2.95 | 59 |

Il seed fissa la geometria; la diversa cadenza nativa campiona comunque pose
diverse. C128 misura clock phi1, Plus/4 clock master TED, non cicli istruzione
CPU direttamente confrontabili. Dati grezzi conservati fuori dall'SDK.

## Qualificazione

Per SDK: **1.440 viste native** (sei demo × PAL/NTSC × 120), più **240** viste
a seed fisso, **128** viste istruzioni/modello delle mappe fisse, **24**
acquisizioni fisiche complete e **30** casi tastiera. Zero differenze bitmap
a pari posa e zero differenze fisiche in viewport/margini. Mappa RAM infinita
coincidente con la generazione host. Verificati font, palette, UI, split,
registri nativi e ordine dei buffer. Verificate build/sorgenti riproducibili
e manifest dei pacchetti.

I test fisici hanno trovato un artefatto nel margine della sola infinita
Plus/4: la metà font recuperata poteva essere letta prima dello split bitmap.
L'azzeramento delle righe colore inutilizzate sotto la UI lo corregge senza
cambiare viewport attiva o geometria.

Niente musica/player/file audio. Verifica campionaria, non esaustiva su tutti
i seed/percorsi. **Hardware reale e joystick fisico non testati.**
Nessuna ottimizzazione estranea. Il packaging non pubblica su GitHub.
