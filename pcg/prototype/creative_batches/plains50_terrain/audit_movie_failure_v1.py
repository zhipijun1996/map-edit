"""Enumerate original strict comparison differences without changing its gate."""
import argparse,gzip,json
from pathlib import Path
from collections import Counter
from pcg.prototype.workshop.record import KEYS
from pcg.tools.record_plains import event_key
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import file_sha
REPO=ROOT.parent
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,required=True);a=p.parse_args();directory=a.directory;failure=json.loads((directory/'strict-failure.json').read_text());case=json.loads((directory/'review_cases.json').read_text())['cases'][0];run=REPO/failure['source_run'];ev=case['factory_evidence'];batch=next(b for b in json.loads((run/'batches.json').read_text())if b['batch']==ev['batch']);packed=run/batch['gzip_path'];source=json.loads(gzip.decompress(packed.read_bytes()))['results'][ev['index']];native_path=REPO/failure['native_trace'];native=json.loads(native_path.read_text());assert source['id']==case['id']==native['case_id'];assert native['module_sha256']==case['module_sha256'];differences=[]
 for x,y in zip(native['frames'],source['frames']):
  for key in KEYS:
   if x[key]!=y[key]:differences.append(dict(frame=x['frame'],field=key,native=x[key],validated=y[key]))
  for key,left,right in [('plains.events',[event_key(e)for e in x['plains']['events']],[event_key(e)for e in y['plains']['events']]),('plains.bells',x['plains']['bells'],y['plains']['bells']),('plains.enemies',x['plains']['enemies'],y['plains']['enemies']),('workshop',x['workshop'],y['workshop'])]:
   if left!=right:differences.append(dict(frame=x['frame'],field=key,native=left,validated=right))
 report=dict(schema='pcg/native-strict-differences/v1',case_id=case['id'],source_run=failure['source_run'],source_case_sha256=case['module_sha256'],native_trace_sha256=file_sha(native_path),raw_physics_output_sha256=batch['raw_output_sha256'],native_frames=len(native['frames']),validated_frames=len(source['frames']),strict_pass=False,review_only=True,differing_fields=dict(Counter(d['field']for d in differences)),differing_frames=len({d['frame']for d in differences}),differences=differences,original_gate_unchanged=True)
 out=directory/'strict-differences-v1.json'
 if out.exists():raise ValueError('immutable_audit_exists')
 out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='differences'}))
