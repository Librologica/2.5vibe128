"""Native continuous procedural demo, isolated from the fixed-map SDK contract."""
from pathlib import Path
import argparse,sys,os,json,math,re,shutil,hashlib
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'src/infinite')]
import world
from native_builder import assemble
from mode8.build import replace
from ui_font import update_font

def labels(p):return {l.split()[2][1:]:int(l.split()[1],16) for l in p.read_text().splitlines()}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest().upper()
def build(out,run='auto',seed=None):
    out=Path(out).resolve()
    if out.is_relative_to(ROOT) or out.exists():raise ValueError('OUTPUT_DIRECTORY: new directory outside SDK required')
    if seed is not None and (type(seed)is not int or not 0<=seed<=0xffffffff):raise ValueError('SEED: unsigned 32-bit integer required')
    if run not in ('auto','interactive'):raise ValueError('RUN: auto or interactive required')
    package=json.loads((ROOT/'PACKAGE-MANIFEST.json').read_text());c128=package['platform']=='c128'
    dest=out/'native';dest.mkdir(parents=True)
    for p in (ROOT/'src/infinite').iterdir():
        if p.suffix in ('.asm','.bin'):shutil.copyfile(p,dest/p.name)
    s=(dest/'endless-interactive.asm').read_text()
    if run=='auto':s=s.replace('ENDLESS_AUTO=0','ENDLESS_AUTO=1')
    if seed is not None:s=s.replace('WORLD_FIXED_SEED=-1',f'WORLD_FIXED_SEED=${seed:08x}')
    (dest/'map.bin').write_bytes(world.world(world.START_ORIGIN,world.START_ORIGIN,seed or 0))
    (dest/'hash-a.bin').write_bytes(world.PERM_A);(dest/'hash-b.bin').write_bytes(world.PERM_B)
    (dest/'atan.bin').write_bytes(bytes(round(math.atan(i/128)*512/math.tau) for i in range(128)))
    font=update_font((dest/'font.bin').read_bytes())[:1024]
    (dest/'font.bin').write_bytes(font);(dest/'font-ui.bin').write_bytes(font)
    # Assemble neutral layout once, then replace hardware paths without moving geometry.
    (dest/'layout.asm').write_text(s);assemble(dest,'layout');lab=labels(dest/'layout.labels')
    initial=re.search(r'start:\n.*?(?=init_video_standard:)',s,re.S)[0]
    if c128:
        native=initial.replace('start:\n','native_init:\n',1)
        native=native.replace(' lda #$35\n sta $01\n',' lda #$34\n sta $01\n',1)
        native=native.replace(' lda #$34\n sta $01\n ldx #0\ncopy_second_font:',' lda #$3f\n sta $ff00\n ldx #0\ncopy_second_font:')
        native=native.replace(' lda #$35\n sta $01\n',' lda #$3e\n sta $ff00\n')
        native=native.replace(' jsr vp_clear_frame\n',' jsr vp_clear_frame\n jsr native_shadow_clear\n')
        native=native.replace(' sta $dc00\n',' sta $dc00\n sta $d02f\n',1).replace(' sta $d015\n',' sta $d015\n sta $d030\n',1)
        native=native.replace('render_frame_begin:\n','render_frame_begin:\n lda sim_ticks\n sta frame_pose_tick\n lda sim_ticks+1\n sta frame_pose_tick+1\n')
        native=native.replace('wait_present:\n','wait_present:\n jsr consume_video_ticks\n')
        native+='\nframe_pose_tick: .word 0\n'+(ROOT/'src/native/native.asm').read_text()
        irq=(ROOT/'src/native/irq.asm').read_text().replace(' lda #252\n sta $d012',' lda #247\n sta $d012').replace(' lda #$3b\n sta $d011',' lda #$33\n sta $d011')
        irq=irq.replace(' sta $d012\nirq_exit:',' sta $d012\n nop\n nop\n nop\nirq_exit:')
        s=s.replace(' sta $fec0,x',' jsr native_clear_tail')
    else:
        native=(ROOT/'src/native/init.asm').read_text()
        native=native.replace(' jsr layout_copy_tables\n',' jsr layout_copy_tables\n jsr eg_init\n')
        # TED may fetch the first margin glyph before the body IRQ completes.
        # The upper font half holds world RAM; blank both unused margin rows
        # in the color matrices, not in that live map. Viewport starts row 5.
        native=native.replace(' jsr init_camera\n',' ldx #79\n lda #0\nted_blank_margin:\n sta $d878,x\n sta $dc78,x\n dex\n bpl ted_blank_margin\n jsr init_camera\n')
        native=native.replace('render_frame_begin:\n',' jsr eg_stream\nrender_frame_begin:\n')
        native=native.replace(' jsr vp_clear_frame\n',' jsr vp_clear_frame\n ldx #63\n lda #0\nted_clear_safe_tail:\n sta $fcc0,x\n dex\n bpl ted_clear_safe_tail\n')
        irq=(ROOT/'src/native/irq.asm').read_text()
        detect='''init_video_standard:
 lda $ff07
 and #$40
 sta ted_standard_bit
 beq ted_pal
 lda #1
 sta video_standard
 lda #60
 sta video_hz
 rts
ted_pal:
 lda #0
 sta video_standard
 lda #50
 sta video_hz
 rts
'''
        s=re.sub(r'init_video_standard:\n.*?(?=consume_video_ticks:)',lambda m:detect+f' .fill ${lab["consume_video_ticks"]:04x}-*,0\n',s,flags=re.S)
        for a in ('fcc0','fdc0','fec0'):s=s.replace(' sta $'+a+',x',' nop\n nop\n nop')
        start=s.index('input_normal:\n');end=s.index('collision_check:',start)
        s=s[:start]+f'input_normal:\n jmp ted_read_controls\n .fill ${lab["collision_check"]:04x}-*,0\n'+s[end:]
        # Native TED raster/timer entropy, no absent CIA access. Fixed-seed path unchanged.
        p=dest/'world-runtime.asm';w=p.read_text()
        for a,b in (('$dc04','$ff00'),('$dc05','$ff01'),('$dd04','$ff1e'),('$dd05','$ff1c'),('$d012','$ff1d')):w=w.replace(a,b)
        p.write_text(w)
    s=re.sub(r'start:\n.*?(?=init_video_standard:)',lambda m:f'start:\n jmp native_init\n .fill ${lab["init_video_standard"]:04x}-*,0\n',s,flags=re.S)
    s=re.sub(r'irq:\n.*?nmi:\n rti\n',lambda m:irq+f'\n .fill ${lab["nmi"]+1:04x}-*,0\n',s,flags=re.S)
    assert s.count(' .fill $ba00-*,$00')==1
    s=s.replace(' .fill $ba00-*,$00',' .fill $b380-*,0\n .include "native.asm"\nnative_end:\n .cerror *>=$ba00,"Native code overlaps projection table"\n .fill $ba00-*,$00')
    text=['2.5Dvibe128' if c128 else '2.5VIBEPLUS4','FPS:00  INFINITE WORLD','AUTO EXPLORATION' if run=='auto' else 'W/S MOVE A/D TURN - JOYSTICK PORT 2']
    ui=''.join(t.ljust(40)[:40] for t in text).encode('ascii')
    s=re.sub(r'ui_text:\n.*?(?=direction_0:)',lambda m:'ui_text:\n .byte '+','.join(str(x) for x in ui)+'\n',s,flags=re.S)
    (dest/'native.asm').write_text(native)
    (dest/'engine.asm').write_text('BORDER_FAST=1\n'+s)
    assemble(dest,'engine');el=labels(dest/'engine.labels')
    for n in ('code_end','raycast_layers','compose_screen','latch_pose','simulation_tick','fx_height_lo','world_runtime'):
        assert lab[n]==el[n],('geometry address moved',n)
    assert el['world_map_end']==0x6240 and el['native_init']>=0xb380
    engine=(dest/'engine.prg').read_bytes();assert engine[:2]==b'\x01\x08'
    (dest/'payload.bin').write_bytes(engine[2:]);name='2.5Vibe128-VICII' if c128 else '2.5VibePlus4'
    (dest/f'{name}.asm').write_text((ROOT/'src/native/bootstrap.asm').read_text().replace('@PAYLOAD_BYTES@',str(len(engine)-2)))
    assemble(dest,name)
    shutil.copyfile(dest/f'{name}.prg',out/f'{package["name"]}-infinite-{run}.prg')
    report=dict(package=package['name'],version='1.1.0',demo='infinite',run=run,seed=seed,audio=False,viewport=[128,144],window=[40,40],visibleDistanceCells=18,coordinateBits=32,
        mapBase=0x5c00,mapBytes=1600,fontBytes=1024,nativeCodeBytes=el['native_end']-el['native_init'],nativeFree=0xba00-el['native_end'],
        proceduralCodeAndStateBytes=el['world_runtime_end']-el['world_runtime'],prgBytes=(dest/f'{name}.prg').stat().st_size,prgSHA256=sha(dest/f'{name}.prg'),
        family='infinite',speed='raster' if c128 else 'TED',cpuFastIRQLine=247 if c128 else None,border24=c128,kernel='infinite-pipelined')
    (out/'build.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));return report
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',required=True,type=Path);p.add_argument('--run',choices=('auto','interactive'),default='auto');p.add_argument('--seed',type=lambda s:int(s,0))
    a=p.parse_args();build(a.out,a.run,a.seed)
