"""Exercise the narrow protocol upgrade and reject retries/changed programs."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from unittest.mock import patch
from pcg.migration import core,physics,holdout_guard as guard,legacy_full_v2_upgrade_v1 as upgrade
from .continue_revision063_v1 import AUTH,OUT,rows,label
from .finalize_revision063_v1 import folder_for
def main():
 record_path=AUTH/'six-legacy-full-v2-upgrade.json';ref=physics.artifact(record_path);record=core.read(record_path);state=guard._state();checks=[]
 candidates=[r for r in rows() if label(r).startswith(('lt-','lb-'))]
 for r in candidates:
  upgrade.validate(folder_for(r),ref,state,guard);checks.append(dict(test='authorized_unchanged_passing_legacy_'+label(r),passed=True))
 r=candidates[0];f=folder_for(r);scratch=OUT/'verification/upgrade-guard-negative-inputs';scratch.mkdir(parents=True,exist_ok=True)
 def rejected(name,value,test_state=state):
  p=scratch/(name+'.json');core.write(p,value)
  try:upgrade.validate(f,physics.artifact(p),test_state,guard)
  except (ValueError,AssertionError) as e:checks.append(dict(test=name,passed=True,rejection=str(e)));return
  raise AssertionError('upgrade_guard_accepted:'+name)
 v=copy.deepcopy(record);v['seedsAllocated']=True;rejected('preallocated_seed_forbidden',v)
 v=copy.deepcopy(record);v['rows'][0]['documentSha256']='0'*64;rejected('changed_frozen_document_forbidden',v)
 v=copy.deepcopy(record);v['rows'][0]['reviewId']='idea-unrelated';rejected('unrelated_module_forbidden',v)
 v=copy.deepcopy(record);old=core.read(core.resolve_artifact(v['rows'][0]['legacyCases']['path']));old['cases'][0]['control_plan'][0]['op']='wait';p=scratch/'changed-program-cases.json';core.write(p,old);v['rows'][0]['legacyCases']=physics.artifact(p);rejected('changed_program_cannot_use_protocol_upgrade',v)
 v=copy.deepcopy(record);report=core.read(core.resolve_artifact(v['rows'][0]['passingSupplement']['path']));report['passed']=False;p=scratch/'failed-legacy-report.json';core.write(p,report);v['rows'][0]['passingSupplement']=physics.artifact(p);rejected('failed_legacy_cannot_get_retry',v)
 v=copy.deepcopy(state);v['independentPools'].append(dict(source=guard._identity(f),id='already-allocated'));rejected('second_allocation_forbidden',record,v)
 # The ordinary registration path must still reject an unchanged program.
 with patch.object(guard,'refresh',return_value=state):
  try:guard.register_pool(f,'r063-negative-unchanged-default')
  except ValueError as e:
   assert str(e)=='unchanged_physics_program_or_observer_only_change_requires_raw_reanalysis_not_new_seed';checks.append(dict(test='default_unchanged_program_still_rejected',passed=True))
  else:raise AssertionError('ordinary_guard_weakened')
 core.write(OUT/'verification/upgrade-guard-check.json',dict(passed=True,checks=checks,newPhysicsAttempts=0,poolsAllocatedByChecks=0));print('UPGRADE_GUARD',len(checks),'PASS')
if __name__=='__main__':main()
