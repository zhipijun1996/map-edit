"""Human A1 two real spaces, explicit independently verified ordered controls."""
import copy,json,math
from pathlib import Path
from pcg.prototype.workshop import rules as source
from pcg.prototype.workshop import evaluate as original
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.map_directed.block_grid.contracts import anchor,declare,regions,raster,validate
from pcg.map_directed.content_domains.reservation import connect
from pcg.prototype.factory.core.quality import digest
from .clearance_v1 import inspect as inspect_clearance
HERE=Path(__file__).parent
RECIPES=('block128-human-A1-bidirectional',)
RUNNER_SCRIPT=HERE.parents[1]/'workshop/runner.gd'
NATIVE_SCENE='res://prototype/creative_batches/batch30_blocka1/main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(source.__file__),Path(original.__file__),HERE.parents[1]/'workshop/transitions.py',HERE.parents[1]/'workshop/ideas.json',HERE/'source-baseline-v1.json',HERE/'map-input-v1.json',HERE/'protocol-v1.json',HERE/'clearance_v1.py',HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_runtime/block_draw_v1.gd',HERE.parents[2]/'map_directed/block_grid/contracts.py',HERE.parents[2]/'map_directed/content_domains/reservation.py']
RETURN=[(40,6,10,.15),(32,8,8,.15),(48,6,10,.25),(24,8,8,.05)]

