"""Native infinite demo: emulated hardware + same-pose neutral 6510 oracle.

No hardware test is implied. Requires py65 and the platform VICE executable.
All captures and reports are written outside the SDK, beside a fresh build.
"""
from pathlib import Path
import argparse,json,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src/infinite'),str(ROOT/'src')]
import world
from py65.devices.mpu6502 import MPU
from run_vice import run
from timing import analyze

def labels(p):return {l.split()[2][1:]:int(l.split()[1],16) for l in p.read_text().splitlines()}
class Oracle:
    def __init__(self,native):
        self.lab=labels(native/'layout.labels');p=(native/'layout.prg').read_bytes()
        self.mem=[0]*65536;a=int.from_bytes(p[:2],'little');self.mem[a:a+len(p)-2]=p[2:]
        self.cpu=MPU(memory=self.mem)
        for n in ('layout_copy_tables','init_camera','init_simulation'):self.call(n)
    def call(self,n):
        self.cpu.sp=0xfd;self.mem[0x1fe:0x200]=[0xff,0x2f];self.cpu.pc=self.lab[n]
        for _ in range(5000000):
            self.cpu.step()
            if self.cpu.pc==0x3000:return
        raise AssertionError(('oracle timeout',n))
    def view(self,ram):
        self.mem[0x5c00:0x6240]=ram[0x5c00:0x6240]
        self.mem[0x20:0x26]=ram[0x26:0x2c]
        for n in ('latch_pose','raycast_layers','select_strips','vp_clear_frame'):self.call(n)
        self.mem[6]=0;self.call('compose_screen')
        return bytes(self.mem[0x63c0:0x7f40])

def check(build,out,frame,oracle):
    cfg=json.loads((build/'build.json').read_text());c128=cfg['package']=='2.5vibe128'
    stem=f'frame-{frame:03d}';lab=labels(build/'native/engine.labels')
    if c128:
        from check_capture import memory
        mmu,ram=memory(out/(stem+'.vsf'))
        assert mmu[0]==0x3e and mmu[6]==15 and mmu[9]==1 and not mmu[5]&0x40,'native MMU'
    else:ram=(out/(stem+'-ram.bin')).read_bytes()
    assert len(ram)==65536
    val=lambda n,k=1:int.from_bytes(ram[lab[n]:lab[n]+k],'little')
    seed=val('eg_seed',4);ox=val('eg_origin_x',4);oy=val('eg_origin_y',4)
    assert ram[0x5c00:0x6240]==world.world(ox,oy,seed),('procedural map',frame,seed,ox,oy)
    if cfg['seed'] is not None:assert seed==cfg['seed']
    expected=oracle.view(ram);display=ram[7]
    actual=ram[0x63c0+display*32768:0x7f40+display*32768]
    length=7040 if c128 else 6400
    diff=sum(a!=b for a,b in zip(actual[:length],expected[:length]))
    assert diff==0,('native bitmap vs neutral renderer',frame,diff)
    pose=[val(n,2) for n in ('pose_x','pose_y','pose_angle')]
    assert 20*256<=pose[0]<21*256 and 20*256<=pose[1]<21*256,('unstreamed pose',pose)
    assert val('frame_pose_tick',2)<=val('sim_ticks',2) and ram[17]==0,'logical ticks'
    assert int.from_bytes(ram[18:20],'little')==frame and ram[8]==0 and ram[6]==display^1 and display==frame%2,'complete publication'
    font=(build/'native/font.bin').read_bytes();assert len(font)==1024 and ram[0x5800:0x5c00]==font
    prg=(build/'native/engine.prg').read_bytes()[2:];ui=prg[lab['ui_text']-0x801:lab['ui_text']-0x801+120]
    if c128:
        assert ram[0xd800:0xdc00]==font
        color=bytes(x&15 for x in (out/(stem+'-color.bin')).read_bytes());assert color==bytes([1]*120+[7]*880)
        vic=(out/(stem+'-vic.bin')).read_bytes();cia=(out/(stem+'-cia2.bin')).read_bytes();port=(out/(stem+'-port.bin')).read_bytes()
        phase=ram[9];assert phase in (0,1,2,3)
        assert port[1]&7==4 and vic[0x30]&1==int(phase in (0,1))
        bitmap=phase in (0,3)
        assert vic[0x11]&0x7f==(0x33 if bitmap else 0x1b)
        assert vic[0x18]&0xfe==((0x30 if display else 0)|(8 if bitmap else 6))
        assert vic[0x16]&0x1f==0x18 and vic[0x21]&15==0 and cia[0]&3==(0 if display else 2)
        for a in (0x4000,0xcc00):
            assert all(ram[a+i]==v for i,v in enumerate(ui) if i not in (44,45))
            assert ram[a+44:a+46]==f'{ram[16]:02d}'.encode()
            assert ram[a+120:a+1000]==bytes([0x98])*880
            assert ram[a+1000:a+1024]==bytes([0xa5])*24
        assert ram[0xff00:0xff05]==bytes(5)
    else:
        ted=(out/(stem+'-ted.bin')).read_bytes()
        assert ram[0x7cc0:0x7f40]==expected[6400:]==bytes(640)
        assert ram[0xd800:0xd878]==bytes([0x71])*120 and ram[0xd878:0xdbe8]==bytes(80)+bytes([0x42])*800
        assert ram[0xdc78:0xdfe8]==bytes(80)+bytes([0x98])*800 and ram[0xdbe8:0xdc00]==ram[0xdfe8:0xe000]==bytes([0xa5])*24
        assert all(ram[0xdc00+i]==v for i,v in enumerate(ui) if i not in (44,45))
        assert ram[0xdc2c:0xdc2e]==f'{ram[16]:02d}'.encode()
        assert ted[0x13]&0xfe==0x58 and ted[0x14]&0xf8==0xd8 and ted[0x13]&1==0
        assert ted[0x15]&127==0 and ted[0x16]&127==0x67 and ted[0x19]&127==0
    return dict(frame=frame,seed=seed,origin=[ox,oy],pose=pose,poseTick=val('frame_pose_tick',2),simulationTick=val('sim_ticks',2),display=display,bitmapDifferences=0,pixelDifferences=0,map=True,font=True,palette=True,UI=True,bufferOrder=True)

def qualify(build,standard='pal',frames=120,tag=None):
    build=Path(build).resolve()
    if build.is_relative_to(ROOT):raise ValueError('External build required')
    cfg=json.loads((build/'build.json').read_text());assert cfg['demo']=='infinite'
    c128=cfg['package']=='2.5vibe128';hz=(985248 if standard=='pal' else 1022727) if c128 else (1773447 if standard=='pal' else 1789772)
    tag=tag or 'qualification-'+standard;out=build/tag
    if not out.exists():run(build,standard,int(hz*100),tag,tuple(range(1,frames+1)),('trace exec .fps_frame_done',) if c128 else ())
    oracle=Oracle(build/'native');checks=[]
    for f in range(1,frames+1):
        checks.append(check(build,out,f,oracle))
        if f%20==0:print(build.name,standard,f,'exact views',flush=True)
    timing=analyze(build,out,standard,20)
    result=dict(**timing,checks=len(checks),bitmapDifferences=0,hostWorldDifferences=0,hardwareTest=False)
    (out/'checks.json').write_text(json.dumps(checks,indent=2));(out/'qualification.json').write_text(json.dumps(result,indent=2))
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',required=True);p.add_argument('--standard',choices=('pal','ntsc'),default='pal');p.add_argument('--frames',type=int,default=120);p.add_argument('--tag')
    a=p.parse_args();qualify(a.build,a.standard,a.frames,a.tag)
