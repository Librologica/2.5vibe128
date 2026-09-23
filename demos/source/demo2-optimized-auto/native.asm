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
 lda $5c00,x
 sta $dc00,x
 lda $5d00,x
 sta $dd00,x
 lda $5e00,x
 sta $de00,x
 lda $5f00,x
 sta $df00,x
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
 jsr consume_video_ticks
wait_present:
 lda ready
 bne wait_present
presentation_done:
 jmp main_loop

; Adapted from frozen build-3Dvibe64.ps1:10616 detect_video_standard.
; Same high-raster threshold, autonomous state; no KERNAL assumption.

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

nx_extra_begin:
nx_ceiling:
 lda drawbuf
 bne nx_ceiling_b
 lda col
 asl
 asl
 asl
 tax
 ldy band_count
 jmp nx_ceiling_a_0
nx_ceiling_b:
 lda col
 asl
 asl
 asl
 tax
 ldy band_count
 jmp nx_ceiling_b_0
nx_ceiling_a_0:
 lda #$44
 sta $6660,x
 sta $6662,x
 sta $6664,x
 sta $6666,x
 lda #$11
 sta $6661,x
 sta $6663,x
 sta $6665,x
 sta $6667,x
 dey
 bne nx_ceiling_a_1
 jmp nx_ceiling_done
nx_ceiling_a_1:
 lda #$44
 sta $67a0,x
 sta $67a2,x
 sta $67a4,x
 sta $67a6,x
 lda #$11
 sta $67a1,x
 sta $67a3,x
 sta $67a5,x
 sta $67a7,x
 dey
 bne nx_ceiling_a_2
 jmp nx_ceiling_done
nx_ceiling_a_2:
 lda #$44
 sta $68e0,x
 sta $68e2,x
 sta $68e4,x
 sta $68e6,x
 lda #$11
 sta $68e1,x
 sta $68e3,x
 sta $68e5,x
 sta $68e7,x
 dey
 bne nx_ceiling_a_3
 jmp nx_ceiling_done
nx_ceiling_a_3:
 lda #$44
 sta $6a20,x
 sta $6a22,x
 sta $6a24,x
 sta $6a26,x
 lda #$11
 sta $6a21,x
 sta $6a23,x
 sta $6a25,x
 sta $6a27,x
 dey
 bne nx_ceiling_a_4
 jmp nx_ceiling_done
nx_ceiling_a_4:
 lda #$44
 sta $6b60,x
 sta $6b62,x
 sta $6b64,x
 sta $6b66,x
 lda #$11
 sta $6b61,x
 sta $6b63,x
 sta $6b65,x
 sta $6b67,x
 dey
 bne nx_ceiling_a_5
 jmp nx_ceiling_done
nx_ceiling_a_5:
 lda #$44
 sta $6ca0,x
 sta $6ca2,x
 sta $6ca4,x
 sta $6ca6,x
 lda #$11
 sta $6ca1,x
 sta $6ca3,x
 sta $6ca5,x
 sta $6ca7,x
 dey
 bne nx_ceiling_a_6
 jmp nx_ceiling_done
nx_ceiling_a_6:
 lda #$44
 sta $6de0,x
 sta $6de2,x
 sta $6de4,x
 sta $6de6,x
 lda #$11
 sta $6de1,x
 sta $6de3,x
 sta $6de5,x
 sta $6de7,x
 dey
 bne nx_ceiling_a_7
 jmp nx_ceiling_done
nx_ceiling_a_7:
 lda #$44
 sta $6f20,x
 sta $6f22,x
 sta $6f24,x
 sta $6f26,x
 lda #$11
 sta $6f21,x
 sta $6f23,x
 sta $6f25,x
 sta $6f27,x
 dey
 bne nx_ceiling_a_8
 jmp nx_ceiling_done
nx_ceiling_a_8:
 lda #$44
 sta $7060,x
 sta $7062,x
 sta $7064,x
 sta $7066,x
 lda #$11
 sta $7061,x
 sta $7063,x
 sta $7065,x
 sta $7067,x
 dey
 bne nx_ceiling_a_9
 jmp nx_ceiling_done
nx_ceiling_a_9:
 lda #$44
 sta $71a0,x
 sta $71a2,x
 sta $71a4,x
 sta $71a6,x
 lda #$11
 sta $71a1,x
 sta $71a3,x
 sta $71a5,x
 sta $71a7,x
 dey
 bne nx_ceiling_a_10
 jmp nx_ceiling_done
