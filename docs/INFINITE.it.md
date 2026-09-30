# Demo del mondo infinito continuo

## Contratto di compilazione

Demo specializzata con build separata, non estensione del parser JSON delle
mappe fisse. Usare `build_infinite.py --run auto|interactive --out NUOVA_CARTELLA`.
La cartella di output deve essere esterna all'SDK e non deve esistere.
`--seed` opzionale accetta un intero 0..4294967295, decimale o esadecimale 0x.
Se omesso, si campionano timer/raster nativi all'avvio. Non è casualità
crittografica: temporizzazioni di avvio identiche possono ripetere il seed.

I due PRG pubblicati usano il seed variabile all'avvio. Per confrontare piattaforme
o riprodurre un mondo compilare con lo stesso seed esplicito. Seed e direzione
di esplorazione determinano parti diverse di un unico mondo coerente; tornando
indietro si rigenera la stessa geometria. Non viene conservato un archivio delle
stanze visitate. Coordinate a 32 bit per asse, con wrap definito: “infinito”
significa esplorazione generata continuamente, non mappa memorizzata illimitata.

## Geometria e navigazione

- Un livello; pareti ortogonali, porte statiche con architrave, aperture al soffitto.
- Hash deterministico di coordinate globali e seed; non una mappa fissa ripetuta.
- Blocchi di 16 celle divisi indipendentemente per asse a 6, 8 o 10 celle.
- Stanze libere di 5, 7 o 9 celle, con varianti rettangolari/a L/T/croce.
- Una croce centrale larga tre celle conserva il collegamento tra gli accessi.
- Le decisioni sui confini condivisi coincidono dai due lati. Porte larghe una
  cella, aperture a tutta altezza larghe due. L'hash punta al 75% di porte / 25%
  di aperture: regola statistica globale, non quota esatta per finestra visibile.
- Finestra residente 40×40, 1.600 byte, con bordo solido di sicurezza.
- Lo streaming nel main thread sposta una cella e applica la traslazione inversa
  alla camera locale, mantenendo la posa globale. Precede l'acquisizione della
  posa; nessuna rigenerazione della mappa durante il rendering di una vista.
- La camera acquisita resta localmente in [20,21) celle. Movimento fixed-point,
  collisioni e guida automatica morbida derivano dalla demo C64 qualificata.
  Il moto automatico privilegia gli accessi raggiungibili delle stanze.
- Cutoff DDA grezzo a 18 celle: non una sfera visiva euclidea di raggio 18.
  Nessun retino d'ombra a distanza; il soffitto ha un pattern ancorato allo schermo.
- W/S muove e A/D ruota nell'interattiva; joystick porta 2 implementato.
  Reset per uscire. Input consumato ai tick logici, non una volta per immagine.

Viewport 128×144 pixel logici multicolor, due bitmap. 32 raggi principali più
campioni fini adattivi alle discontinuità alimentano fill verticali di byte interi
e parziali. Il percorso procedurale conserva l'ultima composizione multi-architrave
C64 e il suo budget di otto eventi per raggio. Non è il kernel semplificato delle
mappe fisse con due aperture. Mappe arbitrarie o costanti diverse richiedono
una nuova qualificazione.

## Sorgenti e memoria

`src/infinite/world.py` è il generatore host indipendente. Generazione runtime,
streaming e navigazione sono in `world-runtime.asm` / `world-navigation.asm`.
Il template del renderer è `endless-interactive.asm`, con gli helper architrave.
`build_infinite.py` adatta bootstrap, video, input e aree di memoria native.
La build di layout neutra è l'oracolo del renderer a pari posa, non il PRG nativo.
Snapshot assembly nativi completi distribuiti anche in `demos/source`.

