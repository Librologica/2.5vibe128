"""Native C128 raster-fast measurements, emulated phi1 time."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,re,statistics,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))

from run_vice import run,PHASES
from check_capture import check
def analyze(b,out,standard,seconds=20):
    labels={x.split()[2][1:]:int(x.split()[1],16) for x in (b/'native/engine.labels').read_text().splitlines()}
    inv={labels[n]:n for n in PHASES};events=[];switches=[];raster=None;publications=[]
    for line in (out/'trace.log').read_text(errors='replace').splitlines():
        m=re.search(r'\)\s+(\d+)/\$[0-9a-f]+,\s+(\d+)/\$',line)
        if m:raster=[int(m[1]),int(m[2])]
        m=re.search(r'\.C:([0-9a-f]{4}).*A:([0-9A-Fa-f]{2}).*\s(\d+)\s*$',line)
        if not m:continue
        pc=int(m[1],16)
        if pc==labels['fps_frame_done']:publications.append(int(m[3]))
        if pc not in inv:continue
        n=inv[pc];t=int(m[3]);a=int(m[2],16)
        if n in PHASES[3:]:switches.append(dict(name=n,time=t,raster=raster,value=a))
        else:
            e=(n,t)
            if not events or events[-1]!=e:events.append(e)
    hz=985248 if standard=='pal' else 1022727
    first=next(t for n,t in events if n=='render_frame_begin');lo=first+2*hz;hi=lo+seconds*hz
    assert events[-1][1]>=hi,'Benchmark window incomplete'
    frames=[];cur={}
    for n,t in events:
        if n=='render_frame_begin':cur={}
        cur[n]=t
        if n=='presentation_done' and len(cur)==3:frames.append(cur.copy())
    used=[f for f in frames if lo<=f['render_frame_begin'] and f['presentation_done']<hi]
    def st(v):
        a=sorted(v);return dict(mean=statistics.mean(a),median=statistics.median(a),p95=a[int(.95*(len(a)-1))],worst=max(a),n=len(a))
    presented=[f['presentation_done'] for f in frames]
    stats=st([b-a for a,b in zip(presented,presented[1:]) if lo<=a and b<hi])
    cfg=json.loads((b/'build.json').read_text())
    for s in switches:
        if s['name']=='slow_store':assert s['value']==0 and s['raster'][0]==46,s
        if s['name']=='fast_store':assert s['value']==int(cfg['speed']=='raster') and s['raster'][0]==cfg['cpuFastIRQLine'],s
        # Trace is at STA entry, not the register write (+3 clocks). Preserve
        # final text glyph fetch through cycle55 and set D011 (+9) before
        # next-line badline BA at cycle12. PAL=63/NTSC=65 clocks per line.
        if s['name']=='body_mode_store':
            clocks=63 if standard=='pal' else 65
            assert s['raster'][0]==74 and s['raster'][1]+3>=55 and s['raster'][1]+9<clocks+12,s
    prev={b['render_frame_begin']:a['presentation_done'] for a,b in zip(frames,frames[1:])}
    costs=dict(renderIncludingIRQ=st([f['render_frame_end']-f['render_frame_begin'] for f in used]),
               presentationWait=st([f['presentation_done']-f['render_frame_end'] for f in used]),
               simulationAndLoop=st([f['render_frame_begin']-prev[f['render_frame_begin']] for f in used if f['render_frame_begin'] in prev]))
    result=dict(build=b.name,standard=standard,family=cfg['family'],run=cfg['run'],speed=cfg['speed'],phi1Hz=hz,
        warmupSeconds=2,windowSeconds=seconds,fps=sum(lo<=t<hi for t in presented)/seconds,
        framesPresented=sum(lo<=t<hi for t in presented),intervalPhi1=stats,phasePhi1=costs,
        rasterSwitchChecks=len(switches),clock='emulated phi1, not CPU instruction cycles',overlayIncluded=True)
    if publications:
        # In pipelined variants foreground completion can follow the real IRQ
        # swap by several milliseconds. Count only actual new-buffer swaps.
        result['foregroundCompletionFPS']=result['fps']
        result['fps']=sum(lo<=t<hi for t in publications)/seconds
        result['framesPresented']=sum(lo<=t<hi for t in publications)
        result['intervalPhi1']=st([b-a for a,b in zip(publications,publications[1:]) if lo<=a and b<hi])
        result['measurement']='actual IRQ new-buffer publication'
        assert len(publications) in (len(frames),len(frames)+1)
        pairs=list(zip(frames,publications))
        assert all(f['render_frame_end']<=p<=f['presentation_done'] for f,p in pairs)
        result['poseToPublicationMs']=st([(p-f['render_frame_begin'])*1000/hz for f,p in pairs if lo<=p<hi])
        result['readyToPublicationPhi1']=st([p-f['render_frame_end'] for f,p in pairs if lo<=p<hi])
        result['publicationToForegroundPhi1']=st([f['presentation_done']-p for f,p in pairs if lo<=p<hi])
        result['framePublications']=publications
    if cfg.get('kernel') in ('pipelined','combined-pipelined'):
        assert publications,'Pipelined measurement needs fps_frame_done traces'
        result['phaseNote']='presentationWait includes useful simulation; only readyToPublication is IRQ wait elapsed time'
    (out/'timing.json').write_text(json.dumps(result,indent=2)+'\n')
    (out/'frame-events.json').write_text(json.dumps(frames,indent=2)+'\n')
    (out/'raster-events.json').write_text(json.dumps(switches,indent=2)+'\n')
    print('FPS',b.name,standard,result['fps'],flush=True);return result