def candidate(interface=0,control=0,route='outbound'):
 if interface not in [0,1]or route not in ['outbound','return']or control not in range(4):raise ValueError('outside_registered_A1_domain')
 c=copy.deepcopy(source.thorn(interface));dx=32*interface;dy=-86
 def rect(r):return[r[0]+dx,r[1]+dy,*r[2:]]
 c['platforms']=[rect(r)for r in c['platforms']]
 p=c['platforms'][0];end=p[0]+p[2];p[0]=0;p[2]=end
 face=640 if interface==0 else 768;r=c['platforms'][1];before=r[:];bottom=r[1]+r[3];r[1]=352;r[3]=bottom-r[1];r[2]=face-r[0]
 assert abs(r[1]-before[1])<=32 and max(0,face-before[0]-before[2])<=32
 c['ports']=[dict(id='A',position=[24,334],normal=[-1,0],support_index=0),dict(id='B',position=[face-24,334],normal=[1,0],support_index=1)]
 for s in c['reward_sites']:s['position']=[face-24,334];s['region']=[face-49,329,50,10]
 if route=='outbound':
  plan=[cmd('axis',value=1),wait_x(80+dx),cmd('axis',value=0),ground(),cmd('wait',8)]+source.launch(takeoff=205+dx)+[settle(face-24,6)];start=[24,334];target=[face-24,334];fromid='A';toid='B'
 else:
  offset,release,shot,down=RETURN[control];plan=[cmd('axis',value=-1),wait_x(r[0]+offset,-1),cmd('jump'),cmd('jump_release',release),cmd('shoot',shot,direction=[math.sqrt(1-down*down),down]),settle(24,6)];start=[face-24,334];target=[24,334];fromid='B';toid='A'
 c.update(id=f'b30-blocka1-v1-i{interface}-{route}-c{control}',family=RECIPES[0],capabilities=['move','jump','shot_recoil'],spawn=start,entry_port=start[:],exit_port=target,goal=[target[0]-7,330,14,8],control_plan=plan,max_frames=1400,trace_all=False,interface=interface,production_recipe=RECIPES[0],challenge_route=True,expected_reward=8 if route=='outbound'else 0,required_rewards=['visible-cache']if route=='outbound'else[],idea_ids=['human-A1-thorn-slot'],native_scene=NATIVE_SCENE,native_block_scene=str((HERE/'main_v1.tscn').relative_to(HERE.parents[3])))
 c['route_spec']=dict(id=route,from_port=fromid,to_port=toid,role='reward'if route=='outbound'else'return',via_ports=[],require_bell=False,required_rewards=c['required_rewards'])
 ports={}
 for p,cell,edge in zip(c['ports'],[[0,2],[face//128-1,2]],['W','E']):
  point=anchor(cell,edge);ports[p['id']]=dict(position=point,normal=p['normal'],grid=dict(cell=cell,edge=edge,profile='ground64/v1',stagingPosition=p['position']),crossing_offset=[0,14],aperture=[point[0]-32,point[1]-32,64,64])
 reserves=[[12,176,face-36,478]];extra=[[face-42,316,36,36]]
 allregions=regions(dict(case=c,action_clearance=reserves))+extra;cells=set().union(*(raster(v)for v in allregions));cells,air=connect(cells,ports)
 m=declare(dict(case=c,ports=ports,action_clearance=reserves),cells);errors=validate(m)
 if errors:raise ValueError('blockA1static/'+','.join(errors))
 c['block_grid']=m['block_grid'];c['block_ports']=ports;c['block_reservations']=reserves+extra
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','thorns','reward_sites','block_grid','block_ports']})
 c['layout_title']='A1 尖刺窄通道 / '+('五格岸口'if interface==0 else'六格斜口')
 c['rule_parameters']=dict(interface=interface,control=control,route=route,source='originalhumanA1thorn-'+str(interface),translation=[dx,dy],slot_body=[24,36],internal_slot_scaled=False,retained_recovery_bank=4,terminal_B_top_delta=r[1]-before[1],terminal_B_outward_extension=max(0,face-before[0]-before[2]),visible_currency=8,port_span_blocks=face//128)
 c['generation_rule']=dict(id='batch30/blockA1',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['map_specification']=specification(c)
 return c

def specification(c):
 return dict(schema='map-notes/challenge-specification/v1',id=f'block-demand/A1-bidirectional/risk-reward-{c["interface"]}',source_type='human_idea_and_current_Map_constraint_derived',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=c['interface'],physical_layout_sha256=c['layout_uid'],core='Real fullbody thornchannel recoil tovisible original8coin chest; independentlyvalidated return, not mirroredpromise',human_idea='human-A1-thorn-slot',actual_Map_reference='block-demand/r3',actual_Map_required_edge_pairs=[['e6','e7'],['e7','e6']],local_mapping_proposal=dict(A='e6',B='e7'),currency8_is_proposal_against_unknownvalue=True,independent_new_family_claim=False),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]],block_profiles=['ground64/v1']),relations=[dict(from_port=a,to_port=b,role=role,route_id=rid)for a,b,role,rid in [('A','B','reward','outbound'),('B','A','return','return')]],space=dict(block_size=128,max_width=1280,max_height=896,max_port_span_x=640 if c['interface']==0 else 768,boundary_policy='open',ownership_shape='connected_irregular_cells'),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites'],visible_currency_once=8,original_bottom_bank_preserved=True),resource_state=dict(reset_between_components=False,entry='FreshA/B grounded demonstrations separately. ReversefreshB maycollectchest; onlycontinuousfixtureprovesonce-only afteroutbound. Arbitraryclaimed/energy stateUNKNOWN',exit='Observed stableactualdock/resources; no genericensures'),return_conditions='Twoorderedlocalroutes requireownfullregular; sameworld A->B->A separatelyverifiedfixture. No boundarycrossing or genericMapreturn inference',budget=dict(generator_candidates=4,director_revisions=0))

def purpose(c,r):
 v=copy.deepcopy(c);v['family']='thorn-slot';q=original.purpose(v,r);legacy=copy.deepcopy(q['causal']);clearance=inspect_clearance(c,r)
 q['reasons']=[why for why in q['reasons']if why!='body_sweep_intersects_thorns']
 if clearance['swept_intersections']:q['reasons'].append('actual_complete_body_sweep_intersects_thorns')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in r.get('frames',[])if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:q['reasons'].append('actual_complete_body_outside_frozen_block_ownership')
 q['causal'].update(legacy_one_sided_observer=legacy,complete_2D_body_clearance=clearance,outside_body_frames=outside[:12],outside_count=len(outside),human_chest_motivation_retained=True)
 q['ok']=not q['reasons'];return q
