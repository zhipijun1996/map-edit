"""Add only unexecuted FULL checks, retain one original independent holdout per route."""
import copy,gzip,json,shutil,sys
from pcg.migration import core,physics
from .continue_revision058_v1 import rows,label
from .finalize_revision058_v1 import folder_for

def actual(root,e):return core.read(root/'physics'/(e['batch']+'.input.json'))['cases'][e['index']],json.loads(gzip.decompress((root/e['output']).read_bytes()))['results'][e['index']]
def run(r):
 n=label(r);f=folder_for(r);root=core.REPO/f'pcg/results/approved-r058-{n}-qualified-final-v1';original=root/'migration-physics.json';old=core.read(original);assert not old.get('holdoutPool');assert all(v['passed']for v in old['routes'])
 physics.verify_report(f,physics.artifact(original),deep=True)
 eng,cs,authors=physics._engine(f,f'approved-r058-{n}-full-completion-v2',physics.FULL_PROTOCOL);doc=core.read(f/'module.mapnote.json');baselines={}
 for route in old['routes']:
  cal=core.read(core.resolve_artifact(route['calibration']['path']));w=next(v for v in cal['rows']if v['level']=='clean'and v['purpose']['ok']);_,raw=actual(root,w['evidence']);baselines[route['routeId']]=raw
 probes=[]
 for c,raw,e in eng.run([physics.continuous_entry(c,doc)for c in cs],'full-v2-continuous-entry'):probes.append(dict(id=c['id'],probe=c['migration_probe'],check=physics.crossing(c,raw),evidence=e))
 counters=physics._run_counters(eng,cs,authors,'full-v2-counters',baselines)
 assert eng.sim.cases<=32
 for p in (eng.out/'physics').iterdir():
  dest=root/'physics'/p.name;assert not dest.exists();shutil.copy2(p,dest)
 oldprobes=core.read(core.resolve_artifact(old['probes']['path']));reobserved=[]
 for v in oldprobes:
  c,raw=actual(root,v['evidence']);w=copy.deepcopy(v);w['check']=physics.crossing(c,raw);reobserved.append(w)
 core.write(root/'full-completion-checks.json',dict(originalProbesReobserved=reobserved,newContinuousEntries=probes));core.write(root/'boundary-probes-completed.json',reobserved+probes);core.write(root/'counterexamples-completed.json',counters);core.write(root/'batches-completed.json',core.read(core.resolve_artifact(old['batches']['path']))+eng.batches);core.write(root/'protocol-completed.json',core.read(physics.FULL_PROTOCOL))
 result=copy.deepcopy(old);result.update(passed=all(v['check']['passed']for v in reobserved+probes)and not any(v['adjudication']['invalidates_design']for v in counters),actualAttempts=old['actualAttempts']+eng.sim.cases,batches=physics.artifact(root/'batches-completed.json'),probes=physics.artifact(root/'boundary-probes-completed.json'),counterexamples=physics.artifact(root/'counterexamples-completed.json'),protocol=physics.artifact(root/'protocol-completed.json'),protocolCompletion=dict(schema='pcg/review-protocol-completion/v1',sourceReport=physics.artifact(original),newPhysicsAttempts=eng.sim.cases,newIndependentHoldout=False,supplementBinding=physics.artifact(eng.out/'source_binding.json'),supplementBatches=physics.artifact(eng.out/'batches.json'),supplementChecks=physics.artifact(root/'full-completion-checks.json'),observer=physics.artifact(core.REPO/'pcg/migration/revision058_top_observer_v1.py')))
 dest=root/'migration-physics-completed.json';core.write(dest,result);proof=physics.artifact(dest)
 if result['passed']:physics.verify_report(f,proof,deep=True)
 core.write(f/'qualification-completed.json',dict(passed=result['passed'],report=proof,actualAttempts=result['actualAttempts'],newIndependentHoldout=False));print(n,'FULL_COMPLETED',result['passed'],eng.sim.cases,flush=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:run(r)
