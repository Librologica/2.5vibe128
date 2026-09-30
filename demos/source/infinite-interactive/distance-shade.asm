; Distance darkening disabled for this demo. Ceiling retino is independent.
DISTANCE_SHADE = 0
; Existing depth is unsigned Q8.8 perpendicular distance. Integer thresholds
; preserve the full precision of comparisons at exactly 9 and 12 cells.
FOG_MID = 9
FOG_FAR = 12
fog_pattern = $2fa0 ; 8 output bytes for the current four-pixel band
fog_even = $2fa8
fog_odd = $2fa9
fog_solid = $2faa
fog_depth = $2fb0 ; far[4], front[4], underside[4], high byte of depth

; A=depth high; preserve X (coarse bitmap column).
.if DISTANCE_SHADE
fog_coarse:
 ldy #$ff
 sty fog_even
 sty fog_odd
 cmp #FOG_MID
 bcc fog_prepare
 ldy #$cc
 sty fog_even
 cmp #FOG_FAR
 bcc fog_prepare
 ldy #$33
 sty fog_odd
fog_prepare:
 lda fog_even
 and fog_odd
 cmp #$ff
 lda #0
 rol
 sta fog_solid
 lda fog_even
 and band_shade
 sta fog_pattern
 sta fog_pattern+2
 sta fog_pattern+4
 sta fog_pattern+6
 lda fog_odd
 and band_shade
 sta fog_pattern+1
 sta fog_pattern+3
 sta fog_pattern+5
 sta fog_pattern+7
 rts

; X=0/4/8 into fine depth array, lane 0 is leftmost sample.
; Each pair of bits remains intact: a texel is original pigment or black.
fog_refined:
 ; Even-row even lanes and odd-row odd lanes remain lit at all levels.
 ; Only four decisions are needed for the other four sample positions.
 lda #$cc
 sta fog_even
 lda #$33
 sta fog_odd
 lda fog_depth+1,x
 cmp #FOG_MID
 bcs fog_lane3
 lda fog_even
 ora #$30
 sta fog_even
fog_lane3:
 lda fog_depth+3,x
 cmp #FOG_MID
 bcs fog_lane0
 lda fog_even
 ora #3
 sta fog_even
fog_lane0:
 lda fog_depth,x
 cmp #FOG_FAR
 bcs fog_lane2
 lda fog_odd
 ora #$c0
 sta fog_odd
fog_lane2:
 lda fog_depth+2,x
 cmp #FOG_FAR
 bcs fog_lanes_done
 lda fog_odd
 ora #$0c
 sta fog_odd
fog_lanes_done:
 jmp fog_prepare
.else
; Solid-colour path for every depth, including $ff. Preserve caller's X.
fog_coarse:
fog_refined:
 lda #$ff
 sta fog_even
 sta fog_odd
 lda #1
 sta fog_solid
 lda band_shade
 sta fog_pattern
 sta fog_pattern+1
 sta fog_pattern+2
 sta fog_pattern+3
 sta fog_pattern+4
 sta fog_pattern+5
 sta fog_pattern+6
 sta fog_pattern+7
 rts
.endif

; Full rows, only for dithered walls. The original fast STA abs,X path
; remains in use for solid walls and for the background floor.
fog_fill_rows:
 jsr band_address
fog_fill_next:
 lda fog_pattern
 ldy #0
 sta (outptr),y
 ldy #2
 sta (outptr),y
 ldy #4
 sta (outptr),y
 ldy #6
 sta (outptr),y
 lda fog_pattern+1
 ldy #1
 sta (outptr),y
 ldy #3
 sta (outptr),y
 ldy #5
 sta (outptr),y
 ldy #7
 sta (outptr),y
 dec band_count
 beq fog_fill_done
 clc
 lda outptr
 adc #$40
 sta outptr
 lda outptr+1
 adc #1
 sta outptr+1
 jmp fog_fill_next
fog_fill_done:
 rts
