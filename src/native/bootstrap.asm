; Native BASIC 7 load at $1c01. No GO64, no ROM/KERNAL after takeover.
; Original geometry image relocates downwards using temporary $0200 code.
*=$1c01
 .word basic_end,10
 .byte $9e
 .text "7181"
 .byte 0
basic_end:
 .word 0
boot:
 sei
 cld
 ldx #$ff
 txs
 lda #$3e ; ensure native bank 0 + I/O even after BANK 0:SYS
 sta $ff00
 lda #$7f
 sta $dc0d
 sta $dd0d
 lda $dc0d
 lda $dd0d
 lda #0
 sta $d01a
 sta $d011
 sta $d015
 ; Bank 0, 16 KB common at both ends. CPU-bank middle = $4000..bfff.
 lda #$0f
 sta $d506
 ldx #0
copy_loader:
 lda loader_bytes,x
 sta $0200,x
 inx
 cpx #loader_end-loader_bytes
 bne copy_loader
 jmp $0200
loader_bytes:
 .logical $0200
 lda #$3f ; all bank-0 RAM, including payload under I/O
 sta $ff00
 lda #0
 sta $fb
 lda #$20
 sta $fc
 lda #$01
 sta $fd
 lda #$08
 sta $fe
 ldx #(@PAYLOAD_BYTES@ / 256)
 ldy #0
relocate_page:
 lda ($fb),y
 sta ($fd),y
 iny
 bne relocate_page
 inc $fc
 inc $fe
 dex
 bne relocate_page
relocate_tail:
 cpy #(@PAYLOAD_BYTES@ & 255)
 beq relocated
 lda ($fb),y
 sta ($fd),y
 iny
 bne relocate_tail
relocated:
 lda #$3e ; native bank 0 RAM + I/O
 sta $ff00
 jmp $080d
 .here
loader_end:
 .cerror loader_end-loader_bytes>256,"loader page"
 .cerror boot!=$1c0d,"BASIC SYS target"
*=$2000
 .binary "payload.bin"
 .cerror *>=$ff00,"payload collides with MMU shadow"