nx_ceiling_a_10:
 lda #$44
 sta $72e0,x
 sta $72e2,x
 sta $72e4,x
 sta $72e6,x
 lda #$11
 sta $72e1,x
 sta $72e3,x
 sta $72e5,x
 sta $72e7,x
 dey
 bne nx_ceiling_a_11
 jmp nx_ceiling_done
nx_ceiling_a_11:
 lda #$44
 sta $7420,x
 sta $7422,x
 sta $7424,x
 sta $7426,x
 lda #$11
 sta $7421,x
 sta $7423,x
 sta $7425,x
 sta $7427,x
 dey
 bne nx_ceiling_a_12
 jmp nx_ceiling_done
nx_ceiling_a_12:
 lda #$44
 sta $7560,x
 sta $7562,x
 sta $7564,x
 sta $7566,x
 lda #$11
 sta $7561,x
 sta $7563,x
 sta $7565,x
 sta $7567,x
 dey
 bne nx_ceiling_a_13
 jmp nx_ceiling_done
nx_ceiling_a_13:
 lda #$44
 sta $76a0,x
 sta $76a2,x
 sta $76a4,x
 sta $76a6,x
 lda #$11
 sta $76a1,x
 sta $76a3,x
 sta $76a5,x
 sta $76a7,x
 dey
 bne nx_ceiling_a_14
 jmp nx_ceiling_done
nx_ceiling_a_14:
 lda #$44
 sta $77e0,x
 sta $77e2,x
 sta $77e4,x
 sta $77e6,x
 lda #$11
 sta $77e1,x
 sta $77e3,x
 sta $77e5,x
 sta $77e7,x
 dey
 bne nx_ceiling_a_15
 jmp nx_ceiling_done
nx_ceiling_a_15:
 lda #$44
 sta $7920,x
 sta $7922,x
 sta $7924,x
 sta $7926,x
 lda #$11
 sta $7921,x
 sta $7923,x
 sta $7925,x
 sta $7927,x
 dey
 bne nx_ceiling_a_16
 jmp nx_ceiling_done
nx_ceiling_a_16:
 lda #$44
 sta $7a60,x
 sta $7a62,x
 sta $7a64,x
 sta $7a66,x
 lda #$11
 sta $7a61,x
 sta $7a63,x
 sta $7a65,x
 sta $7a67,x
 dey
 bne nx_ceiling_a_17
 jmp nx_ceiling_done
nx_ceiling_a_17:
 lda #$44
 sta $7ba0,x
 sta $7ba2,x
 sta $7ba4,x
 sta $7ba6,x
 lda #$11
 sta $7ba1,x
 sta $7ba3,x
 sta $7ba5,x
 sta $7ba7,x
 dey
 bne nx_ceiling_a_18
 jmp nx_ceiling_done
nx_ceiling_a_18:
nx_ceiling_b_0:
 lda #$44
 sta $e660,x
 sta $e662,x
 sta $e664,x
 sta $e666,x
 lda #$11
 sta $e661,x
 sta $e663,x
 sta $e665,x
 sta $e667,x
 dey
 bne nx_ceiling_b_1
 jmp nx_ceiling_done
nx_ceiling_b_1:
 lda #$44
 sta $e7a0,x
 sta $e7a2,x
 sta $e7a4,x
 sta $e7a6,x
 lda #$11
 sta $e7a1,x
 sta $e7a3,x
 sta $e7a5,x
 sta $e7a7,x
 dey
 bne nx_ceiling_b_2
 jmp nx_ceiling_done
nx_ceiling_b_2:
 lda #$44
 sta $e8e0,x
 sta $e8e2,x
 sta $e8e4,x
 sta $e8e6,x
 lda #$11
 sta $e8e1,x
 sta $e8e3,x
 sta $e8e5,x
 sta $e8e7,x
 dey
 bne nx_ceiling_b_3
 jmp nx_ceiling_done
nx_ceiling_b_3:
 lda #$44
 sta $ea20,x
 sta $ea22,x
 sta $ea24,x
 sta $ea26,x
 lda #$11
 sta $ea21,x
 sta $ea23,x
 sta $ea25,x
 sta $ea27,x
 dey
 bne nx_ceiling_b_4
 jmp nx_ceiling_done
nx_ceiling_b_4:
 lda #$44
 sta $eb60,x
 sta $eb62,x
 sta $eb64,x
 sta $eb66,x
 lda #$11
 sta $eb61,x
 sta $eb63,x
 sta $eb65,x
 sta $eb67,x
 dey
 bne nx_ceiling_b_5
 jmp nx_ceiling_done
