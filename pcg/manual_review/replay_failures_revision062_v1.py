"""Reproduce existing failed instantiated calibration inputs, without new seeds."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .continue_revision062_v1 import rows,label,AUTH,OUT

def main():
 facts=[]
 for row in rows():
  n=label(row);source=AUTH/'prior-calibration'/(n+'.json')
  if not source.exists():continue
  original=core.read(source);out=OUT/'fixtures'/('prior-calibration-replay-'+n+'-v1');assert not out.exists();cs=[v['input']for v in original['rows']];core.write(out/'module.mapnote.json',core.read(core.resolve_artifact(original['sourceModule']['path'])));core.write(out/'cases.json',dict(cases=cs));eng,cases,authors=physics._engine(out,'approved-r062-'+n+'-prior-calibration-replay-v1',physics.FULL_PROTOCOL);checks=[]
  for i,(c,raw,e)in enumerate(eng.run(cases,'identical-observed-calibration-replay')):
   q=checked_purpose(authors[i],c,raw);checks.append(dict(route=c['route_spec']['id'],originalCheck=original['rows'][i]['failedCheck'],rerun=q,inputUnchanged=c==original['rows'][i]['input'],evidence=e,firstInput=raw.get('fired_commands',[])[:2],lastInputs=raw.get('fired_commands',[])[-4:],nativeOutcome=raw.get('reason')))
  core.write(out/'report.json',dict(rows=checks,identicalInputs=True,newIndependentHoldout=False,originalFailuresRetained=True,originalSource=physics.artifact(source),geometryChanged=False));facts.append(dict(name=n,replayedCases=len(checks),stillFailed=sum(not v['rerun']['ok']for v in checks),report=physics.artifact(out/'report.json')));print(n,'SAME_CONDITION_REPLAY',facts[-1]['stillFailed'],len(checks),flush=True)
 core.write(OUT/'verification/prior-failure-replay.json',dict(rows=facts,noLuckyReroll=True,classification='Repeat confirms measured driver failures; native control repair required. Does not prove impossible geometry.'))
if __name__=='__main__':main()
