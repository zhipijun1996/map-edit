"""Final hypothesis: chase from behind; low path passes below the parked lift."""
from pathlib import Path
from . import rules_v1 as old
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=old.RECIPES;RUNNER_SCRIPT=old.RUNNER_SCRIPT;NATIVE_SCENE=old.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(old.__file__),*old.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json',HERE/'probe_v2.py']

def candidate(interface=0,control=0,route='high'):
 c=old.candidate(interface,control,route);c['latches'][0]['bell']=[560,476]
 c['moving_platforms'][1].update(start=[720,416],travel_duration=.65)
 c['platforms'][2]=[1056,608,224,48];board=c['control_plan'][:14]
 if route=='high':
  takeoff=[828,840,852,864][control];hold=[12,12,16,16][control]
  c['control_plan']=board+[wait_x(700),cmd('axis',value=1),wait_x(takeoff),cmd('jump'),cmd('jump_release',hold),cmd('shoot',aim_cell=dict(kind='bell',id='intercept-start')),old.on('intercept-carrier'),cmd('axis',value=0),cmd('wait',8),wait_x(1080),cmd('axis',value=1),cmd('jump'),cmd('jump_release',8),cmd('shoot',6,direction=[-.8,.6]),settle(1256,6)]
 else:
  takeoff=[680,700,720,740][control];delay=[0,2,4,6][control]
  c['control_plan']=board+[wait_x(takeoff),cmd('axis',value=1),dict(op='wait',trigger=dict(state='airborne',timeout=240)),cmd('shoot',delay,direction=[-.98,.1989974874]),settle(1256,6)]
 c['id']=c['id'].replace('blockn02-v1','blockn02-v2')
 c['rule_parameters'].update(departure_actor_x=takeoff,active_static_bell=[560,476],new_rule='P2chasesfrombehind, lowpassesunderstaticP2',carrier2_speed=432/.65)
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites','block_grid','block_ports']})
 c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 c['map_specification']=old.specification(c)
 return c

def purpose(c,r):
 q=old.purpose(c,r);fs=r.get('frames',[])
 if 'onward_after_P2_landing_missing'in q['reasons']:
  support=[f for f in fs if f.get('grounded')and f.get('support_id')=='intercept-carrier']
  if support and any(f['frame']>support[0]['frame']and any(e.get('type')=='ground_jump'for e in f.get('accepted',[]))for f in fs):
   q['reasons'].remove('onward_after_P2_landing_missing');q['causal']['ordinary_onward_hop_is_allowed_after_realP2']=True
 if q['reasons']==['low_route_unexpected_second_carrier_use']and r.get('jumps',0)>=2:
  q['reasons']=[];q['causal']['low_paid_extra_groundjump_via_realP2_allowed']=True
 q['ok']=not q['reasons'];return q
