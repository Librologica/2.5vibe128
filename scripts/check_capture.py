"""Independent frozen bitmap oracle plus native VIC/MMU/palette checks."""
from pathlib import Path
from functools import lru_cache
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.dont_write_bytecode=True
sys.path.insert(0,str(ROOT/'src'))
from mode8.reference import adapter
from mode8.build import load
from mode8.navigation import simulate
def memory(path):
    b=path.read_bytes();i=b.index(b'C128MEM');assert b[21:37].rstrip(b'\0')==b'C128'
    assert b[i+16:i+18]==bytes([0,0])
    return b[i+22:i+33],b[i+33:i+33+65536]
@lru_cache(maxsize=24)
def setup(build):
    data=load(build/'reference/scene.json');c,oracle,meta=adapter(data)
    return data,oracle,simulate(data['scene'],data['navigation'],backend=c['backend'])[0]
def check(build,capture,frame=3,injected=False,stem=None):
    build=Path(build);capture=Path(capture);stem=stem or f'frame-{frame:03d}';cfg=load(build/'build.json')
    mmu,ram=memory(capture/(stem+'.vsf'))
    if frame is None:frame=int.from_bytes(ram[18:20],'little')
    assert mmu[0]==0x3e and mmu[6]==0x0f and mmu[9]==1 and not mmu[5]&0x40,mmu.hex()
    pose=[int.from_bytes(ram[a:a+2],'little') for a in (0x26,0x28,0x2a)]
    pose += [ram[0x2d],ram[0x2f]] if cfg['family']=='two-levels' else [32,0]
    data,oracle,poses=setup(build);expected=oracle(pose)[0]
    display=ram[7];actual=ram[0x63c0+display*0x8000:0x7f40+display*0x8000]
    assert len(expected)==len(actual)==7040
    diff=sum(x!=y for x,y in zip(expected,actual));assert diff==0,('bitmap',pose,display,diff,[(hex(0x63c0+i+display*0x8000),x,y) for i,(x,y) in enumerate(zip(expected,actual)) if x!=y][:8])
    tick=int.from_bytes(ram[20:22],'little');assert ram[0x11]==0
    labels={x.split()[2][1:]:int(x.split()[1],16) for x in (build/'native/engine.labels').read_text().splitlines()}
    pose_tick=int.from_bytes(ram[labels['frame_pose_tick']:labels['frame_pose_tick']+2],'little') if 'frame_pose_tick' in labels else tick
    assert pose_tick<=tick
    if not injected:
        assert tuple(pose)==tuple(poses[pose_tick] if cfg['run']=='auto' else data['scene']['initial']),('pose',pose_tick,pose)
        camera=[int.from_bytes(ram[a:a+2],'little') for a in (0x20,0x22,0x24)]
        assert camera==list((poses[tick] if cfg['run']=='auto' else data['scene']['initial'])[:3]),('live camera',tick,camera)
    assert ram[8]==0 and ram[6]==display^1 and display==frame%2,'publication order'
    if cfg['family']=='two-levels':assert ram[0xf2]==0,'event overflow'
    color=bytes(x&15 for x in (capture/(stem+'-color.bin')).read_bytes());assert color==bytes([1]*120+[7]*880)
    port=(capture/(stem+'-port.bin')).read_bytes();assert port[1]&7==4,('port',port.hex())
    vic=(capture/(stem+'-vic.bin')).read_bytes();cia=(capture/(stem+'-cia2.bin')).read_bytes()
    # With useful work during publication wait, foreground completion can be
    # later than raster 46. Validate the actual qualified IRQ phase rather
    # than assuming every capture lands in the top border.
    phase=ram[labels['irq_phase']]
    assert phase in (0,1,2,3)
    assert vic[0x30]&1==int(cfg['speed']=='raster' and phase in (0,1)),('D030',phase,vic[0x30])
    bitmap=phase in (0,3)
    expected_d011=0x7b if phase==0 and cfg.get('blankMargin') else ((0x33 if cfg.get('border24') else 0x3b) if bitmap else 0x1b)
    assert vic[0x11]&0x7f==expected_d011,('D011',phase,vic.hex())
    assert vic[0x18]&0xfe==((0x30 if display else 0)|(8 if bitmap else 6)),('D018',phase,vic.hex())
    assert vic[0x16]&0x1f==0x18 and vic[0x21]&15==0
    assert cia[0]&3==(0 if display else 2),('bank',cia.hex())
    font=(build/'native/font.bin').read_bytes();assert ram[0x5800:0x6000]==font==ram[0xd800:0xe000]
    labels={x.split()[2][1:]:int(x.split()[1],16) for x in (build/'native/engine.labels').read_text().splitlines()}
    engine=(build/'native/engine.prg').read_bytes()[2:]
    ui=engine[labels['ui_text']-0x801:labels['ui_text']-0x801+120]
    for address in (0x4000,0xcc00):
        assert all(ram[address+i]==v for i,v in enumerate(ui) if i not in (44,45)),'UI glyphs'
        assert all(48<=ram[address+i]<=57 for i in (44,45)),'FPS digits'
        assert ram[address+120:address+1000]==bytes([0x98]*880),'screen palette'
        assert ram[address+1000:address+1024]==bytes([0xa5]*24),'sprite-pointer guards'
    assert ram[0xff00:0xff05]==bytes(5),'MMU shadow backing RAM not zero'
    result=dict(frame=frame,pose=pose,simulationTick=tick,poseTick=pose_tick,display=display,bitmapDifferentBytes=diff,
                logicalPixelDifferences=0,mmu=mmu.hex(),nativeC128=True,palette=True)
    (capture/(stem+'-check.json')).write_text(json.dumps(result,indent=2)+'\n');print(result,flush=True);return result
if __name__=='__main__':check(Path(sys.argv[1]),Path(sys.argv[2]),int(sys.argv[3]) if len(sys.argv)>3 else 3)
