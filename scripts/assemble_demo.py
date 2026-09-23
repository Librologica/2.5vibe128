"""Assemble the complete published demo source into a new external folder."""
import argparse,json,os,shutil,subprocess,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]

def assemble(source,out):
    source=Path(source).resolve();out=Path(out).resolve()
    if out.is_relative_to(ROOT) or out.exists():raise ValueError('Use a new external output directory')
    exe=os.environ.get('TASS64_EXE') or shutil.which('64tass') or shutil.which('64tass.exe')
    if not exe:raise ValueError('64tass missing: PATH or TASS64_EXE required')
    cfg=json.loads((source/'source.json').read_text())
    out.mkdir(parents=True)
    for p in source.iterdir():
        if p.suffix in ('.asm','.bin'):shutil.copyfile(p,out/p.name)
    for name in ('engine',cfg['bootstrap']):
        cmd=[exe,'-a','-B','--m6502','-o',name+'.prg',name+'.asm']
        p=subprocess.run(cmd,cwd=out,capture_output=True)
        (out/(name+'.log')).write_bytes(p.stdout+p.stderr)
        if p.returncode:raise RuntimeError((p.stdout+p.stderr).decode(errors='replace'))
        if name=='engine':(out/'payload.bin').write_bytes((out/'engine.prg').read_bytes()[2:])
    import hashlib
    final=out/(cfg['bootstrap']+'.prg')
    actual=hashlib.sha256(final.read_bytes()).hexdigest().upper()
    if actual!=cfg['sha256']:raise ValueError('Demo source/reference mismatch')
    print(final,actual)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--source',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();assemble(a.source,a.out)
