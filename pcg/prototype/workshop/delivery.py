"""Package standard contracts, exact videos and experiment evidence for review."""
import argparse,copy,gzip,json,shutil,subprocess
from pathlib import Path
from .engine import ROOT,HERE
from .experiments import write
from ..factory.core.quality import digest,module_hash
from ..factory.core.engine import file_sha
from pcg.map_directed.library import verified_document

SELECTED=[('workshop-a1-holdout-v1',None),('workshop-five-holdout-v1',{'brake-under-ledge','one-shot-two-routes','air-refund'}),('workshop-carrier-binding-v2',None),('workshop-gate-window-v2',None)]

def prepare_review(run):
    root=ROOT/'results'/run;cases=json.loads((root/'cases.json').read_text())['cases'];by={c['id']:c for c in cases};reviews=[]
    for b in json.loads((root/'batches.json').read_text()):
        raw=gzip.decompress((root/b['gzip_path']).read_bytes())
        import hashlib
        if hashlib.sha256(raw).hexdigest()!=b['raw_output_sha256']:raise ValueError('trace drift')
        for i,r in enumerate(json.loads(raw)['results']):
            if '-mild-'in r['id']or not r['ok']:continue
            c=copy.deepcopy(by[r['id']]);c['factory_id']=digest(c);c['factory_evidence']=dict(batch=b['batch'],index=i,output=b['gzip_path'],raw_output_sha256=b['raw_output_sha256'])
            c['recorded_frames']=[dict(frame=f['frame'],axis=f['axis'],requested=f['requested'])for f in r['frames']]
            c['module_sha256']=module_hash(c);c['review_alias']=c['id'];reviews.append(c)
    path=root/'review_cases.json'
    if path.exists():raise ValueError('immutable_review_cases')
    write(path,dict(cases=reviews));return path

def build(out_name):
    out=ROOT.parent/out_name
    if out.exists():raise ValueError('immutable_delivery')
    modules=out/'modules';modules.mkdir(parents=True);entries=[];play=[];lineage=[]
    aliases=json.loads((HERE/'source-aliases.json').read_text())['aliases']
    for run,allowed in SELECTED:
        root=ROOT/'results'/run;manifest=json.loads((root/'modules/manifest.json').read_text());cases=json.loads((root/'review_cases.json').read_text())['cases']
        for item in manifest['modules']:
            if allowed and item['family']not in allowed:continue
            src=root/'modules'/item['file'];doc=verified_document(src)
            shutil.copy2(src,modules/item['file']);shutil.copy2(src.with_suffix('').with_suffix('.svg'),modules/(doc['id']+'.svg'))
            entries.append(dict(item,source_run=run,sha256=file_sha(src),svg=doc['id']+'.svg'))
        for c in cases:
            if allowed and c['family']not in allowed:continue
            play.append(c)
            lineage.append(dict(case_id=c['id'],family=c['family'],source_ids=[aliases.get(s,s)for s in c['idea_ids']],source_aliases=c['idea_ids'],physics_run=run,module_sha256=c['module_sha256']))
    write(modules/'manifest.json',dict(schema='pcg/workshop-delivery/v1',modules=entries,distinct_families=len({e['family']for e in entries}),production_admitted=False))
    write(out/'review_cases.json',dict(cases=play));write(out/'source-lineage.json',dict(schema='pcg/idea-to-content-lineage/v1',records=lineage,original_sources='pcg/prototype/workshop/ideas.json',aliases='pcg/prototype/workshop/source-aliases.json',human_idea_is_not_approval=True))
    rows=[]
    for run,_ in SELECTED:
        for e in json.loads((ROOT/'results'/run/'evaluations.json').read_text()):
            if run=='workshop-five-holdout-v1'and e['case']['family']in ['chase-landing','timed-cache']:continue
            rows.append(dict(id=e['case']['id'],family=e['case']['family'],rates={k:dict(trials=v['trials'],passed=v['purpose_valid'])for k,v in e['stats'].items()},quality=e['quality_gate'],source_run=run))
    write(out/'technical-results.json',dict(rows=rows,quality_policy='existing factory POLICY v2 regular',human_video_observation='unreviewed',human_playtest='unreviewed',production_admitted=False))
    videos=out/'videos';videos.mkdir();clips=[]
    sources=[('a1-first-delivery',None),('five-families-v1',{'brake-under-ledge','air-refund'}),('fork-high-v1',None),('carrier-binding-v2',None),('gate-window-v2',None)]
    for source,allowed in sources:
        root=ROOT.parent/'generation/workshop'/source;m=json.loads((root/'manifest.json').read_text())
        for clip in m['clips']:
            if allowed and clip['family']not in allowed:continue
            shutil.copy2(root/clip['file'],videos/clip['file']);clips.append(dict(clip,recording_manifest=str((root/'manifest.json').relative_to(ROOT.parent))))
    write(videos/'manifest.json',dict(schema='pcg/video-review/v1',clips=clips,frames_exact=sum(c['frames_exact']for c in clips),speed=1,end_hold_seconds=1,human_video_observation='unreviewed',human_playtest='unreviewed',production_admitted=False))
    concat=videos/'concat.txt';concat.write_text(''.join("file '"+c['file']+"'\n"for c in clips))
    with(videos/'concat.log').open('w')as f:subprocess.run(['ffmpeg','-nostdin','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(videos/'six-families.mp4')],stdout=f,stderr=subprocess.STDOUT,check=True)
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--prepare-review');p.add_argument('--out');a=p.parse_args()
    print(prepare_review(a.prepare_review)if a.prepare_review else build(a.out))
