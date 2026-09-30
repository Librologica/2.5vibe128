"""Public deterministic world, input-domain and native build contracts."""
import hashlib,json,sys,tempfile,unittest
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'src/infinite')]
import world
from build_infinite import build

class InfiniteContracts(unittest.TestCase):
    def test_world_deterministic_and_wrapped(self):
        for seed in (0,0x12345678,0xffffffff):
            for x,y in ((0,0),(0xfffffff9,0xfffffffb),(1024,1987)):
                a=world.world(x,y,seed)
                self.assertEqual(a,world.world(x,y,seed))
                self.assertEqual(a,world.world(x+(1<<32),y,seed))
                self.assertEqual(len(a),1600)
                self.assertLessEqual(set(a),{0,1,9})
                self.assertEqual(a[:40],bytes([1])*40)
                self.assertEqual(a[-40:],bytes([1])*40)
                self.assertTrue(all(a[r*40]==a[r*40+39]==1 for r in range(40)))

    def test_streaming_overlap(self):
        for seed in (0,0x12345678,0xffffffff):
            a=world.world(0xfffffff0,0xfffffff4,seed)
            b=world.world(0xfffffff1,0xfffffff4,seed)
            c=world.world(0xfffffff0,0xfffffff5,seed)
            for y in range(1,38):
                for x in range(1,38):
                    self.assertEqual(a[y*40+x+1],b[y*40+x])
                    self.assertEqual(a[(y+1)*40+x],c[y*40+x])

    def test_build_validation(self):
        with self.assertRaisesRegex(ValueError,'OUTPUT_DIRECTORY'):build(ROOT/'forbidden')
        self.assertFalse((ROOT/'forbidden').exists())
        with tempfile.TemporaryDirectory() as t:
            for seed in (-1,1<<32,True,1.5):
                with self.subTest(seed=seed),self.assertRaisesRegex(ValueError,'SEED'):build(Path(t)/'bad',seed=seed)
            with self.assertRaisesRegex(ValueError,'RUN'):build(Path(t)/'bad',run='walk')
            self.assertFalse((Path(t)/'bad').exists())

    def test_reproducible_native_demos(self):
        expected=json.loads((ROOT/'tests/contracts.json').read_text())['infinite']
        for run in ('auto','interactive'):
            with tempfile.TemporaryDirectory(prefix='vibe-infinite-') as t:
                a=build(Path(t)/'a',run);b=build(Path(t)/'b',run)
                self.assertEqual(a['prgSHA256'],b['prgSHA256'])
                self.assertEqual(a['prgSHA256'],expected[run])
                self.assertFalse(a['audio'])
                self.assertEqual(a['viewport'],[128,144])
                self.assertEqual(a['mapBytes'],1600)
                self.assertGreater(a['nativeFree'],1000)
                self.assertEqual(a['visibleDistanceCells'],18)
        with tempfile.TemporaryDirectory(prefix='vibe-fixed-') as t:
            a=build(Path(t)/'fixed','auto',0x12345678)
            self.assertEqual(a['prgSHA256'],expected['fixedSeedAuto'])

    def test_silent_sources(self):
        import re
        for p in (ROOT/'src').rglob('*.asm'):
            s=p.read_text(encoding='utf-8')
            self.assertIsNone(re.search(r'(?im)^\s*(jsr|jmp)\s+sid_(init|play)',s),str(p))
        self.assertFalse(list(ROOT.rglob('*.sid')))
        self.assertFalse(list(ROOT.rglob('*.mp3')))

if __name__=='__main__':unittest.main(verbosity=2)
