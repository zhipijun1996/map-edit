"""Wire audited exposure bookkeeping after the active frozen run completes."""
from pcg.migration import core,physics
from .continue_revision062_v1 import OUT
from .finalize_revision062_v1 import folder_for
from .continue_revision062_v1 import rows,label

def main():
 r=next(r for r in rows()if label(r)=='rs12');assert(folder_for(r)/'qualification.json').exists(),'do_not_edit_sources_of_active_frozen_run';p=core.REPO/'pcg/migration/holdout_guard.py';s=p.read_text();needle="        state['counts']=dict(observedRoutes=len(state['observations']),";assert s.count(needle)==1
 if 'partial_holdout_exposure_v1'not in s:s=s.replace(needle,"        from .partial_holdout_exposure_v1 import ingest_all\n        import sys\n        ingest_all(state,sys.modules[__name__])\n"+needle);p.write_text(s)
 p=core.REPO/'pcg/migration/physics.py';s=p.read_text();needle="Path(__file__).with_name('review_counter_scope_v14.py')"
 if "Path(__file__).with_name('partial_holdout_exposure_v1.py')"not in s:assert s.count(needle)==1;s=s.replace(needle,"Path(__file__).with_name('partial_holdout_exposure_v1.py'), "+needle);p.write_text(s)
 import shutil
 frozen=OUT/'verification/source-snapshots';frozen.mkdir(exist_ok=True)
 for name in ['holdout_guard.py','partial_holdout_exposure_v1.py','physics.py']:shutil.copyfile(core.REPO/'pcg/migration'/name,frozen/name)
 core.write(OUT/'verification/partial-holdout-guard-wiring.json',dict(passed=True,scope='Exposure bookkeeping and source freezing only; no physics, seed allocation or gate thresholds changed',guard=physics.artifact(frozen/'holdout_guard.py'),helper=physics.artifact(frozen/'partial_holdout_exposure_v1.py'),runnerSourceFreeze=physics.artifact(frozen/'physics.py'),activeRunCompletedBeforeEdit=True));print('PARTIAL_HOLDOUT_GUARD_WIRED',flush=True)
if __name__=='__main__':main()
