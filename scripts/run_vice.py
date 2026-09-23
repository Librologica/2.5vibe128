"""Native x128 capture/trace; no runtime profiling instructions inserted."""
from pathlib import Path
import argparse,json,subprocess,os,shutil
ROOT=Path(__file__).resolve().parents[1]
VICE=Path(os.environ.get('VICE_X128') or shutil.which('x128') or shutil.which('x128.exe') or 'x128')
PHASES=('render_frame_begin','render_frame_end','presentation_done','slow_store','fast_store','body_mode_store')
def run(build,standard='pal',cycles=12000000,tag='probe',frames=(3,4),extra=()):
    build=Path(build).resolve();out=build/tag;out.mkdir();native=build/'native'
    lines=[f'logname "{out.as_posix()}/trace.log"','log on','disable 1','sidefx off',f'load_labels "{native.as_posix()}/engine.labels"']
    lines += ['trace exec .'+n for n in PHASES]
    for i,frame in enumerate(frames,2+len(PHASES)):
        stem=f'frame-{frame:03d}'
        playback=[f'dump "{out.as_posix()}/{stem}.vsf"','bank cpu']
        for n,start,end in [('color',0xd800,0xdbe7),('vic',0xd000,0xd03f),('cia2',0xdd00,0xdd03),('port',0,1)]:
            playback += [f'bsave "{out.as_posix()}/{stem}-{n}.bin" 0 ${start:04x} ${end:04x}']
        playback += ['x'];(out/(stem+'.mon')).write_text('\n'.join(playback)+'\n')
        # otherwise correct snapshot of this frame at the same CPU address.
        lines += [f'break exec .presentation_done if (@cpu:$ff00 == $3e) && (@cpu:$0012 == ${frame&255:02x}) && (@cpu:$0013 == ${frame>>8:02x})',
                  f'command {i} "playback \\"{out.as_posix()}/{stem}.mon\\""']
    lines += list(extra)+['x'];(out/'run.mon').write_text('\n'.join(lines)+'\n')
    cmd=[str(VICE),'-default','+confirmonexit','-console','-warp','+go64','-40col','-'+standard,'-VICIIfilter','0',
         '-autostartprgmode','1','-initbreak','0x1c0d','-moncommands',str(out/'run.mon'),'-limitcycles',str(cycles),
         '-exitscreenshotvicii',str(out/'vic.png'),str(native/'2.5Vibe128-VICII.prg')]
    startup=None
    if os.name=='nt':
        startup=subprocess.STARTUPINFO();startup.dwFlags|=subprocess.STARTF_USESHOWWINDOW;startup.wShowWindow=0
    p=subprocess.run(cmd,capture_output=True,timeout=240,startupinfo=startup)
    (out/'console.log').write_bytes(p.stdout+p.stderr);(out/'run.json').write_text(json.dumps(dict(command=cmd,returncode=p.returncode),indent=2))
    assert (out/'trace.log').exists() and all((out/f'frame-{f:03d}.vsf').exists() for f in frames),'Incomplete VICE capture'
    print(out,p.returncode,flush=True);return out
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('build');p.add_argument('--standard',default='pal');p.add_argument('--tag',default='probe');p.add_argument('--cycles',type=int,default=12000000)
    a=p.parse_args();run(a.build,a.standard,a.cycles,a.tag)
