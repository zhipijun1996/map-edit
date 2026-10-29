"""Re-derive completed reports; separately audit explicit counter-driver provenance."""
import sys
from pcg.migration import core,physics
from pcg.migration.evidence_stream_verify_v1 import verify_report
from .continue_revision062_v1 import rows,label,OUT
from .finalize_revision062_v1 import folder_for

def counter_override(report,path):
 if not report.get('counterDriverContinuation'):return None
 x=report['counterDriverContinuation'];core.verify_artifacts(list(x.values()));binding=core.read(core.resolve_artifact(x['binding']['path']));core.verify_artifacts([binding['source']]);assert binding['inputChanges']is False and binding['newPhysicsCases']==12
 driver=core.resolve_artifact(binding['source']['path']);script=driver.read_text();assert script.startswith('extends "revision062_runner_v1.gd"');assert "not command.has('direction')"in script and "command.trigger.state='r062_pair_observe'"in script
 assert not any(k in script for k in ['motor.position=','motion_clock=','shot_charges=','restore_motion(','set_motion_running('])
 dest=path.parent;old=core.resolve_artifact(x['oldSourceBinding']['path']).parent;batches=core.read(dest/'batches.json');before=core.read(old/'batches.json');assert len(batches)==len(before)+1
 for a,b in zip(before,batches):assert a==b
 for b in before:assert core.sha(old/b['gzip_path'])==core.sha(dest/b['gzip_path'])
 name=batches[-1]['batch'];assert name=='0009-cheap-adaptation-counters';assert core.read(old/'physics'/(name+'.input.json'))==core.read(dest/'physics'/(name+'.input.json'));execution=core.read(dest/'physics'/(name+'.execution.json'));assert execution['exit_code']==0 and str(driver)in execution['command'];assert len(core.read(dest/'physics'/(name+'.input.json'))['cases'])==12
 return dict(passed=True,originalCompletedBatches=len(before),sameCounterInputs=12,originalFailedCounterCases=12,newIndependentHoldout=False,driver=physics.artifact(driver),actualCommand=physics.artifact(dest/'physics'/(name+'.execution.json')),oldFailedRawRetained=True)
def main():
 for r in rows():
  n=label(r)
  if n not in sys.argv[1:]:continue
  f=folder_for(r);q=core.read(f/'qualification.json');assert q['passed'];report=core.read(core.resolve_artifact(q['report']['path']));override=counter_override(report,core.resolve_artifact(q['report']['path']));verified=verify_report(f,q['report']);core.write(OUT/('verification/rederived-'+n+'.json'),dict(passed=True,name=n,report=q['report'],actualAttempts=verified['actualAttempts'],counterDriverOverride=override,source=physics.artifact(__file__),physicsRerun=False));print(n,'FULL_REPORT_RAW_REDERIVED',flush=True)
if __name__=='__main__':main()
