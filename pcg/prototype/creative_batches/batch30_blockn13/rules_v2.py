"""Existing carrier/dock composition after real front/mid/rear core controls."""
import copy,math
from pathlib import Path
from .core_v2 import candidate as core
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,regions,raster,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('dock-parking-relative-recoil-budget',)
RUNNER_SCRIPT=HERE/'runner_v2.gd';NATIVE_SCENE=HERE/'main_v1.tscn';EXPORT_SCRIPT=HERE/'export_v1.mjs'
SOURCE_DEPENDENCIES=[HERE/n for n in ['protocol-v1.json','protocol-v2.json','idea-source-v1.json','core_v1.py','core_v2.py','runner_v1.gd','runner_v2.gd','observe_v1.gd','main_v1.gd','main_v1.tscn','export_v1.mjs']]+[HERE.parent/'machinery'/n for n in ['dock_runner_v11.gd','dock_binding_v11.gd','dock_latch_v11.gd']]+[HERE.parent/'batch30_d05/mount_v1.gd',HERE.parent/'batch30_runtime/export_block_v1.mjs',HERE.parent/'batch30_runtime/export_mounted_v1.mjs',HERE.parent/'batch30_runtime/block_draw_v1.gd']
CONTROLS=[(1,1240,20),(1,1260,16),(2,1240,20),(2,1260,16)]
def candidate(interface=0,control=0):
 if interface not in [0,1]or control not in range(4):raise ValueError('outsideN13registered2world/4controlrange')
 walk,takeoff,hold=CONTROLS[control];c=core(walk)
 c['control_plan']=c['control_plan'][:-1]+[cmd('wait',16),cmd('axis',value=1),wait_x(takeoff),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-.5,math.sqrt(.75)]),settle(1640,0)]
 c['reward_sites']=[dict(id='gate-cache',position=[1640,462],region=[1622,454,36,16],amount=12)]
 c['goal']=[1633,458,14,8]
 c.pop('validation_fixture',None)
 c.update(id=f'b30-blockn13-v2-i{interface}-c{control}',family=RECIPES[0],trace_all=False,max_frames=1800,interface=interface,production_recipe=RECIPES[0],challenge_route=True,expected_reward=12,required_rewards=['gate-cache'],idea_ids=['B31-N13'],native_scene='res://prototype/creative_batches/batch30_blockn13/main_v1.tscn',native_block_scene=str(NATIVE_SCENE.relative_to(HERE.parents[3])),layout_title='停车前，给身体留后退余量')
 docks={'A':[24,590],'B':[1640,462]};normals={'A':[-1,0],'B':[1,0]};bindings={'A':([0,4],'W'),'B':([12,3],'E')}
 if interface:
  def point(p):return[1664-p[0],p[1]]
  def rect(r):return[1664-r[0]-r[2],*r[1:]]
  c['platforms']=[rect(r)for r in c['platforms']];c['world_bounds']=rect(c['world_bounds'])
  for key in ['spawn','entry_port','exit_port']:c[key]=point(c[key])
  c['goal']=rect(c['goal'])
  for p in c['moving_platforms']:p['start']=point(p['start']);p['finish']=point(p['finish'])
  for l in c['latches']:
   l['bell']=point(l['bell']);l['gate']=rect(l['gate'])
   if l.get('carrier_dock'):l['carrier_dock']['rect']=rect(l['carrier_dock']['rect'])
  for s in c['reward_sites']:s['position']=point(s['position']);s['region']=rect(s['region'])
  for q in c['control_plan']:
   if q['op']=='axis':q['value']=-q['value']
   if 'direction'in q:q['direction'][0]=-q['direction'][0]
   if 'aim_target'in q:q['aim_target']=point(q['aim_target'])
   if 'target_x'in q:q['target_x']=1664-q['target_x']
   d=q.get('trigger',{}).get('dynamic',{})
   if d.get('kind')=='actor_x':d['value']=1664-d['value'];d['direction']='lte'if d['direction']=='gte'else'gte'
  docks={k:point(v)for k,v in docks.items()};normals={'A':[1,0],'B':[-1,0]};bindings={'A':([12,4],'E'),'B':([0,3],'W')}
 c['ports']=[dict(id=k,position=docks[k][:],normal=normals[k],support_index=i)for k,i in [('A',0),('B',1)]]
 ports={k:block_port(k,*bindings[k],docks[k])for k in ['A','B']}
 reservations=[[0,0,1664,1152]];m=declare(dict(case=c,ports=ports,action_clearance=reservations),[(x,y)for x in range(13)for y in range(9)]);assert not validate(m),validate(m)
 c['block_grid']=m['block_grid'];c['block_ports']=ports;c['block_reservations']=reservations
 c['route_spec']=dict(id='A-to-B',from_port='A',to_port='B',role='main',via_ports=[],required_rewards=['gate-cache'],require_bell=True)
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites','block_grid','block_ports']})
 c['rule_parameters']=dict(interface=interface,control=control,walk_kind=walk,relative_forward_walk_frames=[0,30,50][walk],east_takeoff=takeoff,exit_hold=hold,mirror=bool(interface),mounted_receiver_offset=[-200 if interface else 200,-80],core_rule=2,first_initial_shore_recoil_failure_retained=True)
 c['generation_rule']=dict(id='batch30/N13',version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='batch30/N13/'+str(interface),source_type='explicitmodel_authored_dock_return_currencydemand',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=interface,physical_layout_sha256=c['layout_uid'],core='ParkingholdsrealnativeArea2Dgatebutoriginalgroundrecoilconsumesremainingdecklength; originalreturnusemustbeactualseparatefixture',independent_new_family_claim=False),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[normals['A'],normals['B']]),relations=[dict(from_port='A',to_port='B',role='main',route_id='A-to-B')],space=dict(block_size=128,max_width=1664,max_height=1152,max_port_span_x=1664,port_profiles=['ground64/v1']),boundary_policy='open',enclosing_walls=False,rewards=[dict(kind='currency',amount=12,status='explicitderivedallocationnotMapbudget')],difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='SupportedA,originalpausedPstart; trueDockgateclosed',exit='ObservedB/12coins andobservedDockstate only; no arbitraryreturnpromise'),return_conditions='Sameworldreturnfixtureseparate;freshB->A/arbitraryphase/boundary/seam/fullMapUNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
 return c
