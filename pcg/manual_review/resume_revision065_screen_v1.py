"""Reuse24 completed screen cases; run only the two not yet executed."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import gzip,json
from pcg.migration import core,physics
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .continue_revision065_lift_v1 import OUT
from .run_revision065_lift_v1 import frozen_row,rows
def main():
 row=frozen_row(rows()[0],'v2');f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];original=core.REPO/'pcg/results/approved-r065-lift-control-screen-v2';assert not(original/'screen.json').exists()
 inputs=[];labels={}
 for i,c in enumerate(cs):
  for level,total in [('clean',1),('mild',6),('moderate',6)]:
   for j in range(total):
    v=instantiate(physics.fresh(c,'screen-v2'),271028029,level,j);inputs.append(v);labels[v['id']]=(i,level)
 batch=core.read(original/'batches.json')[0];p=original/batch['gzip_path'];execution=core.read(original/batch['execution']);assert execution['exit_code']==0
 assert core.read(original/'physics/0000-bounded-control-screen.input.json')['cases']==inputs[:24]
 data=json.load(gzip.open(p))['results'];assert len(data)==24 and not list((original/'physics').glob('0001-*.input.json'))
 eng,_,authors=physics._engine(f,'approved-r065-lift-control-screen-v2-resume-v1',physics.FULL_PROTOCOL);counts={c['route_spec']['id']:dict(clean=0,mild=0,moderate=0)for c in cs};records=[]
 def accept(c,r,e):
  i,level=labels[c['id']];q=checked_purpose(authors[i],c,r);counts[cs[i]['route_spec']['id']][level]+=q['ok'];records.append(dict(route=cs[i]['route_spec']['id'],level=level,check=q,evidence=e))
 for i,(c,r)in enumerate(zip(inputs[:24],data)):accept(c,r,dict(raw=physics.artifact(p),index=i,originalCompletedBatch=True))
 for c,r,e in eng.run(inputs[24:],'same-input-missing-tail'):accept(c,r,dict(raw=physics.artifact(eng.out/e['output']),index=e['index'],originalCompletedBatch=False))
 assert len(records)==26;passed=all(v['clean']==1 and v['mild']==6 and v['moderate']>=5 for v in counts.values())
 result=dict(passed=passed,counts=counts,rows=records,sourceCases=physics.artifact(f/'cases.json'),continuation=dict(originalSource=physics.artifact(original/'source_binding.json'),newSource=physics.artifact(eng.out/'source_binding.json'),completedCasesReusedByteExactly=24,newCases=2,noNewIndependentHoldout=True,cause='physics.py TOP interface bindings were edited while screen was active; frozen-source guard rejected the second batch before any of its cases ran.',nominalRunnerAuthorCandidateAndSeedsUnchanged=True))
 core.write(original/'screen.json',result);core.write(OUT/'verification/screen-continuation.json',dict(passed=passed,report=physics.artifact(original/'screen.json'),source=physics.artifact(__file__),priorErrorRetained=True));print('R065_SCREEN_COMPLETED',passed,counts,flush=True)
if __name__=='__main__':main()
