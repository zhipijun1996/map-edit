import json,gzip
from pathlib import Path
from . import rules_v2 as rules,alternatives_v1 as counters,counter_policy_v1 as policy,fixtures_v1 as fixtures
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome
HERE=Path(__file__).parent
def main():
 bases=[rules.candidate('B',1),rules.candidate('C',0)];cs=[v for c in bases for v in counters.preliminary(c)]+[fixtures.floor_retry(bases[1])]
 bfile=next((ROOT/'results/workshop-batch30-blockn17-core-v2/physics').glob('*.output.json.gz'));baseline={r['id']:r for r in json.load(gzip.open(bfile,'rt'))['results']}
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn17-more-v1',extra_sources=[Path(__file__),Path(counters.__file__),Path(policy.__file__),Path(fixtures.__file__),HERE/'fixture-protocol-v1.json',HERE/'counter-policy-v1.json',*policy.SOURCE_DEPENDENCIES,*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,'extra-counters-and-one-specific-floor-retry'):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev)
  if c.get('counterexample_kind'):row['classification']=policy.classify(c,r,q,external_outcome(c,r),baseline[c['id'].split('-counter-')[0]])
  else:
   supports=[];last=''
   for f in r['frames']:
    name=f.get('support_id','')
    if f.get('grounded')and name!=last:supports.append({k:f.get(k)for k in ['frame','x','y','support_id','shot_charges','jumps_used','energy','shot_cooldown']});last=name
   row['actual_ground_resource_stages']=supports;row['fixture_only_not_generic_recovery']=True
  rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0,new_families=0))
if __name__=='__main__':main()
