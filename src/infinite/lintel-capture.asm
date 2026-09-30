; Per fine sample: retain all encountered overhead volumes before DDA resumes.
; Eight is a checked capacity for the compact 8-cell-module / 13-cell-view map.
; A ray crosses at most three overhead slab groups per axis in that interval.
PX_CAPACITY=8
px_count=$2f96
px_max=$2f97
px_level=$2f98
px_slot=$2f99
px_sub=$2f9a
px_overflow=$2f9c
px_coarse_counts=$2fc0 ; even indices of 64 bytes, one per coarse ray
px_plane=$b280
px_front_lo=$b2a0
px_front_hi=$b2c0
px_exit_plane=$b2e0
px_exit_lo=$b300
px_exit_hi=$b320
px_side=$b340
px_counts=$b360 ; four lane counts, no bulk clear required

px_capture:
 lda px_count
 cmp #PX_CAPACITY
 bcc px_capture_room
 inc px_overflow
 rts
px_capture_room:
 asl
 asl
 ora ss_sub
 tay
 ldx ray_index
 lda fx_near_plane,x
 sta px_plane,y
 lda fx_near_depth,x
 sta px_front_lo,y
 lda fx_near_depth_hi,x
 sta px_front_hi,y
 lda fx_exit_plane,x
 sta px_exit_plane,y
 lda exit_depth,x
 sta px_exit_lo,y
 lda exit_depth_hi,x
 sta px_exit_hi,y
 lda upper_side,x
 sta px_side,y
 inc px_count
 rts
