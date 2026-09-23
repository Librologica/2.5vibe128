"""Test native keyboard reads through VICE's keyboard matrix, not code patches."""
from pathlib import Path
import argparse,json,os,subprocess,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from run_vice import VICE

def check(build,standard):
    build=Path(build).resolve()
    if build.is_relative_to(ROOT):raise ValueError('Use an external build directory')
    cfg=json.loads((build/'build.json').read_text())
    assert cfg['run']=='interactive'
    c128=cfg['project']=='2.5vibe128'
    source=build/f'qualification-{standard}/frame-003.vsf'
    b=source.read_bytes();idx=b.index(b'KEYBOARD');data=idx+22
    assert b[idx+16:idx+18]==bytes([1,1]) and int.from_bytes(b[idx+18:idx+22],'little')==118
    lab={s.split()[2][1:]:int(s.split()[1],16) for s in (build/'native/engine.labels').read_text().splitlines()}
    parent=build/f'input-{standard}';parent.mkdir()
    results=[]
    for name,row,col,expected in [('none',0,0,0),('W',1,1,1),('S',1,5,2),('A',1,2,4),('D',2,2,8)]:
        out=parent/name;out.mkdir();snap=bytearray(b)
        snap[data:data+96]=bytes(96)
        if expected:
            snap[data+4*row:data+4*row+4]=(1<<col).to_bytes(4,'little')
            snap[data+64+4*col:data+64+4*col+4]=(1<<row).to_bytes(4,'little')
        (out/'pressed.vsf').write_bytes(snap)
        capture=(f'dump "{out.as_posix()}/sample.vsf"\n' if c128 else
                 f'bank ram\nbsave "{out.as_posix()}/sample.bin" 0 $0000 $ffff\n')
        cb=out/'capture.mon';cb.write_text(capture+'quit\n')
        lines=[f'logname "{out.as_posix()}/trace.log"','log on','disable 1','sidefx off',
               f'load_labels "{build.as_posix()}/native/engine.labels"',f'undump "{out.as_posix()}/pressed.vsf"',
               'break exec .input_sampled'+(' if (@cpu:$ff00 == $3e)' if c128 else ''),
               f'command 2 "playback \\"{cb.as_posix()}\\""','x']
        (out/'run.mon').write_text('\n'.join(lines)+'\n')
        cmd=[str(VICE),'-default','+confirmonexit','-console','-warp']
        cmd+=['+go64','-40col','-VICIIfilter','0'] if c128 else ['-model','plus4','-TEDfilter','0']
        cmd+=['-'+standard,'-autostartprgmode','1','-initbreak','0x1c0d' if c128 else '0x100d',
              '-moncommands',str(out/'run.mon'),'-limitcycles','200000000',str(build/cfg['outputPRG'])]
        startup=None
        if os.name=='nt':
            startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
        proc=subprocess.run(cmd,capture_output=True,timeout=60,startupinfo=startup)
        (out/'console.log').write_bytes(proc.stdout+proc.stderr)
        (out/'command.json').write_text(json.dumps(cmd,indent=2))
        if c128:
            from check_capture import memory
            r=memory(out/'sample.vsf')[1]
        else:r=(out/'sample.bin').read_bytes()
        actual=r[lab['keys']];assert actual==expected,(name,actual,expected)
        results.append(dict(key=name,actual=actual,expected=expected))
    result=dict(standard=standard,cases=results,method='VICE keyboard-matrix injection; actual native device reads; no engine patch',joystick='not exercised')
    (parent/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result));return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--build',type=Path,required=True);p.add_argument('--standard',choices=['pal','ntsc'],default='pal')
    a=p.parse_args();check(a.build,a.standard)