def core_purpose(c,r):
 why=[];fs=r.get('frames',[])
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if r.get('returns'):why.append('world_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('workshop',{}).get('coins')!=12:why.append('actual_reward_missing')
 support=[f for f in fs if f.get('support_id')=='parking-deck']
 if not support:why.append('actual_carrier_support_missing')
 gx,gy,gw,gh=c['latches'][1]['gate'];cross=[f for f in fs if f['x']-12<gx+gw and f['x']+12>gx and f['y']-18<gy+gh and f['y']+18>gy]
 bad=[f['frame']for f in cross if not any(d['id']=='dock-gate'and d['open']and d['gate_layer']==0 and d['gate_disabled']for d in f.get('n13',{}).get('docks',[]))]
 if not cross or bad:why.append('actual_body_open_dock_gate_crossing_missing')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:why.append('actual_body_outside_frozen_ownership')
 return dict(ok=not why,reasons=why,causal=dict(real_carrier_support_frames=len(support),actual_gate_crossing_frames=[f['frame']for f in cross],closed_gate_body_frames=bad,outside_count=len(outside),final_dock=fs[-1].get('n13',{}).get('docks')if fs else None,actual_carrier_toggles=[e for e in r.get('workshop',{}).get('events',[])if e['type']=='carrier_toggle']),behavior={k:r.get(k)for k in ['shots','jumps','ticks']})
def purpose(c,r):
 q=core_purpose(c,r);toggles=q['causal']['actual_carrier_toggles'];stop=next((e for e in toggles if not e['running']),None)
 after=[f for f in r.get('frames',[])if stop and stop['frame']<f['frame']<=stop['frame']+10 and f.get('support_id')=='parking-deck']
 if not stop or len(after)<6:q['reasons'].append('nominal_ground_stop_real_retained_deck_missing')
 final=q['causal'].get('final_dock')or[]
 if not any(d['occupied']and d['open']for d in final):q['reasons'].append('nominal_useful_held_dock_at_B_missing')
 q['causal'].update(actual_stop=stop,actual_supported_after_stop=len(after));q['ok']=not q['reasons'];return q
