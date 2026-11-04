"""Verify that the sampling fix preserves all noise and historical sampling."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,physics,revision063_group_sampling_v1 as current
from pcg.prototype.workshop import evaluate as legacy
from .continue_revision063_v1 import rows,label,OUT
from .finalize_revision063_v1 import folder_for
def main():
 row=next(r for r in rows()if label(r)=='s04');cases=core.read(folder_for(row)/'physics-input-cases.json')['cases'];checks=[]
 for index,case in enumerate(cases):
  for level in ['clean','mild','moderate']:
   for trial in range(12):
    seed=2710271401+index*1009;a=legacy.instantiate(case,seed,level,trial);b=current.instantiate(case,seed,level,trial);again=legacy.instantiate(case,seed,level,trial);assert a==again
    authored={p['platform_id']:p['initial_phase']for p in case['moving_platforms']}
    expected=copy.deepcopy(a)
    for p in expected['moving_platforms']:p['initial_phase']=authored[p['platform_id']]
    assert b==expected and b.get('noise')==a.get('noise') and b['enemies']==a['enemies']
    checks.append(dict(route=case['route_spec']['id'],level=level,trial=trial,noiseAndEnemiesUnchanged=True,legacyFunctionUnchanged=True))
 invalid=copy.deepcopy(cases[0]);invalid['approved_implementation']['reviewId']='unreviewed-module'
 try:current.instantiate(invalid,1,'clean',0)
 except ValueError:pass
 else:raise AssertionError('unreviewed_sampling_scope_accepted')
 core.write(OUT/'verification/group-sampling-check.json',dict(passed=True,checks=checks,validTrials=len(checks),unreviewedScopeRejected=True,newPhysicsCases=0,newSeedAllocated=False,source=physics.artifact(__file__),sampler=physics.artifact(current.__file__)))
 print('GROUP_SAMPLING_NOISE_AND_HISTORY',len(checks),'PASS')
if __name__=='__main__':main()
