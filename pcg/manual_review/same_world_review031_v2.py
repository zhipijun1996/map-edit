"""One fixed composition of 200's frozen routes, no reset or new holdout."""
import copy
from pcg.migration import core,physics
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .prepare_review031_v1 import rows,OUT
from .finalize_review031_v1 import folder_for
def main():
 row=next(r for r in rows()if r['reviewId']=='200');f=folder_for(row);eng,cs,authors=physics._engine(f,'approved-r031-200-same-world-return-v2',physics.FULL_PROTOCOL)
 a,z=cs;c=copy.deepcopy(a);c.update(id='approved-r031-200-same-world-high-and-back-v2',control_plan=a['control_plan']+z['control_plan'],goal=z['goal'])
 c['route_spec']=dict(id='entry-high-entry-same-world',from_port='entry',to_port='entry',role='return');c['same_world_witness_only']=True
 core.write(eng.out/'protocol.json',dict(selection='single fixed concatenation; zero revisions or retries; no new independent holdout',maximumAttempts=1,priorFixture="v1 rejected 13 duplicate entry/exit definitions before physics; same control and physical state",fixtureCorrection="keep the two distinct real native definition Ports; only diagnostic final goal returns to the low dock",levels=dict(clean=1,mild=0,moderate=0),seed=271029031,claim='native same-world witness and bounded perturbations; separate from route formal qualification'))
 cases=[instantiate(physics.fresh(c,'same-world'),271029031,level,i)for level,n in [('clean',1)]for i in range(n)];results=[];counts=dict(clean=0,mild=0,moderate=0);recordings=[]
 for i,(case,raw,e)in enumerate(eng.run(cases,'same-world-no-reset')):
  q=checked_purpose(authors[0],case,raw);hit=[v for v in raw.get('plains',{}).get('events',[])if v.get('type')=='enemy_hit'];high=any(abs(v['y']-100)<5 and v.get('grounded')for v in raw.get('frames',[]));continuity=high and bool(hit)and raw.get('hp')==5 and not raw.get('returns')and raw.get('workshop',{}).get('coins')==16
  good=q['ok']and continuity;level='clean'if i==0 else'mild'if i<=6 else'moderate';counts[level]+=good;results.append(dict(level=level,check=q,continuousWorld=continuity,evidence=e))
  if good and level=='clean':recordings.append(physics._recording(case,raw))
 core.write(eng.out/'same-world.json',dict(counts=counts,rows=results,newIndependentHoldout=False,continuousNativeWitness=bool(recordings),formalScope='not additional formal independent qualification',sourceCases=physics.artifact(f/'physics-input-cases.json')));core.write(eng.out/'playback-cases.json',dict(cases=recordings));print('SAME_WORLD',counts,flush=True)
if __name__=='__main__':main()
