# Memoria e piattaforma

Indirizzi esadecimali. Nessuna modifica al layout geometrico qualificato.

| Range | Allocation |
|---|---|
| 0000–0001 | CPU I/O port |
| 0002–00EC | Renderer, navigation, IRQ state/scratch |
| 0100–01FF | CPU stack |
| 0200–07FF | Lookup RAM after temporary loader completes |
| 0801–2E73 auto / 0801–2C71 interactive | Low program; 140 / 654 bytes before 2F00 |
| 2F00–3BFF | Ray, edge, refinement and projection workspace |
| 3C00–3FFF | 32×32 solid map |
| 4400–57FF | Geometry/lookups/fill masks/navigation data |
| 5800–5FFF | 2 KB explicit-pattern UI font |
| 6000–7FFF | Low bitmap window; prefix also contains navigation data |
| 6660–7C9F | Active low viewport: 4,608 bytes |
| 8000–AFFF | Renderer tables/data |
| B000–B990 | Native init/helpers + specialized ceiling fill |
| B991–C3FF | Inherited geometry tables/data |
| C480–C536 | Cold bitmap clear helper |
| C600–CBFF | Projection/door tables, copy helper and owners |
| E660–FC9F | Active high viewport: 4,608 bytes |
| FFFA–FFFF | Private vectors |

## C128 nativo, uscita VIC-IIe

CPU 8502, BASIC 7, nessun GO64. Bank 0 + I/O ($FF00=$3E), $D506=$0F
configura 16 KB common ad entrambe le estremità. Il secondo banco non è
necessario al renderer 1.0.0: non viene dichiarata un'accelerazione da RAM1.
Non usa Z80 o VDC. Due banche video VIC tramite $DD00, Screen RAM
$4000/$CC00, font $5800/$D800, bitmap $6000/$E000. $D018 seleziona layout;
Color RAM è inizializzata una volta, salvo UI che aggiorna codici schermo.
Palette VIC-II fissa 0/9/8/7, tinte per orientamento e retino soffitto.

IRQ a quattro fasi: FAST nel bordo dalla riga 247, SLOW alla 46 prima dei
fetch testo; split bitmap alla 74, viewport righe raster 91–234. La selezione
24 righe nel solo corpo chiude il bordo basso prima di FAST. Non sono 2 MHz
continui; nessun FAST nell'immagine attiva. Durante attesa pubblicazione il
foreground può consumare tick utili senza cambiare la posa già renderizzata.

Init disabilita IRQ/NMI e ripulisce il backing RAM sotto i registri MMU
$FF00–$FF04 tramite alias temporaneo della pagina stack; nessuna push/pop o
chiamata mentre lo stack è aliased. Poi ripristina pagina 1. Non rimuovere
questo passaggio copiando un clear C64 generico.

Helper nativo 1.720 byte, 729 liberi nel suo slot. PRG 51.712 byte, include
loader e gap, non è una misura della RAM viva. La CPU resta nativa.

## Contratti comuni

UI tre righe, ultimo blocco 24 byte di ogni screen/matrice protetto da guardie.
Niente sprite o modifica dei loro puntatori. Nessun output generato nell'SDK.
Le label/listing di ogni build sono la mappa autorevole; non considerare ogni
buco della tabella libero. Modifiche al layout richiedono nuovi test.
