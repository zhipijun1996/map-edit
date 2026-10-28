"""Read-only proof audit, real-raw mechanism checks and tamper rejection."""
import copy,gzip,json
from pathlib import Path
from pcg.migration import core,physics,review_boundary_repair_v4 as boundary
from pcg.migration.review_counter_scope_v5 import classify
from .probe_review_refresh_v1 import AUTH
ROOT=AUTH.parent

def actual(run,e):return json.loads(gzip.decompress((run/e['output']).read_bytes()))['results'][e['index']]
def main():
 checks=[]
 def record(name,ok):assert ok,name;checks.append(dict(name=name,passed=True))
 def reject(name,fn):
  try:fn()
  except (ValueError,KeyError):checks.append(dict(name=name,passed=True));return
  raise AssertionError('tamper accepted: '+name)
 provenance=core.read('pcg/prototype/godot/source_provenance.json');project=core.REPO/'pcg/prototype/godot';bad=[p for p,h in provenance['files'].items()if core.sha(project/p)!=h];record('870 original runtime files unchanged',len(provenance['files'])==870 and not bad)
 for n,v in [('125','v1'),('140','v2'),('150','v1'),('154','v2')]:
  p=core.REPO/'pcg/results'/('approved-r024-'+n+'-qualified-final-'+v)/'migration-physics-fixture-repair-v1.json';r=core.read(p);boundary.validate_lineage(r,p);record(n+' exact boundary supplement',True)
  x=copy.deepcopy(r);x['routes'][0]['passed']=False;reject(n+' cannot replace original held-out result',lambda:boundary.validate_lineage(x,p))
  x=copy.deepcopy(r);x['boundaryRepair']['newIndependentHoldout']=True;reject(n+' cannot fabricate another holdout',lambda:boundary.validate_lineage(x,p))
  x=copy.deepcopy(r);x['actualAttempts']-=1;reject(n+' cannot hide repair attempt',lambda:boundary.validate_lineage(x,p))
 run=core.REPO/'pcg/results/approved-r024-133-qualified-final-v1';counter=next(v for v in core.read(run/'counterexamples.json')if v['probe']['kind']=='omit-all-shots');e=counter['evidence'];case=core.read(run/'physics'/(e['batch']+'.input.json'))['cases'][e['index']];raw=actual(run,e);cal=core.read(run/'calibration-0.json');base=actual(run,next(v for v in cal['rows']if v['level']=='clean'and v['purpose']['ok'])['evidence']);q=counter['causalCheck'];out=counter['externalOutcome'];j=counter['adjudication']
 accepted=classify(case,raw,q,out,j,base);record('real rejected exterior path is not an accepted internal solution',not accepted['invalidates_design']and accepted['accepted_module_solution']is False and raw['hp']==5)
 for name,cc,rr,qq in [('wrong version',dict(case,approved_implementation=dict(case['approved_implementation'],designVersion='sha256:wrong')),raw,q),('real player harm',case,dict(raw,hp=4),q),('another causal rejection',case,raw,dict(q,reasons=q['reasons']+['actual_player_harm'])),('a healthy interior bypass',case,raw,dict(q,reasons=[]))]:record('counter scope rejects '+name,classify(cc,rr,qq,out,j,base)==j)
 run=core.REPO/'pcg/results/approved-r024-consumer-probes-v2';row=core.read(run/'mechanism-checks.json')['rows'][0];r=actual(run,row['evidence']);frames=r['frames'];pairs=[]
 for a,b in zip(frames,frames[1:]):
  if not b.get('refresh_consumers')or b['refresh_consumers'][0]['carried_frames']<=a['refresh_consumers'][0]['carried_frames']:continue
  x=a['plains']['enemies'][0];y=b['plains']['enemies'][0];pa=a['moving_platforms'][0]['position'];pb=b['moving_platforms'][0]['position'];pairs.append(abs((y['x']-x['x'])-(pb[0]-pa[0]))<.001 and abs((y['y']-x['y'])-(pb[1]-pa[1]))<.001)
 xs=[f['plains']['enemies'][0]['x']for f in frames];record('carrier actual enemy displacement equals 320px ferry displacement',bool(pairs)and all(pairs)and abs(max(xs)-min(xs)-320)<.001 and r['hp']==5 and not r['returns'])
 mechanism=[];run=core.REPO/'pcg/results/approved-r024-consumer-probes-v1'
 for row in core.read(run/'mechanism-checks.json')['rows'][1:]:
  r=actual(run,row['evidence']);record(row['id']+' genuine native mechanism',row['passed']and r['hp']==5 and not r['returns']);mechanism.append(row)
 for row in core.read(AUTH/'handoff.json')['rows']:
  record(row['reviewId']+' exact approval source bytes',core.sha(core.REPO/row['designFile'])==row['designFileSha256']and core.sha(core.REPO/row['sourceModule']['file'])==row['sourceModule']['sha256'])
 deleted=core.read(ROOT/'deletions.json');record('all 21 discarded active directories absent',len(deleted['rows'])==21 and all(not(core.REPO/'modules'/r['moduleId']).exists()for r in deleted['rows']))
 core.write(ROOT/'verification/evidence-audit.json',dict(passed=True,checks=checks,protectedFiles=870,protectedMismatches=bad,newIndependentHoldout=False,newPhysicsAttempts=0,carrierComparedNativeSteps=len(pairs),mechanism=mechanism));print('AUDIT_PASS',len(checks),flush=True)
if __name__=='__main__':main()
