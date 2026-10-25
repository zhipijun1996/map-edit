import sys,json,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'prototype/composable'))
from synthesis import gated
from pcg.prototype.workshop.engine import WorkshopEngine
from pcg.prototype.workshop.rules import cmd
OWN=Path(__file__);AD=OWN.with_name('runner-capabilities-v1.gd');OUT=ROOT/'results/workshop-creative-jump-wall-wallslide-probes-v3';eng=WorkshopEngine(OUT,extra_sources=[OWN,AD],runner_script=AD)
cs=[]
for phase in [0,.25,.5,.85]:
 for window in [[.28,.34],[.34,.40]]:
  c=copy.deepcopy(json.loads((ROOT/'results/workshop-creative-jump-wall-wallslide-probes-v1/wallslide-235.json').read_text())['case']);c['platforms'][2]=[40,-500,20,600];c['thorns'][0]['length']=600;c['thorns'] += [dict(surface_id='right-upper-no-reset',platform_index=1,face='left',start_offset=0,length=80,depth=8),dict(surface_id='right-top-no-perch',platform_index=1,face='top',start_offset=0,length=32,depth=8)];c['id']='slide-saw-'+str(phase)+'-'+str(window[0]);c['saws']=[dict(source_id='mouth-saw',origin=[60,170],travel=[0,100],radius=18,period=.9,initial_phase=phase,damage=1,contact_interval=.7)];c['control_plan'][3]['trigger']['dynamic']=dict(kind='saw_phase',id='mouth-saw',window=window);cs.append(c)
for c,r,e in eng.run(cs,'saw-slide'):
 (OUT/(c['id']+'.json')).write_text(json.dumps(dict(case=c,result=r,evidence=e)))
 fs=r.get('frames',[]);ks=[f for f in fs if any(q.get('state')=='wall_kick'for q in f['accepted'])];print(c['id'],r['reason'],r.get('plan_error'),r.get('workshop',{}).get('coins'),'kicks',[(f['frame'],round(f['y']),f['saws'])for f in ks],flush=True)
