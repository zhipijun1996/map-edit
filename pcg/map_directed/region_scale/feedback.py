"""One bounded physical-space feedback step using existing Director ports.

No second embedding algorithm and no terrain repair. An observed failed Map and
its source-owned dynamic envelopes cause the existing joint column search to
resolve a fresh contact contract. Infeasible contracts stay rejected.
"""
import argparse,json
from pathlib import Path
from ..director import REPO
from ..run import write
from ..direct_join.director import requests
from pcg.prototype.factory.core.engine import file_sha

def run(source,failed_run,name):
 source=Path(source).resolve();failed_run=Path(failed_run).resolve();out=REPO/'pcg/results'/name
 if out.exists():raise ValueError('immutable_region_feedback_exists')
 out.mkdir(parents=True);c=json.loads((source/'compiled.json').read_text());summary=json.loads((failed_run/'summary.json').read_text())
 if not any(not r['ok']for r in summary['rows']):raise ValueError('no_observed_failure_for_feedback')
 conflicts=[]
 for m in c['modules']:
  for p in m['ports'].values():
   if p['kind']!='vertical' or p['normal'][1]<=0:continue
   for col in m.get('columns',[]):
    if abs(p['column_x']-col['x'])<192:
     conflicts.append(dict(node_id=m['id'],bottom_port=p['id'],carrier=col['id'],column_distance=abs(p['column_x']-col['x']),required_design_distance=192,
      basis='Source-owned lift and lower ingress share a narrow column; actual full-world failures are retained independently',physical_clearance_guaranteed=False))
 if not conflicts:raise ValueError('failure_not_explained_by_supported_space_feedback_rule')
 layout=json.loads((source/'layout.json').read_text());layout['physical_port_clearance']=True;write(out/'layout.json',layout)
 receipt=dict(schema='map-notes/challenge-space-feedback/v1',maximum_local_attempts=1,actual_local_attempts=1,conflicts=conflicts,
  source_files={str(p.relative_to(REPO)):file_sha(p)for p in [source/'compiled.json',failed_run/'summary.json',failed_run/'physics/batches.json',Path(__file__)]},
  map_added_terrain=0,graph_changed=False,physical_verification='REQUIRED_AFTER_REGENERATION')
 try:
  graph,specs,seams=requests(out/'layout.json')
  write(out/'resolved-contact-specifications.json',specs);write(out/'resolved-seams.json',seams)
  receipt.update(status='spatial_contract_resolved',module_demands=len(specs),physical_success=False)
 except ValueError as error:
  receipt.update(status='space_unsatisfied',reason=str(error),physical_success=False)
 write(out/'feedback.json',receipt);return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--failed-run',required=True);p.add_argument('--name',required=True);a=p.parse_args();print(run(a.source,a.failed_run,a.name))
