# Pipeline 2.5D

## Perimetro della 1.0.0

Renderer software autonomo derivato dal backend mono-portals della Mode 8 di
3Dvibe64 1.4.0. Questa distribuzione contiene solo il percorso nativo
monolivello con aperture statiche della demo 2. Non contiene le modalità
poligonali 1–7 e non promuove porting multilivello o VDC non qualificati.
Il nome storico del modulo `mode8` e dello schema JSON conserva compatibilità,
non seleziona altre modalità grafiche. Non si usa `GraphicsMode=2.5`.

## Dal mondo ai pixel

`tick → simulazione → posa acquisita → DDA → profili → bitmap inattiva → pubblicazione`

1. L'IRQ accumula tick e aggiorna contatore FPS/interfaccia. Il foreground
   consuma i tick, legge l'input e applica movimento, collisioni o percorso.
2. Una sola posa viene acquisita per ciascuna nuova immagine. Il disegno non
   cambia camera a metà frame. La simulazione usa circa 50 tick logici/s:
   PAL un tick per refresh, NTSC cinque ogni sei. Gli oscillatori reali
   mantengono una piccola differenza rispetto a 50 Hz esatti.
3. 32 raggi principali attraversano la mappa. Direzioni su 512 angoli e offset
   derivati da un piano prospettico a FOV 60°, non angoli uniformi senza
   correzione. Camera Q8.8; DDA fixed-point con delta/tabulazioni, somme,
   confronti e avanzamento al confine X/Y successivo. Il ramo per quadrante
   evita scelte ripetute. Profondità corretta e lookup di proiezione riducono
   la distorsione delle pareti frontali; gli angoli quantizzati hanno una
   correzione geometrica qualificata dei profili.
4. Owner di parete e piano permettono di riconoscere superfici continue.
   I limiti dei gruppi vengono interpolati/corretti; discontinuità e aperture
   richiedono campioni fini adattivi. I 32 raggi non sono semplicemente
   duplicati su quattro colonne: i bordi obliqui sono risolti alla larghezza
   finale di 128 pixel logici. Il numero di raggi effettivi varia con la posa.
5. Per i due varchi supportati il DDA trova ingresso e uscita del volume
   superiore e continua fino alla parete opaca. Si proiettano fronte,
   sottarchitrave e parete dietro l'apertura. Il contratto della mappa prova
   che basta questo numero di strati: non è un portal renderer generico.
6. `select_strips` prepara oggi limiti/profili, non texture. `compose_screen`
   riempie bande verticali della bitmap. Colonne logiche larghe due pixel
   fisici, quattro pigmenti in ciascun byte: riempimenti pieni e maschere
   esatte ai bordi parziali. Non vengono riempiti triangoli o mesh poligonali.
7. Buffer pronto solo dopo il completamento della vista. L'IRQ scambia il
   display in una finestra sicura. Ogni incremento FPS è una nuova vista
   completa; niente colonne alternate o frame parziali contati come interi.

## Ottimizzazioni conservate

Generatori specializzati per layout, tabelle geometriche e trigonometriche,
moltiplicazioni/lookup esatti, DDA per quadrante, riuso dei campioni compatibili,
raffinamento solo alle discontinuità, interpolazione dei bordi per owner,
scritture dirette del soffitto e contatore righe nel registro Y. La rasterizzazione
non effettua shading Gouraud, calcoli di normali, UV, texture sampling o luci.
Il retino del soffitto è ancorato allo schermo. Le tinte dipendono dal lato.
Le vecchie etichette `strip`/`TEXTURED` non definiscono funzionalità attive.

Lo SMC matematico è privato del foreground: il renderer non è rientrante.
Gli handler preservano A/X/Y e non condividono lo scratch della geometria.
Non chiamare le routine di rendering dall'IRQ. Il costo dipende da attraversamenti,
discontinuità e aperture visibili, non dal solo numero di celle solide.
L'FPS medio non è un minimo garantito. Simulazione separata non significa
latenza nulla: una vista lunga ritarda il riscontro visivo del movimento.

## Sorgenti e modifica

`src/mode8/asm/apertures-*.asm` sono template sorgente completi intenzionali.
`src/mode8/build.py` valida e genera mappe/owner; `src/native_builder.py`
adatta la piattaforma; `src/native` contiene bootstrap/IRQ; `src/kernels.py`
genera i due fill specializzati. `mono.py` è l'oracolo fixed indipendente;
`trace.py` esegue le vere istruzioni con py65, senza simulare contese video.
Gli helper host condivisi non rendono pubblici gli altri backend: la build
rifiuta tutto salvo mono-portals. Gli ASM completi di ogni PRG sono anche
in `demos/source`. Vedere MEMORY, MAPS, ASSEMBLY-GUIDE e TESTING.

Nessuna texture, perspective-correct mapping, porta animata, sprite 3D,
mesh importata, illuminazione dinamica, room-over-room o geometria inclinata
arbitraria. Portare oltre questi limiti richiede un nuovo intervento e test.
