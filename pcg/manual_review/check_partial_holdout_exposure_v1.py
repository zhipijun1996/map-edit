"""Regression using real archived prior raw; no new physics or seed allocation."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,json,subprocess,tempfile,shutil
from unittest.mock import patch
from pcg.migration import core,physics,holdout_guard as guard
from pcg.migration.partial_holdout_exposure_v1 import ingest_run
from .continue_revision062_v1 import OUT

def main():
 baseline=json.loads(subprocess.check_output(['git','show','73ea016236f6e4bb36e38fd76e07e8163bb921dd:pcg/migration/foundation-v1/holdout-locks-v1.json']));state=copy.deepcopy(baseline);root=core.REPO/'pcg/results/approved-r060-hq07-qualified-final-v1';f=core.REPO/'pcg/manual_review/implementation/revision-062-final-v1/idea-plains-hq07-001';identity=guard._identity(f);assert not any(o['source']['key']==identity['key']for o in state['observations']);added=ingest_run(state,root,guard);assert added>0;assert any(o['routeId']=='R-to-L'for o in state['observations']if o['source']['key']==identity['key']);n=len(state['observations']);assert ingest_run(state,root,guard)==0 and len(state['observations'])==n
 with patch.object(guard,'_state',return_value=state):
  try:guard.check(f,protocol_path=physics.FULL_PROTOCOL,refresh_locks=False)
  except guard.HoldoutConflict as e:assert 'holdout_conditions_already_observed_for_original_source'in e.details['conflicts'];blocked=e.details
  else:raise AssertionError('partial_holdout_did_not_block_known_pool')
 with tempfile.TemporaryDirectory(prefix='guard-input-only-',dir=core.REPO/'pcg/results')as tmp:
  folder=__import__('pathlib').Path(tmp);(folder/'physics').mkdir()
  for name in ['input-binding.json','protocol.json']:shutil.copyfile(root/name,folder/name)
  b=next(b for b in core.read(root/'batches.json')if b['stage']=='migration-holdout');input_path=root/'physics'/(b['batch']+'.input.json');shutil.copyfile(input_path,folder/'physics'/input_path.name);core.write(folder/'batches.json',[]);isolated=copy.deepcopy(baseline);assert ingest_run(isolated,folder,guard)==1;assert isolated['observations'][-1]['qualityStatus']=='UNKNOWN_INPUT_EXPOSURE_IS_NOT_VALIDATION';assert ingest_run(isolated,folder,guard)==0
  core.write(folder/'physics'/(b['batch']+'.log'),'metadata-only isolated test: later log append');assert ingest_run(isolated,folder,guard)==0
 untouched=copy.deepcopy(baseline);assert ingest_run(untouched,core.REPO/'pcg/results/approved-r062-hq03-qualified-final-v1',guard)==0
 core.write(OUT/'verification/partial-holdout-lock-regression.json',dict(passed=True,scope='Read-only actual prior raw + isolated copied lock state; zero new physics/seeds',newObservedBatches=added,idempotent=True,inputOnlyExposureLocked=True,inputOnlyFixtureNotPhysics=True,laterOptionalLogDoesNotDropLock=True,completeReportNotDuplicated=True,oldBugReproduced='baseline source appears unobserved despite completed interrupted060 R holdout',correctedPreflightWouldBlock=blocked,helper=physics.artifact(core.REPO/'pcg/migration/partial_holdout_exposure_v1.py')));print('PARTIAL_HOLDOUT_GUARD_REGRESSION_PASS',added,flush=True)
if __name__=='__main__':main()
