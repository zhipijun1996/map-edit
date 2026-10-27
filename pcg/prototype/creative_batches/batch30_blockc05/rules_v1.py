"""New Block-native three-port station rule; original moving carrier physics."""
import copy
from pathlib import Path
from pcg.prototype.creative_batches.batch30_c05 import rules_v3 as parent
from pcg.prototype.creative_batches.batch30_c05 import api_v1 as parent_api
from pcg.map_directed.block_grid.contracts import anchor,regions,raster,declare,validate
from pcg.map_directed.content_domains.reservation import connect
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.workshop.rules import cmd,wait_x,ground
HERE=Path(__file__).parent
RECIPES=('block128-moving-station-choice',)
RUNNER_SCRIPT=HERE.parent/'batch30_c05/runner_v1.gd'
NATIVE_SCENE='res://prototype/creative_batches/batch30_blockc05/main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(parent.__file__),Path(parent_api.__file__),*parent_api.SOURCE_DEPENDENCIES,HERE/'protocol-v1.json',HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_runtime/block_draw_v1.gd',HERE.parents[2]/'map_directed/block_grid/contracts.py',HERE.parents[2]/'map_directed/content_domains/reservation.py']


def candidate(interface=0,control=0,route='near'):
 if interface!=0:raise ValueError('needs_design: old highcourt near route failed; no partial fork substitution')
 c=copy.deepcopy(parent.candidate(0,control,route));dy=21
 def pt(p):return[p[0],p[1]+dy]
 def rect(r):return[r[0],r[1]+dy,*r[2:]]
 c['platforms']=[rect(r)for r in c['platforms']]
 for l in c['latches']:
  l['bell']=pt(l['bell']);l['gate']=rect(l['gate'])
  if l.get('paired_gate'):l['paired_gate']=rect(l['paired_gate'])
 for m in c['moving_platforms']:m['start']=pt(m['start']);m['finish']=pt(m['finish'])
 for s in c['reward_sites']:s['position']=pt(s['position']);s['region']=rect(s['region'])
 if c.get('world_bounds'):c['world_bounds']=rect(c['world_bounds'])
 targets={'A':([0,4],'W',[24,590],608),'B':([1,2],'W',[152,334],352),'C':([9,1],'E',[1256,206],224)}
 ports={};edits=[]
 for p in c['ports']:
  cell,edge,dock,top=targets[p['id']];r=c['platforms'][p['support_index']];before=r[:];bottom=r[1]+r[3];point=anchor(cell,edge)
  r[1]=top;r[3]=bottom-top
  if edge=='W':end=r[0]+r[2];r[0]=point[0];r[2]=end-r[0]
  else:r[2]=point[0]-r[0]
  if r[3]<=0 or r[2]<=24:raise ValueError('newterminalinvalid')
  p['position']=dock[:];ports[p['id']]=dict(position=point,normal=p['normal'],grid=dict(cell=cell,edge=edge,profile='ground64/v1',stagingPosition=dock[:]),crossing_offset=[0,14],aperture=[point[0]-32,point[1]-32,64,64])
  edits.append(dict(port=p['id'],before=before,after=r[:],top_delta=top-before[1],new_rule_exceeds32=abs(top-before[1])>32))
 for s,pid in zip(c['reward_sites'],['B','C']):
  dock=targets[pid][2];s['position']=dock[:];s['region']=[dock[0]-25,dock[1]-5,50,10]
 target=targets[c['route_spec']['to_port']][2];start=targets['A'][2]
 prefix=[cmd('axis',value=1),wait_x(80),cmd('axis',value=0),ground(),cmd('wait',8)]
 c['control_plan']=prefix+c['control_plan'];c['control_plan'][-1]['target_x']=target[0]
 c.update(id=f'b30-blockc05-v1-i0-{route}-c{control}',family=RECIPES[0],production_recipe=RECIPES[0],spawn=start[:],entry_port=start[:],exit_port=target[:],goal=[target[0]-7,target[1]-4,14,8],max_frames=1800,native_scene=NATIVE_SCENE,native_block_scene=str((HERE/'main_v1.tscn').relative_to(HERE.parents[3])))
 # Authored conservative action ownership. These rectangles add no physical
 # terrain and do not prove arbitrary actions or boundary crossing.
 reserves=[[12,560,240,110],[180,-80,1090,860],[128,180,550,250],[-110,750,1510,210]]
 extra=[l['paired_gate']for l in c['latches']if l.get('paired_gate')]+[[s['position'][0]-18,s['position'][1]-18,36,36]for s in c['reward_sites']]
 physical=regions(dict(case=c,action_clearance=reserves))+extra
 cells=set().union(*(raster(r)for r in physical));cells,air=connect(cells,ports)
 module=declare(dict(case=c,ports=ports,action_clearance=reserves),cells)
 errors=validate(module)
 if errors:raise ValueError('blockc05_static/'+','.join(errors))
 c['block_grid']=module['block_grid'];c['block_ports']=ports;c['block_reservations']=reserves+extra
 c['block_adaptation']=dict(geometry_class='NEW_BLOCK_RULE_NOT_BOUNDED_TERMINAL_ADAPTER',translation=[0,21],terminal_edits=edits,deleted_recovery_indices=[],new_physical_platforms=0,internal_geometry_scaled=False,reservation_air_cells=air,source_physics_inherited=False)
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites','block_grid','block_ports']})
 c['layout_title']='Block128 追台择岸 / 回折西岸与继续高东岸'
 c['generation_rule']=dict(id='batch30/blockC05',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['block_adaptation'])
 c['rule_parameters']['block_rule']=c['block_adaptation']
 c['map_specification']=specification(c)
 return c


def specification(c):
 cells=c['block_grid']['cells'];xs=[p[0]for p in cells];ys=[p[1]for p in cells]
 return dict(schema='map-notes/challenge-specification/v1',id='block-demand/C05/wide-newrule',source_type='task_a_derived_current_Map_contract_demand',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=0,physical_layout_sha256=c['layout_uid'],junction_role='fork',core='One real moving-carrier decision process: earlier upper-west roof transfer versus later higher-east paired-gate shot departure',request_not_upstream_B_graph=True,independent_new_family_claim=False),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=3,required_normals=[[-1,0],[-1,0],[1,0]],block_profiles=['ground64/v1']),relations=[dict(from_port='A',to_port=to,role='main',route_id=route)for route,to in [('near','B'),('far','C')]],space=dict(block_size=128,max_width=(max(xs)-min(xs)+1)*128,max_height=(max(ys)-min(ys)+1)*128,boundary_policy='open',ownership_shape='connected_polyomino'),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites'],near='10coin roofwest branch',far='16coin high east branch',recovery='Original lower banks internal; no extra mapport'),resource_state=dict(reset_between_components=False,entry='Same supported fresh A dock and parked real carrier; near-open/far-closed initial pair shared across routes',exit='Observed stable selected dock and actual selected chest; arbitrary entry, carrier phase/state transfer UNKNOWN'),return_conditions='All reverse ordered pairs, actual boundary crossing and Map assembly UNKNOWN; failure fixtures separate',budget=dict(generator_candidates=4,director_revisions=0))


def purpose(c,r):
 q=parent.purpose(c,r);owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in r.get('frames',[])if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:q['reasons'].append('actual_complete_body_outside_frozen_block_ownership')
 q['causal'].update(outside_body_frames=outside[:12],outside_count=len(outside),all_reverse_and_boundary_crossing='UNKNOWN')
 q['ok']=not q['reasons'];return q
