import json,sys,copy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'prototype/composable'))
from synthesis import compile_probe,gated
from pcg.prototype.workshop.engine import WorkshopEngine
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,settle,reward,finish
own=Path(__file__);adapter=own.with_name('runner-capabilities-v1.gd');out=ROOT/'results/workshop-creative-jump-wall-candidate-probes-v1';engine=WorkshopEngine(out,extra_sources=[own,adapter],runner_script=adapter)
cs=[]
for top in [280,300]:
 for land in [260,280]:
  c=base(f'late-{top}-{land}');c['capabilities']=['move','jump','double_jump'];c['family']='late-air-rise';c['platforms']=[[-160,438,400,100],[120,140,140,top-140],[340,land+18,220,72]];c['one_way_platform_indices']=[2]
  reward(c,420,land)
  finish(c,420,land,[cmd('axis',value=1),wait_x(205),cmd('jump'),cmd('jump_release',8),wait_x(280),cmd('jump'),cmd('jump_release',12),settle(420,5)]);cs.append(c)
for seed in range(4):
 d=json.loads((ROOT/f'results/workshop-creative-jump-wall-probes-v3/return-{seed}.json').read_text());c=d['materialized'];p=c['platforms'][2];x=p[0]+p[2]/2;y=p[1]-18;c['id']='return-'+str(seed);c['family']='step-off-wall-return';c['reward_sites']=[];reward(c,x,y);c['exit_port']=[x,y];c['world_bounds']=[-1200,-1200,4000,4000];c['max_frames']=400;c['trace_all']=True;cs.append(c)
for seed in range(4):
 c=compile_probe(['wall_contact','wall_jump','wall_separate','wall_contact','wall_jump'],['move','wall_climb'],100+seed,wall_layout='alternating');c.update(id='switch-'+str(seed),family='switchback-wall-ascent',platforms=[[-120,438,260,60],[195,200,32,620],[15,90,32,730],[240,258,160,72]],wall_platform_indices=[1,2],one_way_platform_indices=[3],reward_sites=[],entry_port=[80,420],exit_port=[280,240],thorns=[dict(surface_id='no-return-face',platform_index=1,face='left',start_offset=0,length=180,depth=8)],saws=[],moving_platforms=[],latches=[],enemies=[],world_bounds=[-1200,-1200,4000,4000]);c['control_plan'][-1]=settle(280,1);reward(c,280,240);c['goal']=[255,236,50,8];c['max_frames']=400;c['trace_all']=True;cs.append(c)
for c,r,e in engine.run(cs,'candidates'):
 (out/(c['id']+'.json')).write_text(json.dumps(dict(case=c,result=r,evidence=e)))
 print(c['id'],r['reason'],r.get('plan_error'),r.get('workshop',{}).get('coins'), 'events',[(f['frame'],round(f['x']),round(f['y']),f['traversal_state'],[a['type']for a in f['accepted']])for f in r.get('frames',[])if f['accepted']], 'miny',min((f['y']for f in r.get('frames',[])),default=None),flush=True)
