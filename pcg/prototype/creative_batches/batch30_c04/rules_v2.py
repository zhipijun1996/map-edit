"""C04 geometric cover audit and explicit allowed stepping on new cover."""
import copy
from pathlib import Path
from . import rules_v1 as prior
from pcg.prototype.workshop.rules import cmd,settle,ground,reward
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=prior.SOURCE_DEPENDENCIES+[Path(prior.__file__),HERE/'protocol-v2.json']
def materialize(interface=0,control=0):
 c=prior.materialize(interface,control)
 if interface==0:
  c['latches'][0]['paired_gate']=[300,430,20,120]
  c['platforms'][2]=[231,438,48,40]
 else:
  c['latches'][0]['paired_gate']=[200,430,20,180]
  c['platforms'][1]=[40,438,150,100]
  c['platforms'][3]=[-400,840,1400,40]
  c['exit_port']=[170,420];c['ports'][1]['position']=[170,420];c['goal']=[145,416,50,8]
  c['reward_sites']=[];reward(c,170,420,12)
  c['control_plan'][6]=settle(170,6)
 c['latches'][0]['return_access']=[c['exit_port'][0],c['exit_port'][1]-55]
 c['id']=c['id'].replace('v1','v2')
 c['rule_parameters']['new']=c['exit_port'];c['rule_parameters']['new_cover']=c['latches'][0]['paired_gate']
 c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','enemies','reward_sites']})
 c['map_specification']['objective']['physical_layout_sha256']=c['layout_uid']
 c['map_specification']['risk_reward']['reward_sites']=c['reward_sites']
 return c
def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in [0,1]:raise ValueError('outside C04 exact interfaces')
 return[materialize(interface,0)]
def purpose(c,r):
 q=prior.purpose(c,r);fs=r.get('frames',[]);event=q['causal']['actual_air_cover_swap']
 landing=next((f for f in fs if event and f['frame']>event['frame']and f.get('grounded')),None)
 b=c['latches'][0]['paired_gate'];on_B=bool(landing and b[0]-12<=landing['x']<=b[0]+b[2]+12 and abs(landing['y']+18-b[1])<=1 and any(p.get('open_b')is False for p in landing.get('workshop',{}).get('paired_gates',[])))
 if on_B:q['reasons']=[v for v in q['reasons']if v!='single_shot_first_landing_not_new_receiver']
 q['causal']['first_landing_is_actual_new_cover_top']=on_B
 q['ok']=not q['reasons'];return q
def alternatives(c):
 out=[v for v in prior.alternatives(c)if v['counterexample_kind']!='abandon-new-cover-after-arrival']
 v=copy.deepcopy(c);v['id']+='-counter-reopen-new-cover-and-expose';v['counterexample_kind']='reopen-new-cover-and-expose'
 v['control_plan'] += [cmd('shoot',aim_cell=dict(kind='bell',id='relay',receiver='access')),cmd('wait',140)];out.append(v)
 return out
