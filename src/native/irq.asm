; Four raster phases. Visible UI/body always 1 MHz; border-only fast mode.
; No geometry ZP, MMU or self-modifying renderer operands touched here.
irq:
 pha
 txa
 pha
 tya
 pha
 lda #1
 sta $d019
 lda irq_phase
 beq irq_top
 cmp #1
 beq irq_slow
 cmp #2
 beq irq_body
irq_fast:
 lda #BORDER_FAST
fast_store:
 sta $d030
 lda #0
 sta irq_phase
 sta $d012
 jmp irq_exit
irq_slow:
 lda #0
slow_store:
 sta $d030
 lda #2
 sta irq_phase
 lda #72
 sta $d012
 jmp irq_exit
irq_body:
 ; Original stock PAL/NTSC split: wait line74, delay51 cycles, select bitmap.
 lda display_buf
 beq body_bank_a
 lda #$30
body_bank_a:
 ora #8
 ldx #74
irq_wait_body:
 cpx $d012
 bne irq_wait_body
 bit irq_phase
 .rept 24
 nop
 .endrept
body_mode_store:
 sta $d018
 lda #$3b
 sta $d011
 lda #3
 sta irq_phase
 lda #252
 sta $d012
 jmp irq_exit
irq_top:
 lda ready
 beq irq_no_swap
 lda drawbuf
 sta display_buf
 eor #1
 sta drawbuf
 lda #0
 sta ready
 inc frame_count
 bne fps_frame_done
 inc frame_count+1
fps_frame_done:
 inc fps_count
irq_no_swap:
 lda #$1b
 sta $d011
 lda $dd00
 and #$fc
 ldx display_buf
 bne ui_bank_b
 ora #2
ui_bank_b:
 sta $dd00
 lda display_buf
 beq ui_bank_a
 lda #$30
ui_bank_a:
 ora #6
 sta $d018
 inc pending_ticks
 bne irq_tick_ok
 dec pending_ticks
 lda #1
 sta tick_overflow
irq_tick_ok:
 inc fps_refresh
 lda fps_refresh
 cmp video_hz
 bcc irq_no_second
 lda #0
 sta fps_refresh
 lda fps_count
 sta fps_value
 ldx #0
fps_decimal:
 cmp #10
 bcc fps_decimal_done
 sec
 sbc #10
 inx
 bne fps_decimal
fps_decimal_done:
 ora #$30
 sta $402d
 sta $cc2d
 txa
 ora #$30
 sta $402c
 sta $cc2c
 lda #0
 sta fps_count
irq_no_second:
 lda #1
 sta irq_phase
 lda #46
 sta $d012
irq_exit:
 pla
 tay
 pla
 tax
 pla
 rti
nmi:
 rti
