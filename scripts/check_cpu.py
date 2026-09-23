"""Execute native geometry/fill instructions and compare independent bitmap oracle."""
import argparse,json,shutil,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from mode8.build import load
from mode8.reference import adapter
from mode8.navigation import simulate
from mode8.trace import Trace

def check(build,count=32):
    b=Path(build).resolve()
    if b.is_relative_to(ROOT):raise ValueError('External build required')
    native=b/'cpu-native';native.mkdir(exist_ok=True)
    for s,d in [('engine.prg','3Dvibe64.prg'),('engine.asm','3Dvibe64.asm'),('engine.labels','labels.txt')]:
        shutil.copyfile(b/'native'/s,native/d)
    data=load(b/'reference/scene.json');c,oracle,meta=adapter(data)
    poses=simulate(data['scene'],data['navigation'],backend=c['backend'])[0]
    t=Trace(native,c['backend'],meta);t.categories['nx_ceiling']='Fondo e soffitto'
    rows=[]
    for tick in [i*13603//(count-1) for i in range(count)]:
        result,bitmap=t.view(poses[tick])
        assert bitmap==oracle(poses[tick])[0],('bitmap mismatch',tick)
        rows.append(dict(tick=tick,bitmapDifferences=0,**result))
    (b/'cpu-model.json').write_text(json.dumps(rows,indent=2)+'\n')
    print(b.name,len(rows),'instruction-level poses PASS; not native FPS')

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--build',required=True);p.add_argument('--count',type=int,default=32)
    a=p.parse_args();check(a.build,a.count)
