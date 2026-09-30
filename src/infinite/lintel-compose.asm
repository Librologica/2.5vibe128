; Painter order is independent per logical pixel: far overhead -> near.
; Background wall was already drawn by ss_compose. Single-volume fast path
; is retained. Fine projection uses the existing Q11.5 and clipping routines.
px_compose:
 lda #1
 sta ss_active
 lda px_max
 sta px_level
px_layer:
 dec px_level
 lda #0
 sta px_sub
 sta ss_near_shade
px_sample:
 lda col
 asl
 asl
 ora px_sub
 sta ss_pixel
 lda px_level
 asl
 asl
 ora px_sub
 sta px_slot
 ldy px_sub
 lda px_level
 cmp px_counts,y
 bcc px_project
 lda #0
 sta ss_near_top,y
 sta ss_near_bottom,y
 sta ss_near_exit,y
 jmp px_shade
px_project:
 ldy px_slot
 lda px_plane,y
 cmp #$ff
 bne px_front
 lda #0
 tax
 beq px_store_front
px_front:
 jsr fx_slope
 ldy px_slot
 lda px_front_hi,y
 pha
 lda px_front_lo,y
 tay
 pla
 jsr fx_height
 jsr pf_project_front
px_store_front:
 ldy px_sub
 sta ss_near_top,y
 txa
 sta ss_near_bottom,y
 ldy px_slot
 lda px_exit_plane,y
 jsr fx_slope
 ldy px_slot
 lda px_exit_hi,y
 pha
 lda px_exit_lo,y
 tay
 pla
 jsr fx_height
 jsr fx_project_door
 ldy px_sub
 cmp ss_near_bottom,y
 bcs px_exit_ordered
 lda ss_near_bottom,y
px_exit_ordered:
 sta ss_near_exit,y
 ldy px_slot
 lda px_side,y
 eor #3
px_shade:
 asl ss_near_shade
 asl ss_near_shade
 ora ss_near_shade
 sta ss_near_shade
 inc px_sub
 lda px_sub
 cmp #4
 bne px_sample
 ldx #3
px_front_copy:
 lda ss_near_top,x
 sta top_samples,x
 lda ss_near_bottom,x
 sta bottom_samples,x
 dex
 bpl px_front_copy
 lda ss_near_shade
 sta band_shade
 jsr oc_near_refined
 ldx #3
px_under_copy:
 lda ss_near_bottom,x
 sta top_samples,x
 lda ss_near_exit,x
 sta bottom_samples,x
 dex
 bpl px_under_copy
 lda #$55
 sta band_shade
 jsr oc_near_refined
 lda px_level
 bne px_layer
 lda #0
 sta ss_active
 rts
