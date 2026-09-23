"""Public parser, scene, build and release contracts. No VICE required."""
import copy,hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src')]
from build import build
from mode8.build import validate,load
from mode8.font import font
BASE=load(ROOT/'examples/demo2-original.json')


class Contracts(unittest.TestCase):
    def bad(self,edit,code):
        d=copy.deepcopy(BASE);edit(d)
        with self.assertRaisesRegex(ValueError,code):validate(d)

    def test_valid_examples(self):
        for scene in ROOT.glob('examples/*.json'):
            c=validate(load(scene));self.assertEqual(c['backend'],'mono-portals')
            self.assertEqual(c['blockedTicks'],0);self.assertEqual(c['firstLapTick'],13603)

    def test_invalid_inputs(self):
        cases=[('DOCUMENT',lambda d:d.pop('scene')),
          ('DOCUMENT',lambda d:d.update(meshes=[])),
          ('FORMAT',lambda d:d.update(scene=None)),
          ('SCHEMA',lambda d:d['scene'].update(schema='polygon')),
          ('UNKNOWN_FIELD',lambda d:d['scene'].update(fov=55)),
          ('MISSING_FIELD',lambda d:d['scene'].pop('solid')),
          ('SIZE',lambda d:d['scene'].update(size=[31,32])),
          ('FORMAT',lambda d:d['scene'].update(doors=None)),
          ('FORMAT',lambda d:d['scene'].update(ramps=None)),
          ('FORMAT',lambda d:d['scene']['solid'].pop()),
          ('FORMAT',lambda d:d['scene']['solid'].__setitem__(0,True)),
          ('SOLID',lambda d:d['scene']['solid'].__setitem__(0,2)),
          ('BORDER',lambda d:d['scene']['solid'].__setitem__(0,0)),
          ('CAMERA_HEIGHT',lambda d:d['scene'].update(eyeHeight=31)),
          ('INTEGER',lambda d:d['scene'].update(playerHeight=None)),
          ('HEIGHT_UNIT',lambda d:d['scene'].update(heightUnit='WU')),
          ('FORMAT',lambda d:d['scene']['initial'].pop()),
          ('CAMERA',lambda d:d['navigation']['camera'].__setitem__(0,1000)),
          ('NAV_FORMAT',lambda d:d['navigation'].update(nodes=None)),
          ('FORMAT',lambda d:d['navigation']['nodes'][0].__setitem__(0,1.5)),
          ('NAV_COORD',lambda d:d['navigation']['nodes'][0].__setitem__(0,8192)),
          ('MONO_NAV',lambda d:d['navigation']['nodes'][1].__setitem__(0,d['navigation']['nodes'][1][0]+1)),
          ('MONO_APERTURES',lambda d:d['scene']['doors'][0].__setitem__(0,9)),
          ('MONO_QUOTE',lambda d:d['scene']['ceiling'].__setitem__(14*32+10,65)),
          ('MONO_SEPARATOR',lambda d:d['scene']['solid'].__setitem__(14*32+16,0)),
          ('NAV_CAPACITY',lambda d:d['navigation'].update(nodes=[[500,500]]*194))]
        for code,edit in cases:
            with self.subTest(code=code):self.bad(edit,code)

    def test_duplicates(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'bad.json';p.write_text('{"scene":0,"scene":1}')
            with self.assertRaisesRegex(ValueError,'DUPLICATE_FIELD'):load(p)

    def test_font(self):self.assertEqual(font(),(ROOT/'src/mode8/font.bin').read_bytes())

    def test_output_guard(self):
        with self.assertRaisesRegex(ValueError,'OUTPUT_DIRECTORY'):
            build(ROOT/'examples/demo2-original.json',ROOT/'forbidden')
        self.assertFalse((ROOT/'forbidden').exists())

    def test_cli_validate(self):
        base=[sys.executable,'-B',str(ROOT/'build.py'),'--scene',str(ROOT/'examples/demo2-original.json'),'--validate-only']
        self.assertEqual(subprocess.run(base,capture_output=True).returncode,0)
        self.assertNotEqual(subprocess.run(base+['--GraphicsMode','6'],capture_output=True).returncode,0)

    def test_four_reproducible_builds(self):
        refs=load(ROOT/'tests/contracts.json')['native']
        for scene in ('demo2-original','demo2-optimized'):
            for run in ('auto','interactive'):
                with self.subTest(scene=scene,run=run),tempfile.TemporaryDirectory(prefix='vibe-native-') as t:
                    a=build(ROOT/f'examples/{scene}.json',Path(t)/'a',run)
                    b=build(ROOT/f'examples/{scene}.json',Path(t)/'b',run)
                    self.assertEqual(a['prgSHA256'],b['prgSHA256'])
                    self.assertEqual(a['prgSHA256'],refs[f'{scene}-{run}'])

    def test_manifest(self):
        manifest=ROOT/'MANIFEST.sha256'
        if not manifest.exists():self.skipTest('Run after release packaging')
        expected={}
        for line in manifest.read_text().splitlines():
            h,p=line.split('  ',1);expected[p]=h
        actual={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest().upper()
                for p in ROOT.rglob('*') if p.is_file() and p.name!='MANIFEST.sha256'}
        self.assertEqual(expected,actual)


if __name__=='__main__':unittest.main(verbosity=2)
