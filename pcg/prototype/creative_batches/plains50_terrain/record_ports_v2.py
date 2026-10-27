"""Explicit run selection for further root-owned verified branch samples."""
import argparse,json
from pathlib import Path
from pcg.prototype.creative_batches.plains50_terrain.record_ports_v1 import record_one,REPO
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import file_sha
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--index',required=True);p.add_argument('--cases',nargs='+');a=p.parse_args()
 source=ROOT/'results'/a.run/'review_cases.json';cs=json.loads(source.read_text())['cases'];ids=a.cases or[c['id']for c in cs];out=REPO/'generation/workshop/plains50-ports-v1/videos'/(a.index+'-recording-index-v1.json')
 if out.exists():raise ValueError('immutable_index_exists')
 for cid in ids:
  if(REPO/'generation/workshop/plains50-ports-v1/videos'/cid).exists():raise ValueError('immutable_movie_exists/'+cid)
 rows=[]
 for cid in ids:
  row=record_one(a.run,cid);rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
 out.write_text(json.dumps(dict(schema='pcg/ports-native-review-index/v1',recording_wrappers=[dict(path=str(p.relative_to(REPO)),sha256=file_sha(p))for p in [Path(__file__),Path(__file__).with_name('record_ports_v1.py')]],source_cases=dict(path=str(source.relative_to(REPO)),sha256=file_sha(source)),clips=rows,production_admitted=False,human_video_observation='unreviewed'),ensure_ascii=False,indent=2)+'\n')
