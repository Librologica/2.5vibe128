"""Build the native 2.5D SDK. Python standard library and 64tass only."""
import argparse,json,os,shutil,sys
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from mode8.build import load,validate
from native_builder import build as native_build,sha


def build(scene,out=None,run='interactive',validate_only=False):
    scene=Path(scene).resolve();data=load(scene);contract=validate(data)
    if run not in ('auto','interactive'):raise ValueError('RUN: auto or interactive required')
    if validate_only:return contract
    if out is None:raise ValueError('OUTPUT_DIRECTORY: --out required')
    out=Path(out).resolve()
    if out==ROOT or out.is_relative_to(ROOT) or out.exists():
        raise ValueError('OUTPUT_DIRECTORY: use a new directory outside SDK')
    exe=os.environ.get('TASS64_EXE') or shutil.which('64tass') or shutil.which('64tass.exe')
    if not exe:raise ValueError('DEPENDENCY: install 64tass or set TASS64_EXE')
    import native_builder
    native_builder.TASS=Path(exe)
    package=load(ROOT/'PACKAGE-MANIFEST.json')
    if package['platform']=='c128':
        result=native_build(scene,out,run,'raster','combined-pipelined',247,False,True)
        filename='2.5Vibe128-VICII.prg'
    else:
        result=native_build(out,run,'combined',scene)
        filename='2.5VibePlus4.prg'
    expected=load(ROOT/'tests/contracts.json')['referenceC64'].get(sha(scene))
    if expected and result['referencePrgSHA256']!=expected[run]:
        raise ValueError('BASELINE_MISMATCH: intermediate reference differs')
    final=out/(package['name']+'.prg')
    shutil.copyfile(out/'native'/filename,final)
    result.update(package=package['name'],version=package['version'],outputPRG=final.name)
    (out/'build.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--scene',required=True)
    p.add_argument('--out')
    p.add_argument('--run',choices=('auto','interactive'),default='interactive')
    p.add_argument('--validate-only',action='store_true')
    a=p.parse_args()
    try:print(json.dumps(build(a.scene,a.out,a.run,a.validate_only),indent=2))
    except (ValueError,OSError) as e:p.exit(2,str(e)+'\n')
