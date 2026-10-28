from pathlib import Path
from . import rules_v1 as prior
from pcg.prototype.workshop.rules import cmd,ground,settle
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=prior.SOURCE_DEPENDENCIES+[Path(prior.__file__),HERE/'main-solve-protocol-v2.json']
def materialize(interface=0,route='main',control=0):
 c=prior.materialize(interface,'recovery'if route=='retry'else route,control)
 c['platforms']=[[-100,438,300,80],[500,360,240,100],[270,630,130,40],[250,490,20,140],[400,490,20,140]]
 c['latches'][0].update(gate=[250,-200,20,690],paired_gate=[270,490,130,30])
 if route=='retry':
  c['control_plan'] += [cmd('jump'),cmd('jump_release',20),cmd('shoot',aim_cell=dict(kind='bell',id='recovery-pair',receiver='access')),settle(80),ground(),cmd('wait',10)]+prior.nominal()
  c['exit_port']=[650,342];c['goal']=[625,338,50,8];c['expected_reward']=12;c['required_rewards']=['visible-cache'];c['route_spec']['to_port']='B';c['rule_parameters']['route']='retry';c['max_frames']=1400
 c['id']=c['id'].replace('v1','v2').replace('-recovery-','-retry-'if route=='retry'else'-recovery-');c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','reward_sites']});return c
def purpose(c,r):
 if c['rule_parameters']['route']!='retry':return prior.purpose(c,r)
 copy=__import__('copy').deepcopy(c);copy['rule_parameters']['route']='recovery';q=prior.purpose(copy,r);pair=(r.get('workshop',{}).get('paired_gates')or[{}])[0];events=[v for v in pair.get('events',[])if v.get('type')=='pair_switch'];fs=r.get('frames',[])
 if not any(v.get('open')=='A'and v.get('airborne')for v in events):q['reasons'].append('no_actual_air_restore')
 if not any(f.get('grounded')and f.get('support_id')=='Platform0'and f['frame']>min(q['causal']['cavity_grounded_frames']or[9999])for f in fs):q['reasons'].append('no_real_entry_return_before_retry')
 if r.get('workshop',{}).get('coins',0)<12:q['reasons'].append('retry_reward_missing')
 q['ok']=not q['reasons'];return q
