"""Preparation then commitment using original two-target ShotLatch and timer."""
import argparse,copy
from pathlib import Path
from pcg.prototype.creative_batches.plains50_new_relations.probe_v6 import prepared_gate
from pcg.prototype.creative_batches.plains50_new_relations.production_v1 import specification
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.counterexamples import alternatives as generic_alternatives
from pcg.prototype.workshop.rules import cmd,wait_x,settle
HERE=Path(__file__).parent

def compiler(request):
 cs=[];ss=[]
 for v in [0,1]:
  source=prepared_gate(v);source['rule_parameters'].update(interface=v,scope='canonical witness uses ground preparation and airborne second hit; alternative valid sequence timing allowed, no universal same-shot necessity')
  s=specification(source,v);s['risk_reward']['amount']=12;ss.append(s)
  for hold in [8,10]:
   c=copy.deepcopy(source);c['id']=f'p50-prepared-air-sequence-i{v}-h{hold}';c['control_plan'][6]=cmd('jump_release',after=hold);c['control_plan'][7]['trigger']['after']=18-hold;c['map_specification']=s;c['production_recipe']='prepared-air-sequence';c['idea_ids']=['p50-new/prepared-air-sequence'];c['generation_rule']=dict(id='plains50-new/prepared-air-sequence',version=1,source_type='current_codex_subagent',parameters=c['rule_parameters']);cs.append(c)
 return dict(status='requires_physics',specifications=ss,cases=cs)

def purpose(c,r):
 fs=r.get('frames',[]);why=[]
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('workshop',{}).get('coins',0)<12:why.append('reward_not_claimed')
 shots=[f for f in fs if any(e['type']=='shot'for e in f.get('accepted',[]))];armed=[f for f in fs if any(b['id']=='short-bell'and b['sequence_step']==1 and not b['open']for b in f.get('plains',{}).get('bells',[]))];hits=[e for e in r.get('plains',{}).get('events',[])if e['type']=='bell_open']
 g=c['latches'][0]['gate'];cross=[f for f in fs if f['x']-12<g[0]+g[2]and f['x']+12>g[0]and f['y']+18>g[1]and f['y']-18<g[1]+g[3]]
 if len(shots)<2 or not armed or not hits or not cross:why.append('real_preparation_sequence_then_door_crossing_missing')
 return dict(ok=not why,reasons=why,causal=dict(actual_shots=len(shots),air_shots=sum(not f['grounded']for f in shots),armed_before_open_frames=len(armed),actual_sequence_opens=len(hits),body_door_cross_frames=len(cross),same_air_shot_scope='canonical witness only; valid early sequence alternatives accepted'))

def alternatives(c):
 out=generic_alternatives(c)
 def add(k,p):
  d=copy.deepcopy(c);d['id']+='-counter-'+k;d['counterexample_kind']=k;d['control_plan']=p;out.append(d)
 for delay in [0,20,40]:
  p=[cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='short-bell',receiver='second')),cmd('shoot',after=18,aim_cell=dict(kind='bell',id='short-bell')),cmd('wait',after=delay)]+copy.deepcopy(c['control_plan'][3:]);add('wrong-order-'+str(delay),p)
 for x in [80,180,220]:
  p=[cmd('shoot',aim_cell=dict(kind='bell',id='short-bell')),cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='short-bell',receiver='second'))]+copy.deepcopy(c['control_plan'][3:]);add('ground-preopen-both-'+str(x),p)
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',default='workshop-plains50-new-sequence-production-v1');a=p.parse_args();extras=[HERE/n for n in ['probe_v6.py','production_v1.py','sequence_runner_v1.gd','sequence_main_v1.gd','sequence_main_v1.tscn','sequence_export_v1.mjs']]+[HERE.parent/'resource_routes/export-v4.mjs']
 run(a.name,requests=[dict(recipe='prepared-air-sequence')],cycles=1,compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=extras,runner_script=HERE/'sequence_runner_v1.gd',export_script=HERE/'sequence_export_v1.mjs')
