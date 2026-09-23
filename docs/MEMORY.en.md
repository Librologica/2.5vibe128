# Memory and platform

Hexadecimal addresses. Qualified geometry layout preserved.

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

## Native C128, VIC-IIe output

8502 CPU, BASIC 7, no GO64. Bank 0 + I/O ($FF00=$3E), $D506=$0F selects
16-KB common RAM at both ends. The second bank is not required by this
1.0.0 renderer; no RAM1 performance gain is claimed. No Z80 or VDC use.
Two VIC banks via $DD00, Screen RAM $4000/$CC00, fonts $5800/$D800,
bitmaps $6000/$E000. $D018 selects layout. Color RAM initializes once;
UI updates screen glyph codes. Fixed VIC-II 0/9/8/7 palette, orientation
colors and ceiling stipple.

Four-phase IRQ: FAST in border from line 247, SLOW at 46 before text fetch;
bitmap split at 74, active viewport raster lines 91–234. Body-only 24-row
selection closes the bottom border before FAST. Not continuous 2 MHz;
no FAST inside the active picture. Foreground may consume useful ticks
while waiting for publication without changing the already rendered pose.

Init disables IRQ/NMI and clears backing RAM under MMU $FF00–$FF04 through
a temporary stack-page alias. No calls/push/pop during the alias; page 1
is restored afterwards. Do not replace this with a generic C64 clear.

Native helper 1,720 bytes, 729 free in its slot. PRG 51,712 bytes includes
loader/gaps and is not a measure of live RAM. CPU remains in native mode.

## Shared contracts

Three-row UI; final 24 bytes of each screen/matrix protected by guards.
No sprites or sprite-pointer modification. No generated output in SDK.
Each build's labels/listing are authoritative; not every table gap is free
space. Layout changes require new qualification.
