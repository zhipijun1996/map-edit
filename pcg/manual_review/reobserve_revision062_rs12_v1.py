if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,gzip,json
from pcg.migration import core,physics
from pcg.migration.revision062_top_observer_v1 import observe
from .continue_revision062_v1 import OUT

def main():
 root=core.REPO/'pcg/results/approved-r062-rs12-qualified-final-v1-same-input-resume-v1';folder=core.REPO/'pcg/manual_review/implementation/revision-062-final-v1/idea-spec02-s12-001';source=root/'migration-physics.json';old=core.read(source);probes=core.read(root/'boundary-probes.json');checks=[];changed=[];cache={};guardtests=[]
 for row in probes:
  if row['check']['passed']:checks.append(row);continue
  e=row['evidence'];name=e['batch']
  if name not in cache:
   inputs=core.read(root/'physics'/(name+'.input.json'))['cases']
   with gzip.open(root/e['output'],'rt')as f:rs=json.load(f)['results']
   cache={name:(inputs,rs)}
  c,raw=cache[name][0][e['index']],cache[name][1][e['index']];new=copy.deepcopy(row);new['check']=physics.crossing(c,raw);assert new['check']['passed'],new;checks.append(new);changed.append(dict(id=row['id'],before=row['check'],after=new['check'],rawSha256=e['raw_output_sha256']))
  if not guardtests:
   for kind in ['no_support','outside_original_safe_margin','not_grounded','moving','harm','reset']:
    bad=copy.copy(raw);bad['frames']=[dict(f)for f in raw['frames']]
    if kind=='harm':bad['hp']=4
    elif kind=='reset':bad['returns']=[{'synthetic_guard_only':True}]
    else:
     for f in bad['frames']:
      if kind=='no_support':f['support_id']=''
      elif kind=='outside_original_safe_margin':f['y']=-50.1
      elif kind=='not_grounded':f['grounded']=False
      elif kind=='moving':f['real_velocity']=[2.,0.]
    assert observe(c,bad)is None,kind;guardtests.append(dict(kind=kind,rejected=True,scope='Synthetic observer negative guard only, not physics evidence'))
 assert len(changed)==6;analysis=OUT/'fixtures/rs12-native-neighbor-observation-v1/analysis.json';core.write(analysis,dict(passed=True,source=physics.artifact(__file__),changed=changed,guardTests=guardtests,newPhysicsAttempts=0,newIndependentHoldout=False,originalRawAndReportsUnchanged=True));probes_path=root/'boundary-probes-reobserved-v1.json';assert not probes_path.exists();core.write(probes_path,checks);new=copy.deepcopy(old);new['passed']=all(r['passed']for r in old['routes'])and all(r['check']['passed']for r in checks)and not any(r['adjudication']['invalidates_design']for r in core.read(root/'counterexamples.json'));assert new['passed'];new['probes']=physics.artifact(probes_path);new['boundaryObservationCorrection']=dict(schema='pcg/revision062-native-neighbor-observation-correction/v1',sourceReport=physics.artifact(source),sourceProbes=physics.artifact(root/'boundary-probes.json'),observer=physics.artifact(core.REPO/'pcg/migration/revision062_top_observer_v1.py'),originalObserver=physics.artifact(core.REPO/'pcg/migration/revision061_top_observer_v1.py'),nativePropertyProbe=physics.artifact(OUT/'fixtures/original-motor-margin-v1/report.json'),analysis=physics.artifact(analysis),newPhysicsAttempts=0,newIndependentHoldout=False);target=root/'migration-physics-reobserved-v1.json';assert not target.exists();core.write(target,new);q=core.read(folder/'qualification.json');core.write(folder/'qualification-initial-boundary-failed-v1.json',q);q.update(passed=True,report=physics.artifact(target),originalBoundaryFailure=physics.artifact(source),readOnlyBoundaryObservation=physics.artifact(analysis));core.write(folder/'qualification.json',q);print('RS12_READONLY_NATIVE_CONTACT_REOBSERVED',len(changed),'QUALIFIED_TRUE',old['actualAttempts'],flush=True)
if __name__=='__main__':main()
