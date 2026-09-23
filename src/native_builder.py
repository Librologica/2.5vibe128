"""Native 2.5D platform adapter; no polygonal renderer."""
from pathlib import Path
import argparse, hashlib, json, os, re, shutil, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'src'))
from mode8.build import build as reference_build, labels, load, replace
TASS=Path(os.environ.get('TASS64_EXE') or shutil.which('64tass') or shutil.which('64tass.exe') or '64tass')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()

def assemble(dest,name):
    args=[str(TASS),'-a','-B','--m6502',f'--labels={name}.labels','--vice-labels-numeric',f'--list={name}.listing','-o',f'{name}.prg',f'{name}.asm']
    p=subprocess.run(args,cwd=dest,capture_output=True)
    (dest/f'{name}.assembler.log').write_bytes(p.stdout+p.stderr)
    if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
def build(scene,out,run='auto',speed='raster',kernel='combined-pipelined',fast_line=252,blank_margin=False,border24=False):
    if not 235 <= fast_line <= 252:
        raise ValueError('Fast IRQ must follow the last viewport scanline (234)')
    if blank_margin and fast_line==252:
        raise ValueError('Blanking is only useful inside the unused bottom margin')
    if border24 and (fast_line<247 or blank_margin):
        raise ValueError('24-row border: FAST IRQ at/after 247; register store follows border close; no invalid mode')
    if kernel not in ('baseline','ceiling','fill-y','combined','pipelined','combined-pipelined'):
        raise ValueError('Unknown experimental kernel')
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) or out.exists():raise ValueError('OUTPUT_DIRECTORY: use a new directory outside SDK')
    os.environ['TASS64_EXE']=str(TASS)
    base=out/'reference';r=reference_build(scene,base,run);family=r['contract']['family'];lab=labels(base)
    assert family=='apertures','This private build is limited to demo 2'
    if kernel in ('ceiling','combined','combined-pipelined'):
        assert r['viewport']==[128,144], 'Direct ceiling kernel is specialized for the qualified 128x144 layout only'
    dest=out/'native';dest.mkdir()
    s=(base/'3Dvibe64.asm').read_text()
    initial=re.search(r'start:\n.*?(?=init_video_standard:)',s,re.S)[0]
    initial=initial.replace('start:\n','native_init:\n',1)
    initial=initial.replace(' lda #$35\n sta $01\n',' lda #$34\n sta $01\n',1)
    initial=initial.replace(' lda #$34\n sta $01\n ldx #0\ncopy_second_font:', ' lda #$3f\n sta $ff00\n ldx #0\ncopy_second_font:')
    initial=initial.replace(' lda #$35\n sta $01\n',' lda #$3e\n sta $ff00\n')
    initial=initial.replace(' jsr vp_clear_frame\n',' jsr vp_clear_frame\n jsr native_shadow_clear\n')
    initial=initial.replace(' sta $dc00\n',' sta $dc00\n sta $d02f\n',1)
    initial=initial.replace(' sta $d015\n',' sta $d015\n sta $d030\n',1)
    pipelined=kernel in ('pipelined','combined-pipelined')
    state='' 
    if pipelined:
        state=' .fill $0879-*,0\nframe_pose_tick: .word 0\n'
        # Simulation uses cam_x/cam_y, not latched pose_x/pose_y. Once bitmap is
        # complete its camera remains stable while queued ticks are consumed.
        initial=initial.replace('render_frame_begin:\n','render_frame_begin:\n lda sim_ticks\n sta frame_pose_tick\n lda sim_ticks+1\n sta frame_pose_tick+1\n',1)
        initial=initial.replace('wait_present:\n',' jsr consume_video_ticks\nwait_present:\n',1)
    (dest/'frame-state.asm').write_text(state)
    s=re.sub(r'start:\n.*?(?=init_video_standard:)',lambda m:f'start:\n jmp native_init\n .include "frame-state.asm"\n .fill ${lab["init_video_standard"]:04x}-*,0\n',s,count=1,flags=re.S)
    irq=(ROOT/'src/native/irq.asm').read_text()
    assert irq.count(' lda #252\n sta $d012')==1
    irq=irq.replace(' lda #252\n sta $d012',f' lda #{fast_line}\n sta $d012',1)
    if border24:
        assert irq.count(' lda #$3b\n sta $d011')==1
        # Top text has already opened the border with RSEL=1. Select RSEL=0
        # only at the body split: bottom border closes at 247, wholly below
        # the active viewport ending at 234. No invalid display mode.
        irq=irq.replace(' lda #$3b\n sta $d011',' lda #$33\n sta $d011',1)
    if blank_margin:
        # ECM+BMM is an invalid (black) VIC display mode. Use only below
        # the 128x144 viewport; irq_top restores the unchanged text mode.
        irq=irq.replace('irq_fast:\n','irq_fast:\n lda #$7b\nmargin_blank_store:\n sta $d011\n',1)
    assert irq.count(' sta $d012\nirq_exit:')==1
    irq=irq.replace(' sta $d012\nirq_exit:',' sta $d012\n nop\n nop\n nop\nirq_exit:',1)
    s=re.sub(r'irq:\n.*?nmi:\n rti\n',lambda m:irq+f'\n .fill ${lab["nmi"]+1:04x}-*,0\n',s,count=1,flags=re.S)
    # Cold clear only: skip MMU shadow registers; their backing RAM is cleared
    # through a temporary stack-page alias, with IRQ/NMI disabled at boot.
    s,n=re.subn(r'(vp_clear_frame:\n.*?)( sta \$fec0,x)(.*? rts\n)',lambda m:m[1]+' jsr native_clear_tail'+m[3],s,count=1,flags=re.S)
    assert n==1
    assert s.count(' .fill 2449,0')==1
    extra=''
    if kernel not in ('baseline','pipelined'):
        from kernels import apply
        # Baseline native addresses retain the source generator's fill/clear
        # addresses; all entry relocation stays inside the reserved region.
        s,extra=apply(s,'combined' if kernel=='combined-pipelined' else kernel,lab)
    native=initial+'\n'+(ROOT/'src/native/native.asm').read_text()+'\nnx_extra_begin:\n'+extra+'nx_extra_end:\n'
    (dest/'native.asm').write_text(native)
    s=s.replace(' .fill 2449,0',' .include "native.asm"\n native_end:\n .cerror *>$b991,"native budget"\n .fill $b991-*,0')
    # Keep the existing FPS cells (44/45) and IRQ addresses unchanged.
    text=['2.5Dvibe128', 'FPS:00', '']
    s=replace(s,'ui_text',''.join(t.ljust(40)[:40] for t in text).encode('ascii'))
    s=f'BORDER_FAST={int(speed=="raster")}\n'+s
    (dest/'engine.asm').write_text(s)
    for name in ('font.bin','map.bin'):
        if (base/name).exists():shutil.copyfile(base/name,dest/name)
    from ui_font import update_font
    (dest/'font.bin').write_bytes(update_font((dest/'font.bin').read_bytes()))
    assemble(dest,'engine')
    el={x.split()[2][1:]:int(x.split()[1],16) for x in (dest/'engine.labels').read_text().splitlines()}
    assert el['code_end']==lab['code_end']
    for n in ('compose_screen','simulation_tick','latch_pose','vp_clear_frame'):assert el[n]==lab[n],n
    engine=(dest/'engine.prg').read_bytes();assert engine[:2]==b'\x01\x08'
    (dest/'payload.bin').write_bytes(engine[2:])
    (dest/'2.5Vibe128-VICII.asm').write_text((ROOT/'src/native/bootstrap.asm').read_text().replace('@PAYLOAD_BYTES@',str(len(engine)-2)))
    assemble(dest,'2.5Vibe128-VICII')
    report=dict(project='2.5vibe128',family=family,run=run,speed=speed,referencePrgSHA256=r['prgSHA256'],
        prgSHA256=sha(dest/'2.5Vibe128-VICII.prg'),prgBytes=(dest/'2.5Vibe128-VICII.prg').stat().st_size,
        geometryAddressesPreserved=True,nativeCodeBytes=el['native_end']-el['native_init'],
        viewport=[128,144],bitmapBuffers=[0x6000,0xe000],screenBuffers=[0x4000,0xcc00],
        cpuSlowIRQLine=46,cpuFastIRQLine=fast_line,blankMargin=blank_margin,border24=border24,video='native C128 VIC-IIe multicolor + hires text UI',
        kernel=kernel,
        addedKernelBytes=el['nx_extra_end']-el['nx_extra_begin'])
    (out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report
