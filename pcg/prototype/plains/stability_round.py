"""Frozen infrastructure regression, separate from level-quality denominators."""
import argparse,copy,gzip,json,hashlib
from .engine import ROOT,PlainsEngine
from ..factory.core.quality import module_hash
KEYS=['x','y','vx','vy','grounded','shot_charges','shot_cooldown','jumps_used','jump_maximum','energy','hp','traversal_state','requested','accepted','module_clock','real_velocity','normal_velocity','moving_platforms','saws','support_id','goal_stable_frames']

def run(name,production,batches=30):
 out=ROOT/'results'/name;engine=PlainsEngine(out,12);old=ROOT/'results/plains-stability-debug-v1';baseline=json.loads((old/'baseline-00.output.json').read_text())['results'];inp=ROOT/'results/plains-contract-production-v2/physics/0001-fresh-holdout.input.json';base_cases=json.loads(inp.read_text())['cases']
 run=ROOT/'results'/production;review=json.loads((run/'review_cases.json').read_text())['cases'];pool=[(c,r)for c,r in zip(base_cases,baseline)]
 for c in review:
  assert module_hash(c)==c['module_sha256'];ev=c['factory_evidence'];r=json.loads(gzip.decompress((run/ev['output']).read_bytes()))['results'][ev['index']];pool.append((c,r))
 cases=[];expected={}
 for i in range(batches*12):
  c,r=pool[i%len(pool)];c=copy.deepcopy(c);c['id']+=f'-stability-{i}';cases.append(c);expected[c['id']]=r
 (out/'protocol.json').write_text(json.dumps(dict(scope='Infrastructure and exact-trajectory regression only; not new quality trials',batches=batches,cases=len(cases),source_production=production,legacy_input_sha256=hashlib.sha256(inp.read_bytes()).hexdigest(),pool=len(pool),keys=KEYS),indent=2))
 rows=[]
 for c,r,ev in engine.run(cases,'lifecycle-regression'):
  before=expected[c['id']];assert r['ok']==before['ok']and len(r['frames'])==len(before['frames']),c['id']
  for a,b in zip(before['frames'],r['frames']):assert all(a[k]==b[k]for k in KEYS),(c['id'],a['frame'])
  assert not r['entry_snapshot']['accepted']and not r['entry_snapshot']['requested']
  rows.append(dict(id=c['id'],frames=len(r['frames']),same_motion_resources_phase_and_inputs=True,evidence=ev))
 summary=dict(scope='Finite infrastructure regression, not bulk fun proof',batches=len(engine.batches),physics_cases=engine.sim.cases,engine_errors=0,exact_matching_cases=len(rows),exact_matching_frames=sum(r['frames']for r in rows),protected_files=engine.binding['protected_files'],protected_mismatches=engine.binding['protected_mismatches'])
 (out/'rows.json').write_text(json.dumps(rows));(out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--production',required=True);p.add_argument('--batches',type=int,default=30);a=p.parse_args();run(a.name,a.production,a.batches)
