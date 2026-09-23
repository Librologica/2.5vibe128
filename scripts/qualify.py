"""Qualify a native build with VICE; output remains alongside that build."""
import argparse,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from run_vice import run
from check_capture import check
from timing import analyze


def qualify(build,standard='pal',frames=120,seconds=20):
    build=Path(build).resolve()
    if build.is_relative_to(ROOT):raise ValueError('Use an external build directory')
    package=json.loads((ROOT/'PACKAGE-MANIFEST.json').read_text())
    c128=package['platform']=='c128'
    cfg=json.loads((build/'build.json').read_text())
    if cfg['package']!=package['name']:raise ValueError('PLATFORM: wrong native build')
    hz=(985248 if standard=='pal' else 1022727) if c128 else (1773447 if standard=='pal' else 1789772)
    out=build/('qualification-'+standard)
    if out.exists():raise ValueError('Use a fresh build/capture directory')
    numbers=tuple(range(1,frames+1))
    run(build,standard,int(hz*max(85,seconds+12)),out.name,numbers,
        ('trace exec .fps_frame_done',) if c128 else ())
    checks=[check(build,out,n) for n in numbers]
    result=analyze(build,out,standard,seconds)
    result.update(checks=len(checks),bitmapDifferences=0,hardwareTest=False)
    (out/'checks.json').write_text(json.dumps(checks,indent=2)+'\n')
    (out/'qualification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='framePublications'},indent=2))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--build',required=True)
    p.add_argument('--standard',choices=('pal','ntsc'),default='pal')
    p.add_argument('--frames',type=int,default=120)
    p.add_argument('--seconds',type=float,default=20)
    a=p.parse_args();qualify(a.build,a.standard,a.frames,a.seconds)
