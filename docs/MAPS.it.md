# Preparare le mappe

Partire dai JSON completi in examples: demo2-original (96 owner) oppure
demo2-optimized (44 owner). Stesso itinerario e partenza; geometria diversa.
La seconda non è una mappa casuale. Ogni mappa è un array completo 32×32.
L'indice è `32*y+x`, origine in alto a sinistra, X destra, Y verso il basso.
`PLANS.md` mostra le due piante generate dagli stessi dati.

La radice JSON contiene esattamente `scene` e `navigation`. Il parser rifiuta
chiavi duplicate, ignote, null al posto di array e booleani come interi.

| Campo scene | Contratto |
|---|---|
| schema | `3dvibe64-mode8-map-v1` |
| size | `[32,32]` |
| solid | 1024 interi 0 libero / 1 solido; bordo esterno interamente solido |
| floor | 1024 zeri |
| ceiling | 1024 interi: 96, tranne le quattro celle porta a 64 |
| initial | `[5939,2509,469,32,0]`, fisso |
| eyeHeight | 32 |
| playerHeight | 48, facoltativo con default 48 |
| heightUnit | facoltativo, soltanto `1/32 cell` |
| doors | `[[10,14,11,14],[22,14,23,14]]`, esatto |
| ramps | `[]` |
| notes | stringa facoltativa, senza effetto runtime |

La riga y=14 è solida salvo x=10,11,22,23. I varchi sono larghi due celle,
spessi una, alti 64/32=2 celle; soffitto 96/32=3 celle, occhio 32/32=1 cella.
L'architrave rimane quindi visibile. Porte statiche, non ante apribili.
Non cambiare questi slot, quote o lo spessore per aggirare il validatore.
La mappa consente al massimo 96 tratti contigui esposti (owner), più sentinella.
Owner e piani sono generati da solid; non vanno scritti a mano.

Camera e waypoint usano interi Q8.8 già nel JSON: una cella vale 256,
il centro `(x,y)` vale `(256*x+128,256*y+128)`. Yaw 0..511: 0=+Y,
128=+X,256=−Y,384=−X. FOV 60°, orizzonte fisso, nessun pitch.
Gli ultimi due valori di initial sono quota occhio intera e frazione/256.
`navigation` contiene camera uguale ai primi tre initial e nodes come lista
di coppie Q8.8. In questa release camera e tutti i 193 waypoint devono
rimanere identici al template: non è un editor generico o un pathfinder.

È possibile cambiare celle solide/libere lontano da bordo, separatore,
partenza e percorso. Il builder simula 30.000 tick e rifiuta collisioni del
tour o un giro non completato. La validazione si applica anche all'interattiva.
Raggio collisione auto 224/256 di cella; manuale 48/256, con scorrimento X/Y.
Non vi è il limite del 70% di occupazione da una parete in modalità manuale.

Esempio operativo: copiare demo2-optimized.json fuori dall'SDK, modificare
solid preservando i vincoli, poi eseguire `build.py --scene ../my-map.json
--validate-only`. Una validazione PASS non è una prova esaustiva di ogni posa.
Testare anche il PRG manuale, gli angoli e tutti i varchi.

Errori principali: DOCUMENT/FORMAT/SCHEMA (formato), BORDER (bordo aperto),
INITIAL_POSE/TEMPLATE_CAMERA (camera), MONO_NAV (itinerario cambiato),
MONO_APERTURES/MONO_SEPARATOR/MONO_QUOTE (varchi/quote), OWNER_CAPACITY
(troppi tratti), AUTO_COLLISION/AUTO_TOUR (percorso), NATIVE_BACKEND
(tipo non supportato), LOW_BUDGET (sovrapposizione memoria).
Non vengono abbassate automaticamente qualità o precisione per far compilare.
Palette, FOV e viewport non sono campi pubblici della scena.
