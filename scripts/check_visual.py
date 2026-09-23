"""Fresh-start complete-scanout screenshots, checked against the latched pose."""
import argparse,json,os,subprocess,sys
from pathlib import Path
from PIL import Image
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from run_vice import VICE
from check_capture import setup


def visual(build,standard='pal',frame=3):
    b=Path(build).resolve()
    if b.is_relative_to(ROOT):raise ValueError('External build required')
    c128=json.loads((ROOT/'PACKAGE-MANIFEST.json').read_text())['platform']=='c128'
    out=b/f'visual-{standard}-{frame}';out.mkdir()
    # x128's generic monitor screenshot can select the VDC canvas. Its
    # explicit VIC-II exit screenshot captures the required 40-column output.
    cb=out/'capture.mon';cb.write_text('quit\n' if c128 else f'screenshot "{out.as_posix()}/screen.png" 2\nquit\n')
    capture=f'dump "{out.as_posix()}/published.vsf"' if c128 else f'bank ram\nbsave "{out.as_posix()}/published.bin" 0 $0000 $ffff'
    pb=out/'pose.mon';pb.write_text(capture+'\ndisable 2\nenable 3\nx\n')
    cond=f'if (@ram:$0012 == ${frame:02x}) && (@ram:$0013 == $00)'
    mon=out/'run.mon'
    mon.write_text('\n'.join([f'logname "{out.as_posix()}/trace.log"','log on','disable 1','sidefx off',
        f'load_labels "{b.as_posix()}/native/engine.labels"',f'break exec .presentation_done {cond}',
        f'command 2 "playback \\"{pb.as_posix()}\\""',f'break exec .irq_top {cond}',
        f'command 3 "playback \\"{cb.as_posix()}\\""','disable 3','x'])+'\n')
    native='2.5Vibe128-VICII.prg' if c128 else '2.5VibePlus4.prg'
    opts=['+go64','-40col','-VICIIfilter','0'] if c128 else ['-model','plus4','-TEDfilter','0']
    cmd=[str(VICE),'-default','+confirmonexit','-console','-warp',*opts,'-'+standard,
        '-autostartprgmode','1','-initbreak','0x1c0d' if c128 else '0x100d','-moncommands',str(mon),
        '-limitcycles','18000000',*(['-exitscreenshotvicii',str(out/'screen.png')] if c128 else []),str(b/'native'/native)]
    st=None
    if os.name=='nt':
        st=subprocess.STARTUPINFO();st.dwFlags|=subprocess.STARTF_USESHOWWINDOW;st.wShowWindow=0
    p=subprocess.run(cmd,capture_output=True,timeout=90,startupinfo=st)
    (out/'console.log').write_bytes(p.stdout+p.stderr)
    if c128:
        from check_capture import memory
        r=memory(out/'published.vsf')[1]
    else:r=(out/'published.bin').read_bytes()
    pose=[int.from_bytes(r[a:a+2],'little') for a in (38,40,42)]
    pix=setup(b)[1](pose)[1];im=Image.open(out/'screen.png').convert('RGB')
    top=(75 if standard=='pal' else 63) if c128 else (80 if standard=='pal' else 58)
    left=64;palette={};bad=[]
    for y in range(144):
        for x in range(128):
            code=pix[y*128+x];rgb=im.getpixel((left+x*2,top+y))
            if code in palette and rgb!=palette[code]:bad.append((x,y,code))
            else:palette[code]=rgb
            if im.getpixel((left+x*2+1,top+y))!=rgb:bad.append((x,y,'pair'))
    assert not bad,('physical bitmap',bad[:10],len(bad))
    assert len(set(palette.values()))==len(palette),'colors collapsed'
    # Both platforms share a 16-line black gap after the three text rows.
    outside=[(x,y) for y in range(top-16,top+160) for x in range(32,352)
        if not(left<=x<left+256 and top<=y<top+144) and im.getpixel((x,y))!=(0,0,0)]
    assert not outside,('margin',outside[:10])
    result=dict(standard=standard,frame=frame,pose=pose,physicalPixelDifferences=0,marginDifferences=0,palette=palette)
    (out/'visual.json').write_text(json.dumps(result,indent=2)+'\n');print(result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',required=True)
    p.add_argument('--standard',choices=('pal','ntsc'),default='pal');p.add_argument('--frame',type=int,default=3)
    a=p.parse_args();visual(a.build,a.standard,a.frame)
