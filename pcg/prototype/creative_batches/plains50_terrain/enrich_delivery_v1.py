"""Attach later exact movies to completed disk-retrieval receipt; no physics."""
import json,copy
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import file_sha
REPO=ROOT.parent
if __name__=='__main__':
 folder=REPO/'generation/workshop/plains50-terrain-v1';prior=folder/'manifest.json';out=folder/'manifest-v2.json'
 if out.exists():raise ValueError('immutable_delivery_exists')
 r=json.loads(prior.read_text());r['prior_manifest']=dict(path=str(prior.relative_to(REPO)),sha256=file_sha(prior));r['video_enrichment_physics_cases']=0
 allvideos=list((folder/'videos').glob('*/manifest.json'))
 for item in r['modules']:
  assert file_sha(REPO/item['document'])==item['document_sha256']
  c=json.loads((REPO/item['case_file']).read_text());item['videos']=[];item['main_scene']='pcg/prototype/workshop/main.tscn'
  for p in allvideos:
   for v in json.loads(p.read_text())['clips']:
    if v['case_sha256']!=c['module_sha256']:continue
    movie=p.parent/v['file'];assert file_sha(movie)==v['sha256']
    item['videos'].append(dict(path=str(movie.relative_to(REPO)),sha256=v['sha256'],manifest=str(p.relative_to(REPO)),duration=v['duration'],frames_exact=v['frames_exact'],native_trace_sha256=v['native_trace_sha256'],strict_comparison='passed'))
  assert len(item['videos'])==1,item['title']
 r['video_count']=8;r['exact_native_frames']=sum(m['videos'][0]['frames_exact']for m in r['modules']);assert r['exact_native_frames']==996
 out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n');print(out)
