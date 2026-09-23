"""Isolated, exact compile-time kernels. No changes to the frozen generator."""
import re

def ceiling():
    # Same alternating $44/$11 bytes as ef_clear_ceiling_row, but direct
    # compile-time addresses and a Y row counter. X = character column*8.
    lines=['nx_ceiling:', ' lda drawbuf', ' bne nx_ceiling_b',
           ' lda col',' asl',' asl',' asl',' tax',' ldy band_count',
           ' jmp nx_ceiling_a_0','nx_ceiling_b:',
           ' lda col',' asl',' asl',' asl',' tax',' ldy band_count',
           ' jmp nx_ceiling_b_0']
    for bank,base in [('a',0x6660),('b',0xe660)]:
        for row in range(18):
            lines += [f'nx_ceiling_{bank}_{row}:',' lda #$44']
            lines += [f' sta ${base+320*row+i:04x},x' for i in (0,2,4,6)]
            lines += [' lda #$11']
            lines += [f' sta ${base+320*row+i:04x},x' for i in (1,3,5,7)]
            # Local exit avoids 64tass expanding long forward BEQ instructions.
            lines += [' dey',f' bne nx_ceiling_{bank}_{row+1}',' jmp nx_ceiling_done']
        lines += [f'nx_ceiling_{bank}_18:']
    lines += ['nx_ceiling_done:',' lda #0',' sta band_count',' rts']
    return '\n'.join(lines)+'\n'

def apply(s,variant,labels):
    extra=''
    if variant in ('ceiling','combined'):
        start=s.index(' jsr band_address\nef_clear_ceiling_row:')
        end=s.index('ef_no_ceiling:',start)
        oldaddr=labels['ef_no_ceiling']
        s=s[:start]+f' jsr nx_ceiling\n jmp ef_no_ceiling\n .fill ${oldaddr:04x}-*,0\n'+s[end:]
        extra+=ceiling()
    if variant in ('fill-y','combined'):
        # Preserve all existing entry-point addresses; register decrement is
        # smaller/faster. Three padding bytes remain untouched after the exit.
        start=s.index('fill_rows:');end=s.index('clear_view:',start)
        block=s[start:end]
        # The existing entry table consumes Y before the row counter can load.
        block=block.replace(' lda band_shade\n jmp (fill_ptr)',
                            ' lda band_shade\n ldy band_count\n jmp (fill_ptr)',1)
        # Entry addresses are allowed to move within this reserved fill region.
        block=block.replace(' dec band_count\n beq fill_done', ' dey\n beq fill_done')
        block=block.replace('fill_done:\n rts','fill_done:\n sty band_count\n rts')
        s=s[:start]+block+f' .fill ${labels["clear_view"]:04x}-*,0\n'+s[end:]
    return s,extra
