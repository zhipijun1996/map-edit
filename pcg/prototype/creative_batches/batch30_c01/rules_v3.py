"""C01 final two-space rule, constrained by actual support-transfer evidence."""
import copy
from pathlib import Path
from . import rules_v2 as prior
from .alternatives_v1 import alternatives
from pcg.prototype.workshop.rules import wait_x
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'alternatives_v1.py',HERE/'protocol-v3.json']

def candidate(interface=0,control=0):
 if interface not in [0,1]:raise ValueError('outside two registered C01 spaces')
 c=prior.candidate(0,control);c['id']=f'b30-c01-v3-i{interface}-c{control}'
 shore=[1380,330,220,120]if interface==0 else[1030,180,120,120]
 width=1700 if interface==0 else 1250
 c['platforms']=[[-100,438,340,45],shore,[-100,160,450,120],[-100,800,width,60],[-100,680,160,32],[100,560,260,32]]
 latch=c['latches'][0];latch['gate']=[220,438,340 if interface==0 else 280,24]
 latch['paired_gate']=[820,350,270,24]if interface==0 else[700,280,210,24]
 latch['bell']=[440,390]if interface==0 else[390,390]
 exit=[1490,312]if interface==0 else[1100,162]
 c['ports'][1]['position']=exit;c['exit_port']=exit;c['goal']=[exit[0]-25,exit[1]-4,50,8]
 c['reward_sites'][0].update(position=exit,region=[exit[0]-30,exit[1]-5,60,10])
 c['interface']=interface;c['control_plan'][1]=wait_x(520 if interface==0 else 460)
 c['control_plan'][5]=wait_x(970 if interface==0 else 810);c['control_plan'][10]=wait_x(1050 if interface==0 else 870)
 c['control_plan'][-1]['target_x']=exit[0]
 c['rule_parameters'].update(interface=interface,launch_x=520 if interface==0 else 460,old_bridge=latch['gate'],new_bridge=latch['paired_gate'],shape='wide horizontal broken arch'if interface==0 else'compact rising broken arch')
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites']})
 c['layout_title']='跳出去，桥才出现 / '+('断拱横渡'if interface==0 else'紧凑升层')
 c['generation_rule']=dict(id='batch30/C01',version=3,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['challenge_route']=True
 return c

def support_contact(f,rect):
 x,y,w,h=rect
 return bool(f.get('grounded'))and f['x']+12>x and f['x']-12<x+w and abs(f['y']+18-y)<1

def purpose(c,r):
 q=prior.purpose(c,r);fs=r.get('frames',[])
 q['reasons']=[why for why in q['reasons']if why not in ['first_postshot_landing_not_new_bridge','second_phase_shot_missing']]
 first=q['causal']['first_shot_frame'];land=next((f for f in fs if f['frame']>first and f.get('grounded')),None)
 contact=bool(land and support_contact(land,c['latches'][0]['paired_gate']))
 state=next((p for p in (land or{}).get('workshop',{}).get('paired_gates',[])if p['id']=='bridge-pair'),{})
 if not contact or not state.get('open_a')or state.get('open_b')is not False:q['reasons'].append('first_postshot_landing_not_actual_closed_new_bridge')
 jumps=[f for f in fs if land and f['frame']>land['frame']and any(e.get('type')=='ground_jump'for e in f.get('accepted',[]))]
 if not jumps:q['reasons'].append('onward_ground_jump_from_new_bridge_missing')
 prior_air=[f for f in fs if first<f['frame']<(land['frame']if land else first)and not f.get('grounded')]
 q['causal'].update(actual_first_support_body_overlap=contact,actual_pair_at_first_landing=state,airborne_zero_charge_frames=sum(f.get('shot_charges')==0 for f in prior_air),onward_ground_jump_frames=[f['frame']for f in jumps])
 q['ok']=not q['reasons'];return q

def specification(interface,c):
 return dict(schema='map-notes/challenge-specification/v1',id=f'batch30/C01/{interface}',source_type='model_authored_challenge_specification',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=interface,physical_layout_sha256=c['layout_uid'],core='actual launch support A is removed while landing support B appears from same airborne recoil shot',nonnegotiable='first post-shot contact B and real resource renewal; next ground jump continues'),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port='A',to_port='B',role='main',route_id='support-swap')],space=dict(max_width=1700 if interface==0 else 1250,max_height=950 if interface==0 else 1250,max_port_span_x=1500),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='Original supported fresh A, original single jump/air shot; original real contacts and no resource writes',exit='Observed stable B/reward; arbitrary ingress or return UNKNOWN'),return_conditions='Missed-landing recovery fixture separately measured; B->A remains UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
