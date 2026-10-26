"""Revision accepts valid near-lip anticipation; fourth causal proposal pre-registered."""
import copy,json,importlib.util,sys
from pathlib import Path
OWN=Path(__file__);PARENT=OWN.with_name('production-v2.py');s=importlib.util.spec_from_file_location('jump_wall_prior_v2',PARENT);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.rules import cmd,settle
from pcg.prototype.composable.synthesis import gated
ROOT=m.ROOT;ADAPTER=m.ADAPTER
def compiler(req):
 f=req['recipe']
 if f=='late-air-rise':
  response=m.compiler(req)
  for c in response['cases']:
   c['id']=c['id'].replace('-v1-','-v3-');c['rule_parameters']['objective_revision']='Allow anticipatory jump within final 20 world units before lip; full-body preclear assertion was too strict and rejected legitimate same-relation alternatives.';c['generation_rule']['version']=3
  return response
 cs=[]
 for k in range(4):
  c=copy.deepcopy(json.loads((ROOT/'results/workshop-creative-jump-wall-rebound-probes-v2/rebound-195-480.json').read_text())['case']);c.update(id='bell-wall-rebound-v3-'+str(k),production_recipe=f,parent_family=f);c['latches'][0]['gate']=[-20,80,10,520];c['latches'][0]['open_seconds']=1.0;c['exit_port']=[-80,280];c['goal']=[-105,276,50,8];c['platforms'][2]=[-160,298,200,24];c['reward_sites'][0]['position']=[-80,280];c['reward_sites'][0]['region']=[-110,275,60,10];c['control_plan'][-1]=settle(-80,5);c['control_plan'][4]['trigger']['min_after']=2+k;c['max_frames']=480
  c['rule_parameters']=dict(relationship='Leftward bell aim recoils away from leftward reward; wall kick reverses travel without refilling the spent air shot.',source_type='llm_subagent_proposal',task_name='/root/jump_wall_creator',guard_adapter=str(ADAPTER.relative_to(ROOT.parent)),legacy_guard_routing_only=True,control_candidate=k,human_fun='unreviewed');c['generation_rule']=dict(id='creative/jump-wall/bell-wall-rebound',version=3,parameters=c['rule_parameters']);c['idea_ids']=['llm-subagent/jump-wall/bell-wall-rebound'];cs.append(c)
 spec=dict(m.spec('step-off-wall-return'),id='creative/jump-wall/bell-wall-rebound/0',required_family=f,objective=dict(relationship='Aim and arrival directions conflict; wall provides the reversal with shot charge remaining zero.'),capabilities=dict(version=1,status='defined',allOf=cs[0]['capabilities'],anyOfGroups=[]),rise=140)
 for c in cs:c['map_specification']=spec
 return dict(status='requires_physics',specifications=[spec],cases=cs)
def purpose(c,r):
 if c['production_recipe']=='late-air-rise':
  p=m.purpose(c,r);p['reasons']=[q for q in p['reasons']if q!='second_jump_not_preserved_until_full_body_cleared_roof'];airs=[f for f in r.get('frames',[])if any(e['type']=='air_jump'for e in f.get('accepted',[]))]
  if not any(f['x']>=240 and f['y']>298 for f in airs):p['reasons'].append('second_jump_not_saved_for_lip_exit_window')
  p['causal']['allowed_lip_anticipation_x']=240;p['ok']=not p['reasons'];return p
 fs=r.get('frames',[]);reasons=[];snap=r.get('capability_snapshot',{});ks=m.kicks(r);shots=[f for f in fs if any(e['type']=='shot'for e in f['accepted'])];hits=[e for e in r.get('plains',{}).get('events',[])if e['type']=='bell_open'];gate_x=-20
 if not r.get('ok'):reasons.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):reasons.append('player_harm')
 if sorted(snap.get('declared',[]))!=sorted(c['capabilities'])or snap.get('jump_enabled')or not snap.get('wall_enabled')or not snap.get('shoot_enabled'):reasons.append('actual_capability_snapshot_mismatch')
 if r.get('workshop',{}).get('coins',0)<8:reasons.append('reward_not_actually_claimed')
 direction=next((e['direction']for f in shots for e in f['accepted']if e['type']=='shot'),[0,0]);continuous=bool(shots and ks and all(not f['grounded']and f['shot_charges']==0 for f in fs if shots[0]['frame']<=f['frame']<=ks[0]['frame']))
 if not hits or not shots or direction[0]>=-.3 or not ks or not continuous:reasons.append('one_spent_shot_bell_then_wall_reversal_not_observed')
 if r.get('shots')!=1:reasons.append('extra_shot_bypasses_single_airflight_relationship')
 if not any(f['vx']>80 for f in fs if shots and ks and shots[0]['frame']<=f['frame']<ks[0]['frame'])or not any(f['vx']< -80 for f in fs if ks and f['frame']>ks[0]['frame']):reasons.append('actual_motion_reversal_missing')
 return dict(ok=not reasons,reasons=reasons,causal=dict(shot_aim=direction,shot_frames=[f['frame']for f in shots],bell_hits=hits,wall_kick_positions=[[f['x'],f['y']]for f in ks],spent_charge_continuous_to_wall=continuous),behavior=dict(shots=r.get('shots'),wall_jumps=r.get('wall_jumps')))
def alternatives(c):
 if c['production_recipe']=='late-air-rise':return m.alternatives(c)
 out=[];x=c['exit_port'][0]
 def add(label,plan):
  v=copy.deepcopy(c);v['id']=c['id']+'-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for i,q in enumerate(c['control_plan']):
  if q['op']in ['jump','shoot']:
   p=copy.deepcopy(c['control_plan']);p[i]['op']='wait';p[i].pop('aim_cell',None);add('omit-'+q['op'],p)
 for axis in [-1,0,1]:add('walk-'+str(axis),[cmd('axis',value=axis),settle(x,10)])
 for dy in [.25,.5,.7,.9,1.]:
  dx=(1-dy*dy)**.5
  add('direct-shot-'+str(dy),[cmd('axis',value=-1),cmd('shoot',direction=[dx,dy]),settle(x,5)])
 for hold in [0,8,20,35,50]:
  for dy in [.7,1.]:
   add('ground-preopen-recharge-'+str(hold)+'-'+str(dy),[cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='reverse-bell')),cmd('axis',hold,value=-1),cmd('settle',after=1,target_x=80,deadband=2),gated('wait','grounded',min_after=3,timeout=180),cmd('axis',value=-1),cmd('shoot',4,direction=[(1-dy*dy)**.5,dy]),settle(x,5)])
 for delay in [0,12,30,60,90]:
  p=copy.deepcopy(c['control_plan']);p[4]['trigger']['min_after']=delay;add('late-wall-kick-'+str(delay),p)
 return out
if __name__=='__main__':
 run('workshop-creative-jump-wall-production-v3',[dict(recipe=f,interfaces=[0])for f in ['late-air-rise','bell-wall-rebound']],cycles=2,library_root=ROOT/'results/workshop-creative-jump-wall-library-v1',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=OWN,extra_sources=[PARENT,ADAPTER],runner_script=ADAPTER)
