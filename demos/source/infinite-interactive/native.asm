native_init:
 sei
 cld
 ldx #$ff
 txs
 lda #$7f
 sta $dc0d
 sta $dd0d
 lda $dc0d
 lda $dd0d
 lda #<nmi
 sta $fffa
 lda #>nmi
 sta $fffb
 lda #<irq
 sta $fffe
 lda #>irq
 sta $ffff
 lda #$34
 sta $01
 jsr layout_copy_tables
 jsr eg_init
 nop
 nop
 nop
 lda #$00
 sta $d01a
 sta $d015
 sta $d030
 sta $d020
 lda #0
 sta $d021
 lda #0
 sta $d011
 ldx #$15
clear_state:
 sta $02,x
 dex
 bpl clear_state
 jsr init_video_standard
 lda #0
 sta cpu_fast
 lda #$ff
 sta $dd04
 sta $dd05
 lda #$11
 sta $dd0e ; CIA2 timer A free-running; NMI interrupts remain masked
 lda $dd02
 ora #3
 sta $dd02
 lda $dd00
 and #$fc
 ora #2
 sta $dd00
 lda #$ff
 sta $dc02
 sta $dc00
 sta $d02f
 lda #0
 sta $dc03
 ; Every screen byte outside 0..999, including sprite pointers, is guarded.
 ldx #0
 lda #$a5
init_screens:
 sta $4000,x
 sta $4100,x
 sta $4200,x
 sta $4300,x
 sta $cc00,x
 sta $cd00,x
 sta $ce00,x
 sta $cf00,x
 inx
 bne init_screens
 ldx #119
init_ui:
 lda ui_text,x
 sta $4000,x
 sta $cc00,x
 lda #1
 sta $d800,x
 dex
 bpl init_ui
 ldx #0
 lda #7
init_color:
 sta $d878,x
 sta $d978,x
 sta $da78,x
 inx
 bne init_color
 ldx #111
init_color_tail:
 sta $db78,x
 dex
 bpl init_color_tail
 ldx #0
 lda #$98
palette_screen:
 sta $4078,x
 sta $4178,x
 sta $4278,x
 sta $cc78,x
 sta $cd78,x
 sta $ce78,x
 inx
 bne palette_screen
 ldx #111
palette_tail:
 sta $4378,x
 sta $cf78,x
 dex
 bpl palette_tail
 lda #$3f
 sta $ff00
 ldx #0
copy_second_font:
 lda $5800,x
 sta $d800,x
 lda $5900,x
 sta $d900,x
 lda $5a00,x
 sta $da00,x
 lda $5b00,x
 sta $db00,x
 ; UI contains only codes <128. Upper font halves are not fetched by VIC.
 ; $5c00..$623f is resident map RAM, never copied into the second font.
 inx
 bne copy_second_font
 lda #$3e
 sta $ff00
 lda #11
 sta $d022
 lda #12
 sta $d023
.if TEXTURED = 0
 ldx #79
init_strips:
 lda synthetic_lo,x
 sta strip_lo,x
 lda synthetic_hi,x
 sta strip_hi,x
 dex
 bpl init_strips
.endif
.if RAYCAST != 0
 jsr init_camera
.endif
.if TEXTURED != 0
 jsr init_simulation
 jsr latch_pose
 jsr raycast_layers
 jsr select_strips
.endif
 jsr vp_clear_frame
 jsr native_shadow_clear
 lda #0
 sta drawbuf
 jsr compose_screen
 lda #1
 sta drawbuf
 jsr compose_screen
.if DIAGNOSTIC != 0
 ldx #0
diag_codes:
 txa
 sta $4078,x
 sta $4478,x
 inx
 bne diag_codes
.endif
 nop
 nop
 nop
 lda #$1b
 sta $d011
 lda #$18 ; UI cells have Color RAM bit3=0, so remain hires.
 sta $d016
 lda #$06
 sta $d018
 lda #0
 sta $d012
 lda #1
 sta $d019
 sta $d01a
 cli
main_loop:
 jsr consume_video_ticks
 jsr eg_stream
render_frame_begin:
 lda sim_ticks
 sta frame_pose_tick
 lda sim_ticks+1
 sta frame_pose_tick+1
.if RAYCAST != 0
 jsr latch_pose
 jsr raycast_layers
.if TEXTURED != 0
 jsr select_strips
.endif
.endif
.if DIAGNOSTIC = 0
 jsr compose_screen
.endif
render_frame_end:
 lda #1
 sta ready ; release flag set ONLY after all 880 cells and UI are complete
wait_present:
 jsr consume_video_ticks
 lda ready
 bne wait_present
presentation_done:
 jmp main_loop

; Adapted from frozen build-3Dvibe64.ps1:10616 detect_video_standard.
; Same high-raster threshold, autonomous state; no KERNAL assumption.

frame_pose_tick: .word 0
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
