import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'prototype/composable'))
from synthesis import compile_probe,materialize
from pcg.prototype.workshop.engine import WorkshopEngine
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,settle
from pcg.prototype.composable.synthesis import gated
out=ROOT/'results/workshop-creative-jump-wall-probes-v3';engine=WorkshopEngine(out,extra_sources=[Path(__file__),Path(__file__).with_name('runner-capabilities-v1.gd')],runner_script=Path(__file__).with_name('runner-capabilities-v1.gd'))
cs=[]
for seed in range(4):
 for tag,word,caps,layout in [
 ('return',['wall_contact','wall_jump'],['move','wall_climb'],'same'),
 ('renew',['ground_jump','air_jump','wall_contact','wall_jump','air_jump'],['move','jump','double_jump','wall_climb'],'same'),
 ('switch',['wall_contact','wall_jump','wall_separate','wall_contact','wall_jump','wall_separate','wall_contact','wall_jump'],['move','wall_climb'],'alternating')]:
  c=compile_probe(word,caps,100+seed,wall_layout=layout);c.update(id=f'{tag}-{seed}',family=tag,reward_sites=[],entry_port=c['spawn'][:],exit_port=[120,420],latches=[],enemies=[],thorns=[],saws=[],moving_platforms=[],max_frames=360)
  cs.append(c)
for edge in [260,280]:
 for delay in [0,5]:
  c=base(f'late-{edge}-{delay}');c['capabilities']=['move','jump','double_jump'];c['platforms']=[[-160,438,400,100],[120,180,edge-120,180]]
  c['control_plan']=[cmd('axis',value=1),wait_x(205),cmd('jump'),cmd('jump_release',8),wait_x(edge+20),cmd('jump',delay),cmd('jump_release',12)]
  cs.append(c)
for c,r,e in engine.run(cs,'motion'):
 fs=r.get('frames',[]);g=materialize(c,r,width=200,clearance=60) if not c['id'].startswith('late') else None
 row=dict(case=c,result=r,evidence=e,materialized=g)
 (out/(c['id']+'.json')).write_text(json.dumps(row))
 print(c['id'],r['reason'],r.get('plan_completed'),r.get('plan_error'), 'events',[(f['frame'],round(f['x']),round(f['y']),f['jumps_used'],f['traversal_state'],[a['type']for a in f['accepted']])for f in fs if f['accepted']], 'end',[(f['frame'],round(f['x']),round(f['y'])) for f in fs[::30]],'receiver',g['exit_port'] if g and 'exit_port'in g else g['goal']if g else None,flush=True)