| Area | Utilizzo |
|---|---|
| $0200-$07FF | helper lookup, coseno/seno negativo; non workspace KERNAL |
| $0801-$2EFF | runtime basso, limitato prima del workspace renderer |
| $2F00-$3BFF | descriptor e scratch rendering |
| $3C00-$3DDF | 480 byte di tabelle riga/decodifica indirizzi |
| $4000-$57FF | tabelle iniziali / aree schermo e lookup dipendenti dal target |
| $5800-$5BFF | font UI di 1.024 byte; solo codici carattere inferiori a 128 |
| $5C00-$623F | mondo residente 40×40, 1.600 byte |
| $6288-$63BF | compositore architravi, limitato prima del clear bitmap |
| $63C0-$7F3F | bitmap bassa e margini; viewport da $6660 |
| $8000-$97FF | dati UI, tabelle proiezione/direzione |
| $9800-$A7FF | runtime/stato mondo; 3.350 byte con seed di avvio |
| $A800-$AFFF | tabelle proiezione |
| $B000-$B1FF | due permutazioni da 256 byte |
| $B200-$B27F | tabella angoli di guida, 128 byte |
| $B280-$B363 | scratch architravi multiple |
| $B380-$B9FF | inizializzazione/helper nativi |
| $BA00-$CDFF | tabelle proiezione/porte esatte, clear/layout; dati iniziali |
| RAM alta | video, esclusioni I/O e vettori specifici della piattaforma |

È una mappa degli usi nel tempo, non l'indicazione che tutto l'intervallo sia
libero o occupato simultaneamente. Lo schermo B C128 riusa dati già copiati.
L'assembler controlla i confini fissi; la build verifica stabilità delle label
geometriche. La cache conserva solo decisioni di assi/coordinate correnti,
non la storia delle visite. I PRG nativi comprendono bootstrap BASIC con
rilocazione e padding: la dimensione file non equivale al codice persistente.

## Verifica e limiti

Build: libreria standard Python + 64tass, istruzioni documentate famiglia 6502.
Verifiche opzionali: py65, VICE x128/xplus4, Pillow per i confronti visivi.

```sh
python -B scripts/qualify_infinite.py --build ../BUILD-INFINITA --standard pal
python -B scripts/qualify_infinite.py --build ../BUILD-INFINITA --standard ntsc
python -B scripts/check_visual.py --build ../BUILD-INFINITA --standard pal --frame 3
python -B scripts/check_input.py --build ../BUILD-INTERATTIVA --standard pal
```

La qualificazione confronta la mappa RAM nativa con la generazione host e la
bitmap nativa con le istruzioni del renderer neutro alla posa catturata.
Controlla font, palette, UI, pubblicazione dei buffer e registri video. Il segnale
visualizzato è verificato separatamente: la sola RAM bitmap non rivela errori
di split. Benchmark sulle nuove pubblicazioni in 20 secondi emulati dopo due
secondi di riscaldamento, inclusi UI, streaming e interrupt. Warp accelera solo
l'host. Run con seed casuali non sono confronti prestazionali controllati tra target.

Niente texture, luci dinamiche, porte animate, aree multilivello, correzione
prospettica, audio o necessità di RAM/acceleratori esterni. Il costo varia con
porte, vista e streaming. Nessun FPS minimo garantito.
La qualificazione VICE è campionaria, non una prova su ogni seed o percorso.
Test su hardware e joystick fisici non eseguiti.

## Dettagli C128 nativo

BASIC 7 nativo, caricamento $1C01, SYS 7181; niente GO64 o VDC. Uscita VIC-IIe.
Il bootstrap usa RAM comune MMU e ripristina il mapping nativo $3E.
$D030 abilita 2 MHz solo nei bordi; UI e corpo visibili restano a 1 MHz.
L'IRQ qualificato a quattro fasi usa riga lenta 46 e veloce 247.
Il font UI è duplicato a $D800-$DBFF dietro Color RAM. Lo shadow MMU
$FF00-$FF04 è escluso dal clear iniziale; la RAM sottostante è azzerata tramite
alias temporaneo dello stack a interrupt disabilitati. L'IRQ runtime non cambia
MMU e non usa scratch del renderer. Init/helper nativi: 452 byte;
1.212 byte residui nell'allocazione $B380-$B9FF. PRG pubblico: 51.712 byte.
