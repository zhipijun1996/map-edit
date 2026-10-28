"""New compact loop rule: preserve old C09 failures, use original paired Cell."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,raster,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent;CELL=HERE.parent/'batch30_cell';OLD=HERE.parent/'batch30_c09'
RECIPES=('folded-reward-upper-out-lower-back',)
RUNNER_SCRIPT=OLD/'runner_v1.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(__file__),HERE/'protocol-v1.json',HERE/'main_v1.gd',HERE/'main_v1.tscn',OLD/'runner_v1.gd',OLD/'main_v1.gd',OLD/'generation-gap-v1.json',HERE.parent/'batch30_runtime/block_draw_v1.gd',*[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn']],HERE.parents[2]/'map_directed/block_grid/contracts.py',HERE.parents[2]/'creative-production/batch30/map-constraint-source-v3/source-index.json',HERE.parents[2]/'creative-production/batch30/block-next-ideas-v2.json']
CONTROLS=[(.5,880),(.6,880),(.5,896),(.6,896)]

def seek(x):return cmd('settle',target_x=x,deadband=4)
def reach(x,side):return wait_x(x-side*6,side)
def pause(n=8):return[ground(),cmd('wait',n)]

def outbound(control=0):
 dx,rx=CONTROLS[control];dy=math.sqrt(1-dx*dx)
 plan=[seek(300),reach(300,1),*pause(8)]
 for takeoff,landing in [(300,576),(660,rx),(928,1136)]:
  if takeoff!=300:plan +=[seek(takeoff),reach(takeoff,1),*pause(6)]
  plan +=[seek(landing),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-dx,dy]),reach(landing,1),*pause(12 if landing==rx else 8)]
 # Pillar160 to bank352 is a real192drop across64gap, not another climb.
 plan +=[seek(1512),reach(1512,1),*pause(20)]
 return plan

def lower_return():
 return[seek(1328),reach(1328,-1),*pause(6),cmd('shoot',aim_cell=dict(kind='bell',id='fold-pair',receiver='access')),seek(1216),reach(1216,-1),*pause(2),seek(24),cmd('jump'),cmd('jump_release',20),reach(24,-1),*pause(20)]

def geometry(control=0):
 if control not in range(4):raise ValueError('outside fixed4control domain')
 c=base('N08');c['platforms']=[[0,736,320,96],[800,352,192,96],[1056,160,160,384],[1280,352,256,96],[1184,736,352,64],[256,736,352,64],[96,1248,1344,40],[96,1056,160,32],[256,864,160,32],[1248,1056,192,32],[1120,864,192,32]]
 c['latches']=[dict(id='fold-pair',bell=[400,648],gate=[448,544,256,24],paired_gate=[608,736,512,24],initial_open='B',return_access=[1420,268])]
 a=[24,718];b=[1512,334];c['ports']=[dict(id='A',position=a,normal=[-1,0],support_index=0),dict(id='B',position=b,normal=[1,0],support_index=3)]
 c['block_ports']={'A':block_port('A',[0,5],'W',a),'B':block_port('B',[11,2],'E',b)};c['block_reservations']=[[0,0,1536,1408]]
 proj=declare(dict(case=c,ports=c['block_ports'],action_clearance=c['block_reservations']),[(x,y)for x in range(12)for y in range(11)]);assert not validate(proj),validate(proj);c['block_grid']=proj['block_grid']
 c['reward_sites']=[dict(id='upper-cache',position=[896,334],region=[866,328,60,12],amount=16)]
 c.update(family=RECIPES[0],production_recipe=RECIPES[0],interface=0,world_bounds=[-256,-256,2048,1920],trace_all=False,max_frames=2400,layout_title='折页回廊：取奖走上层，回来看见下桥',idea_ids=['B31-N08'],native_scene='res://prototype/creative_batches/batch30_blockn08/main_v1.tscn',native_block_scene=str(NATIVE_SCENE.relative_to(HERE.parents[3])))
 c['rule_parameters']=dict(control=control,upper_shot_dx=CONTROLS[control][0],reward_stop=CONTROLS[control][1],nominal_ascents=[192,192,192],parent_failed_C09_not_inherited=True)
 c['layout_uid']=digest({k:c.get(k)for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['generation_rule']=dict(id='B31-N08/block-native-folded-return',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),source_map_contract='862b736c491502ae9934265bc7415805b4c122b9',parameters=c['rule_parameters'])
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='B31-N08/reward-return-interface0',source_type='explicit_derived_reward_return_demand_notrewardfreeMap',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],roles=['reward','return'],physical_layout_sha256=c['layout_uid'],new_gameplay_family=False,core='Upperbridge andoneactual16coinclaim outbound, sameworldlowerbridgeactualsupportreturn; alternateupperreturncostmeasurednotforbidden'),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='A',to_port='B',role='reward'),dict(from_port='B',to_port='A',role='return')],space=dict(block_size=128,max_width=1536,max_height=1408,max_port_span_x=1536,port_profiles=['ground64/v1']),boundary_policy='open',enclosing_walls=False,rewards=[dict(id='upper-cache',amount=16)],risk_reward=dict(amount=16,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='OriginalsupportedAorBinternaldock; originalpairupperclosed/loweropen. FreshBhas0coins/unclaimedbox anddoesnotclaimearnedrewardstate.',exit='Observedstableactualdock. SameworldA->reward->B->Arequiresseparatelyboundloopfixture.'),return_conditions='A->B/freshB->A onlystandarddirections. Continuousrewardloop separatelyverified; otherstate/recovery/boundary/MapUNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
 return c

def candidate(control=0,route='loop'):
 c=geometry(control);a=c['ports'][0]['position'];b=c['ports'][1]['position'];loop=route=='loop';back=route=='back'
 if route not in ['out','back','loop']:raise ValueError('unregisteredN08canonical')
 c['id']=f'b31-blockn08-v1-i0-{route}-c{control}';c['spawn']=(b if back else a)[:];c['entry_port']=c['spawn'][:]
 # Original definition requires two distinct valid static markers. The loop is
 # an explicit non-exported fixture: definitionexitB, actualgoal/endA.
 c['exit_port']=(a if back else b)[:];end=a if loop or back else b;c['goal']=[end[0]-7,end[1]-4,14,8]
 c['control_plan']=([]if back else outbound(control))+([]if route=='out'else lower_return())
 c['expected_reward']=0 if back else 16;c['required_rewards']=[]if back else['upper-cache']
 c['route_spec']=dict(id={'out':'reward-outbound','back':'lower-return','loop':'continuous-reward-loop'}[route],from_port='B'if back else'A',to_port='A'if back or loop else'B',role='return'if back else'reward',via_ports=['B']if loop else[],require_bell=route!='out',required_rewards=c['required_rewards'])
 c['fixture_kind']='same-world-A-B-A'if loop else'original-direction';c['actual_end_port']='A'if back or loop else'B';c['exportable_standard_route']=not loop
 return c


def visits(fs,x,y,after=-1):
 return[f for f in fs if f['frame']>after and f.get('grounded')and abs(f['x']-x)<=7 and abs(f['y']-y)<=1 and abs(f.get('vx',0))<=1]

def purpose(c,r):
 fs=r.get('frames',[]);why=[];back=c['route_spec']['from_port']=='B';loop=c.get('fixture_kind')=='same-world-A-B-A';claims=[e for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')and e.get('id')=='upper-cache'];coins=r.get('workshop',{}).get('coins',0)
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if r.get('returns'):why.append('world_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if(back and(coins!=0 or claims))or(not back and(coins!=16 or len(claims)!=1)):why.append('actual_one_reward_transaction_missing_or_wrong')
 bvis=visits(fs,1512,334);atb=bvis[0]['frame']if bvis else -1
 if not back and len(bvis)<12:why.append('actual_B_stable_visit_missing')
 upper=[f for f in fs if f.get('grounded')and f.get('support_id')=='PairGateA_fold-pair'and(not claims or f['frame']<claims[0]['frame'])]
 if not back and not upper:why.append('actual_upper_bridge_before_reward_missing')
 pair=next((p for p in r.get('workshop',{}).get('paired_gates',[])if p.get('id')=='fold-pair'),{});switches=[e for e in pair.get('events',[])if e.get('type')=='pair_switch'];after=atb if loop else-1
 lower=[f for f in fs if f['frame']>after and f.get('grounded')and f.get('support_id')=='PairGateB_fold-pair'and f.get('shot_charges')==1 and f.get('jumps_used')==0]
 if loop or back:
  if len(lower)<12:why.append('actual_lower_bridge_support_refill_missing')
  if not any(e.get('open')=='A'and e['frame']>after for e in switches):why.append('actual_lower_exchange_after_B_missing')
  av=visits(fs,24,718,after)
  if len(av)<12:why.append('actual_A_return_stable_missing')
 else:av=[]
 owned=set(map(tuple,c['block_grid']['cells']));outside=[]
 for a,b in zip(fs,fs[1:]):
  if not raster([min(a['x'],b['x'])-12,min(a['y'],b['y'])-18,abs(a['x']-b['x'])+24,abs(a['y']-b['y'])+36])<=owned:outside.append(b['frame'])
 if outside:why.append('actual_body_left_frozen_ownership')
 return dict(ok=not why,reasons=why,causal=dict(B_first_stable=atb,B_stable_frames=len(bvis),A_return_first_stable=av[0]['frame']if av else None,A_return_stable_frames=len(av),upper_support_frames=len(upper),lower_support_frames=len(lower),first_lower_support=({k:lower[0].get(k)for k in ['frame','x','y','support_id','shot_charges','jumps_used','energy']}if lower else None),pair_switches=switches,reward_claims=claims,coins=coins,outside_body_sweep_frames=outside[:20],fixture_definition_exit_is_not_actual_end=loop),behavior={k:r.get(k)for k in ['shots','jumps','ticks']})
