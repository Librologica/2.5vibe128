; Only cold initialization helpers; no changes to the rendering algorithm.
native_clear_tail:
 cpx #$40
 bcc native_tail_store
 cpx #$45
 bcc native_tail_done
native_tail_store:
 sta $fec0,x
native_tail_done:
 rts

native_shadow_clear:
 ; MMU stack-page alias accesses the backing RAM beneath $ff00..$ff04.
 ; Do not push/pop/call or enable IRQ while the stack is aliased.
 lda #0
 sta $d50a
 lda #$ff
 sta $d509
 lda #0
 sta $0100
 sta $0101
 sta $0102
 sta $0103
 sta $0104
 lda #1
 sta $d509
 rts