nx_ceiling_b_5:
 lda #$44
 sta $eca0,x
 sta $eca2,x
 sta $eca4,x
 sta $eca6,x
 lda #$11
 sta $eca1,x
 sta $eca3,x
 sta $eca5,x
 sta $eca7,x
 dey
 bne nx_ceiling_b_6
 jmp nx_ceiling_done
nx_ceiling_b_6:
 lda #$44
 sta $ede0,x
 sta $ede2,x
 sta $ede4,x
 sta $ede6,x
 lda #$11
 sta $ede1,x
 sta $ede3,x
 sta $ede5,x
 sta $ede7,x
 dey
 bne nx_ceiling_b_7
 jmp nx_ceiling_done
nx_ceiling_b_7:
 lda #$44
 sta $ef20,x
 sta $ef22,x
 sta $ef24,x
 sta $ef26,x
 lda #$11
 sta $ef21,x
 sta $ef23,x
 sta $ef25,x
 sta $ef27,x
 dey
 bne nx_ceiling_b_8
 jmp nx_ceiling_done
nx_ceiling_b_8:
 lda #$44
 sta $f060,x
 sta $f062,x
 sta $f064,x
 sta $f066,x
 lda #$11
 sta $f061,x
 sta $f063,x
 sta $f065,x
 sta $f067,x
 dey
 bne nx_ceiling_b_9
 jmp nx_ceiling_done
nx_ceiling_b_9:
 lda #$44
 sta $f1a0,x
 sta $f1a2,x
 sta $f1a4,x
 sta $f1a6,x
 lda #$11
 sta $f1a1,x
 sta $f1a3,x
 sta $f1a5,x
 sta $f1a7,x
 dey
 bne nx_ceiling_b_10
 jmp nx_ceiling_done
nx_ceiling_b_10:
 lda #$44
 sta $f2e0,x
 sta $f2e2,x
 sta $f2e4,x
 sta $f2e6,x
 lda #$11
 sta $f2e1,x
 sta $f2e3,x
 sta $f2e5,x
 sta $f2e7,x
 dey
 bne nx_ceiling_b_11
 jmp nx_ceiling_done
nx_ceiling_b_11:
 lda #$44
 sta $f420,x
 sta $f422,x
 sta $f424,x
 sta $f426,x
 lda #$11
 sta $f421,x
 sta $f423,x
 sta $f425,x
 sta $f427,x
 dey
 bne nx_ceiling_b_12
 jmp nx_ceiling_done
nx_ceiling_b_12:
 lda #$44
 sta $f560,x
 sta $f562,x
 sta $f564,x
 sta $f566,x
 lda #$11
 sta $f561,x
 sta $f563,x
 sta $f565,x
 sta $f567,x
 dey
 bne nx_ceiling_b_13
 jmp nx_ceiling_done
nx_ceiling_b_13:
 lda #$44
 sta $f6a0,x
 sta $f6a2,x
 sta $f6a4,x
 sta $f6a6,x
 lda #$11
 sta $f6a1,x
 sta $f6a3,x
 sta $f6a5,x
 sta $f6a7,x
 dey
 bne nx_ceiling_b_14
 jmp nx_ceiling_done
nx_ceiling_b_14:
 lda #$44
 sta $f7e0,x
 sta $f7e2,x
 sta $f7e4,x
 sta $f7e6,x
 lda #$11
 sta $f7e1,x
 sta $f7e3,x
 sta $f7e5,x
 sta $f7e7,x
 dey
 bne nx_ceiling_b_15
 jmp nx_ceiling_done
nx_ceiling_b_15:
 lda #$44
 sta $f920,x
 sta $f922,x
 sta $f924,x
 sta $f926,x
 lda #$11
 sta $f921,x
 sta $f923,x
 sta $f925,x
 sta $f927,x
 dey
 bne nx_ceiling_b_16
 jmp nx_ceiling_done
nx_ceiling_b_16:
 lda #$44
 sta $fa60,x
 sta $fa62,x
 sta $fa64,x
 sta $fa66,x
 lda #$11
 sta $fa61,x
 sta $fa63,x
 sta $fa65,x
 sta $fa67,x
 dey
 bne nx_ceiling_b_17
 jmp nx_ceiling_done
nx_ceiling_b_17:
 lda #$44
 sta $fba0,x
 sta $fba2,x
 sta $fba4,x
 sta $fba6,x
 lda #$11
 sta $fba1,x
 sta $fba3,x
 sta $fba5,x
 sta $fba7,x
 dey
 bne nx_ceiling_b_18
 jmp nx_ceiling_done
nx_ceiling_b_18:
nx_ceiling_done:
 lda #0
 sta band_count
 rts
nx_extra_end:
