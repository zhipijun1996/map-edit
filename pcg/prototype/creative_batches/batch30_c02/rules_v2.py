"""C02 repair: receiver banks fit the actual measured one-shot crossing."""
import copy,math
from pathlib import Path
from . import rules_v1 as prior
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle,reward
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=prior.SOURCE_DEPENDENCIES+[Path(prior.__file__),HERE/'protocol-v2.json']
CONTROLS=[(12,10),(12,14),(20,6),(20,10)]

def materialize(interface=0,control=0):
 c=prior.materialize(interface,control);hold,delay=CONTROLS[control]
 front,top,gate_x=(590,530,550)if interface==0 else(550,400,510)
 target=[front+140,top-18]
 c['platforms'][1]=[front,top,280,100]
 c['platforms'][2]=[250,80,gate_x+70-250,50]
 c['latches'][0]['paired_gate'][0]=gate_x
 c['exit_port']=target;c['goal']=[target[0]-25,target[1]-4,50,8]
 c['ports'][1]['position']=target
 c['reward_sites']=[];reward(c,*target,12)
 c['control_plan'][3]=cmd('jump_release',hold);c['control_plan'][4]=cmd('shoot',delay,aim_cell=dict(kind='bell',id='airlock-pair'));c['control_plan'][5]=settle(target[0],6)
 c['id']=f'b30-c02-v2-i{interface}-c{control}'
 c['layout_title']='先穿第一门，再换第二门 / '+('下沉接收岸'if interface==0 else'抬高近岸')
 c['rule_parameters'].update(hold=hold,shot_after_release=delay,bank=c['platforms'][1],gate_B=c['latches'][0]['paired_gate'])
 c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','moving_platforms','latches','reward_sites']})
 c['map_specification']['objective'].update(physical_layout_sha256=c['layout_uid'],receiver=target,role='descending_receiver'if interface==0 else'rising_receiver')
 return c

def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in [0,1]:raise ValueError('unsupported C02 demand')
 return [materialize(interface,0)]

def purpose(c,r):
 fs=r.get('frames',[]);why=[];pairs=r.get('workshop',{}).get('paired_gates',[]);state=pairs[0]if pairs else{}
 near=c['latches'][0]['gate'];far=c['latches'][0]['paired_gate']
 by_frame={f['frame']:f for f in fs}
 events=[e for e in state.get('events',[])if e.get('type')=='pair_switch'and e.get('open')=='B'and e.get('airborne')]
 candidates=[e for e in events if e['frame']in by_frame and by_frame[e['frame']]['x']-12>=near[0]+near[2]+6 and by_frame[e['frame']]['x']+12<far[0]]
 first=candidates[-1]if candidates else None;at=by_frame.get(first['frame'])if first else None
 start=max((f['frame']for f in fs if first and f['frame']<first['frame']and f.get('grounded')),default=0)
 landing=next((f for f in fs if first and f['frame']>first['frame']and f.get('grounded')),None)
 stop=landing['frame']if landing else (fs[-1]['frame']if fs else 0)
 middle=[f for f in fs if first and start<f['frame']<=stop and f['x']-12>=near[0]+near[2]and f['x']+12<=far[0]]
 crossed=[f for f in fs if first and first['frame']<=f['frame']<=stop and f['x']-12>=far[0]+far[2]]
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('world_reset')
 if r.get('workshop',{}).get('coins',0)<12:why.append('required_reward_not_claimed')
 if not first:why.append('full_body_airborne_ordered_swap_missing')
 if not middle or any(f.get('grounded')for f in middle):why.append('unsupported_middle_not_preserved')
 if not crossed:why.append('body_never_crossed_open_B_before_landing')
 if not landing or landing.get('support_id')!='Platform1':why.append('first_post_swap_landing_not_receiver')
 if state.get('open_a')is not False or state.get('open_b')is not True:why.append('wrong_final_gate_state')
 return dict(ok=not why,reasons=why,causal=dict(actual_swap=first,swap_body=({k:at.get(k)for k in ['frame','x','y','grounded','shot_charges']}if at else None),unsupported_middle_frames=len(middle),gate_B_crossing_frames=len(crossed),first_landing=({k:landing.get(k)for k in ['frame','x','y','grounded','support_id']}if landing else None),pair_final=state),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')))

def alternatives(c):
 out=prior.alternatives(c);target=c['exit_port'][0]
 for v in out:
  for q in v['control_plan']:
   if q.get('op')=='settle':q['target_x']=target
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for launch in [400,470,520]:
  for dy in [.75,.95,1.]:
   p=[cmd('axis',value=1),wait_x(launch),cmd('axis',value=0),ground(),cmd('wait',8),cmd('shoot',aim_cell=dict(kind='bell',id='airlock-pair',receiver='access')),cmd('wait',24),cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),cmd('shoot',6,direction=[-math.sqrt(max(0,1-dy*dy)),dy]),settle(target,6)]
   add(f'ground-middle-open-and-climb-{launch}-{dy}',p)
 return out
