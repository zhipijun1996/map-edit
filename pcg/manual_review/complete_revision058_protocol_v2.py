"""Supplement legacy v1 coverage; never rewrite its seeds or claim FULL_v2 admission."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,gzip,json,shutil,sys
from pcg.migration import core,physics
from .continue_revision058_v1 import rows,label
from .finalize_revision058_v1 import folder_for
from .complete_revision058_protocol_v1 import actual

def write_once(path,value):
 if path.exists():assert core.read(path)==value
 else:core.write(path,value)

def run(r):
 n=label(r);f=folder_for(r);root=core.REPO/f'pcg/results/approved-r058-{n}-qualified-final-v1';original=root/'migration-physics.json';old=core.read(original);assert not old.get('holdoutPool');assert all(v['passed']for v in old['routes'])
 physics.verify_report(f,physics.artifact(original),deep=True)
 engroot=core.REPO/f'pcg/results/approved-r058-{n}-full-completion-v2'
 if(engroot/'batches.json').exists():
  extra=core.read(engroot/'batches.json');checks=core.read(root/'full-completion-checks.json');probes=checks['newContinuousEntries'];counters=core.read(root/'counterexamples-completed.json')
 else:
  eng,cs,authors=physics._engine(f,f'approved-r058-{n}-coverage-supplement-v1',physics.FULL_PROTOCOL);engroot=eng.out;doc=core.read(f/'module.mapnote.json');baselines={}
  for route in old['routes']:
   cal=core.read(core.resolve_artifact(route['calibration']['path']));w=next(v for v in cal['rows']if v['level']=='clean'and v['purpose']['ok']);_,raw=actual(root,w['evidence']);baselines[route['routeId']]=raw
  probes=[]
  for c,raw,e in eng.run([physics.continuous_entry(c,doc)for c in cs],'coverage-continuous-entry'):probes.append(dict(id=c['id'],probe=c['migration_probe'],check=physics.crossing(c,raw),evidence=e))
  counters=physics._run_counters(eng,cs,authors,'coverage-counters',baselines);extra=eng.batches
 assert sum(b['cases']for b in extra)<=32
 for p in (engroot/'physics').iterdir():
  dest=root/'physics'/p.name
  if dest.exists():assert core.sha(dest)==core.sha(p)
  else:shutil.copy2(p,dest)
 before=core.read(core.resolve_artifact(old['probes']['path']));observed=[]
 for v in before:
  c,raw=actual(root,v['evidence']);w=copy.deepcopy(v);w['check']=physics.crossing(c,raw);observed.append(w)
 write_once(root/'coverage-checks-v2.json',dict(originalProbesReobserved=observed,newContinuousEntries=probes));write_once(root/'boundary-probes-supplemented-v2.json',observed+probes);write_once(root/'counterexamples-supplemented-v2.json',counters);write_once(root/'batches-supplemented-v2.json',core.read(core.resolve_artifact(old['batches']['path']))+extra)
 result=copy.deepcopy(old);result.update(passed=all(v['check']['passed']for v in observed+probes)and not any(v['adjudication']['invalidates_design']for v in counters),actualAttempts=old['actualAttempts']+sum(b['cases']for b in extra),batches=physics.artifact(root/'batches-supplemented-v2.json'),probes=physics.artifact(root/'boundary-probes-supplemented-v2.json'),counterexamples=physics.artifact(root/'counterexamples-supplemented-v2.json'),protocolCompletion=dict(schema='pcg/review-protocol-completion/v2',sourceReport=physics.artifact(original),newPhysicsAttempts=sum(b['cases']for b in extra),newIndependentHoldout=False,fullV2Qualification=False,requestedProtocol=physics.artifact(physics.FULL_PROTOCOL),scope='Legacy_v1 independent seeds retained. Full seam/counter coverage supplemented; original preregistered FULL_v2 seed experiment remains UNKNOWN.',supplementBinding=physics.artifact(engroot/'source_binding.json'),supplementBatches=physics.artifact(engroot/'batches.json'),supplementChecks=physics.artifact(root/'coverage-checks-v2.json'),observer=physics.artifact(core.REPO/'pcg/migration/revision058_top_observer_v1.py')))
 dest=root/'migration-physics-supplemented-v2.json';write_once(dest,result);proof=physics.artifact(dest)
 if result['passed']:physics.verify_report(f,proof,deep=True)
 core.write(f/'qualification-supplemented.json',dict(passed=result['passed'],fullV2Qualification=False,protocol='legacy_v1_with_full_coverage_supplement',report=proof,actualAttempts=result['actualAttempts'],newIndependentHoldout=False));print(n,'LEGACY_V1_SUPPLEMENTED',result['passed'],sum(b['cases']for b in extra),flush=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:run(r)
