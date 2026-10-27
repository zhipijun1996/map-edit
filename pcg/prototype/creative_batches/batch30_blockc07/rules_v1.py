"""Bounded terminal adaptation of the real original C07 collision-brake core."""
import copy
from pathlib import Path
from pcg.prototype.creative_batches.batch30_c07 import rules_v3 as parent
from pcg.prototype.creative_batches.batch30_c07 import api_v1 as source
from pcg.map_directed.block_grid.contracts import anchor,raster,regions,declare,validate
from pcg.map_directed.content_domains.reservation import connect
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('block128-new-wall-collision-brake',)
RUNNER_SCRIPT=source.RUNNER_SCRIPT
NATIVE_SCENE='res://prototype/creative_batches/batch30_blockc07/main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(parent.__file__),Path(source.__file__),*source.SOURCE_DEPENDENCIES,HERE/'protocol-v1.json',HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_runtime/block_draw_v1.gd',HERE.parents[2]/'map_directed/block_grid/contracts.py',HERE.parents[2]/'map_directed/content_domains/reservation.py']

def candidate(interface=0,control=0):
 if interface!=0:raise ValueError('needs_design: original C07 vertical interface fails; no secondspace claimed')
 c=copy.deepcopy(parent.candidate(0,control));dy=-57
 def pt(p):return[p[0],p[1]+dy]
 def rect(r):return[r[0],r[1]+dy,*r[2:]]
 c['platforms']=[rect(r)for r in c['platforms']]
 for l in c['latches']:l['bell']=pt(l['bell']);l['gate']=rect(l['gate']);l['paired_gate']=rect(l['paired_gate'])
 for s in c['reward_sites']:s['position']=pt(s['position']);s['region']=rect(s['region'])
 if c.get('world_bounds'):c['world_bounds']=rect(c['world_bounds'])
 edits=[];ports={}
 for p in c['ports']:
  r=c['platforms'][p['support_index']];before=r[:];end=r[0]+r[2];bottom=r[1]+r[3]
  if p['id']=='A':cell=[0,0];edge='W';dock=[24,78];r[0]=0;r[2]=end;r[1]=96
  else:cell=[5,3];edge='E';dock=[744,462];r[2]=768-r[0];r[1]=480
  r[3]=bottom-r[1];p['position']=dock[:];point=anchor(cell,edge)
  ports[p['id']]=dict(position=point,normal=p['normal'],grid=dict(cell=cell,edge=edge,profile='ground64/v1',stagingPosition=dock[:]),crossing_offset=[0,14],aperture=[point[0]-32,point[1]-32,64,64])
  edits.append(dict(port=p['id'],before=before,after=r[:],shore_top_delta=r[1]-before[1]))
 assert max(abs(e['shore_top_delta'])for e in edits)<=32
 for s in c['reward_sites']:s['position']=[744,462];s['region']=[719,457,50,10]
 prefix=[cmd('axis',value=1),wait_x(100),cmd('axis',value=0),ground(),cmd('wait',8)]
 c['control_plan']=prefix+c['control_plan'];c['control_plan'][-1]['target_x']=744
 c.update(id=f'b30-blockc07-v1-i0-c{control}',family=RECIPES[0],production_recipe=RECIPES[0],spawn=[24,78],entry_port=[24,78],exit_port=[744,462],goal=[737,458,14,8],max_frames=1400,challenge_route=True,native_scene=NATIVE_SCENE,native_block_scene=str((HERE/'main_v1.tscn').relative_to(HERE.parents[3])))
 reserves=[[12,60,228,100],[180,-80,570,850]];extra=[l['paired_gate']for l in c['latches']]+[[726,444,36,36]]
 allregions=regions(dict(case=c,action_clearance=reserves))+extra;cells=set().union(*(raster(r)for r in allregions));cells,air=connect(cells,ports)
 module=declare(dict(case=c,ports=ports,action_clearance=reserves),cells);errors=validate(module)
 if errors:raise ValueError('blockC07static/'+','.join(errors))
 c['block_grid']=module['block_grid'];c['block_ports']=ports;c['block_reservations']=reserves+extra
 c['block_adaptation']=dict(translation=[0,-57],terminal_edits=edits,retained_recovery_indices=[3,4,5,6],deleted_physical_indices=[],new_physical_platforms=0,source_physics_inherited=False,reservation_air_cells=air)
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['layout_title']='Block128 关墙接住反冲 / 横向刹车袋'
 c['generation_rule']=dict(id='batch30/blockC07',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['block_adaptation'])
 c['map_specification']=specification(c)
 return c

def specification(c):
 cells=c['block_grid']['cells'];xs=[p[0]for p in cells];ys=[p[1]for p in cells]
 return dict(schema='map-notes/challenge-specification/v1',id='block-demand/C07/horizontal',source_type='task_a_derived_current_Map_contract_demand',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=0,physical_layout_sha256=c['layout_uid'],core='Samefallingshot builds actual collisionbrake, then efficient pocket/onwardreward route; actual paid extra-groundjump alternatives allowed',independent_new_family_claim=False,canonical_pair=dict(open_a=True,open_b=False),alternative_pair_states=[dict(open_a=True,open_b=False),dict(open_a=False,open_b=True)]),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]],block_profiles=['ground64/v1']),relations=[dict(from_port='A',to_port='B',role='main',route_id='brake')],space=dict(block_size=128,max_width=(max(xs)-min(xs)+1)*128,max_height=(max(ys)-min(ys)+1)*128,boundary_policy='open',ownership_shape='connected_polyomino'),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites'],pocket='internalcollisiontransfer',recovery_steps='retained; newbodyownership recovery proof required'),resource_state=dict(reset_between_components=False,entry='Original fresh supported A dock, frontgate closed/backbrake open',exit='Observed stableB and real12coin; nominalfrontopen/backbrakeclosed, costedalternatives report actualstates; generictransferUNKNOWN'),return_conditions='B->A, boundarycrossing, rightstairs recovery and all seamsUNKNOWN until newexactevidence',budget=dict(generator_candidates=4,director_revisions=0))

def purpose(c,r):
 q=source.purpose(c,r);owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in r.get('frames',[])if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:q['reasons'].append('actual_complete_body_outside_frozen_block_ownership')
 q['causal'].update(outside_body_frames=outside[:12],outside_count=len(outside),boundary_crossing='UNKNOWN')
 q['ok']=not q['reasons'];return q
