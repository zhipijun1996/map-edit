"""Block128 terminal adaptation of actual C01; original actors and paired Cell."""
import copy,json,math
from pathlib import Path
from pcg.map_directed.block_grid.contracts import anchor,raster,regions,connected
from pcg.prototype.creative_batches.batch30_c01 import api_v1 as parent_api
from pcg.prototype.creative_batches.batch30_c01 import rules_v3 as parent_rules
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
PCG=HERE.parents[2]
RECIPES=parent_api.RECIPES
RUNNER_SCRIPT=parent_api.RUNNER_SCRIPT
NATIVE_SCENE='res://prototype/creative_batches/batch30_blockbridge/main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(parent_api.__file__),*parent_api.SOURCE_DEPENDENCIES,Path(parent_rules.__file__),HERE/'protocol-v1.json',HERE/'source-reservation-v1.json',HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE/'overlay_v1.gd',PCG/'map_directed/block_grid/contracts.py',PCG/'map_directed/block_grid/plains-policy.json']
SEED=json.loads((HERE/'source-reservation-v1.json').read_text())

def rows(cells):
 out=[]
 for y in sorted({y for x,y in cells}):
  xs=sorted(x for x,yy in cells if yy==y)
  if not xs:continue
  start=prior=xs[0]
  for x in xs[1:]:
   if x==prior+1:prior=x;continue
   out.append([start*128,y*128,(prior-start+1)*128,128]);start=prior=x
  out.append([start*128,y*128,(prior-start+1)*128,128])
 return out

def candidate(interface=0,control=0):
 if interface not in [0,1]or control not in [0,1]:raise ValueError('outside registered BlockBridge domains')
 c=copy.deepcopy(parent_rules.candidate(interface,control));source_id=c['id'];dy=-86
 def pt(p):return[p[0],p[1]+dy]
 def rect(p):return[p[0],p[1]+dy,*p[2:]]
 c['platforms']=[rect(p)for p in c['platforms']]
 for k in ['hazards']:c[k]=[rect(p)for p in c.get(k,[])]
 for l in c.get('latches',[]):
  l['bell']=pt(l['bell']);l['gate']=rect(l['gate']);l['paired_gate']=rect(l['paired_gate'])
  if l.get('return_access'):l['return_access']=pt(l['return_access'])
 for p in c['ports']:p['position']=pt(p['position'])
 for s in c['reward_sites']:s['position']=pt(s['position']);s['region']=rect(s['region'])
 if c.get('world_bounds'):c['world_bounds']=rect(c['world_bounds'])
 edits=[];block_ports={}
 for p in c['ports']:
  idx=p['support_index'];r=c['platforms'][idx];before=r[:];old_y=p['position'][1];wanted=round((old_y-78)/128)*128+78;delta=wanted+18-r[1]
  if abs(delta)>32:raise ValueError('needs_design: terminal_height_exceeds32/'+p['id'])
  bottom=r[1]+r[3];r[1]+=delta;r[3]=bottom-r[1]
  x=p['position'][0];normal=p['normal'][0];face=math.floor((x-24)/128)*128 if normal<0 else math.ceil((x+24)/128)*128
  old_left,old_right=r[0],r[0]+r[2]
  if normal<0:r[0]=face;r[2]=old_right-face
  else:r[2]=face-r[0]
  if r[2]<24 or old_left-r[0]>32 or r[0]+r[2]-old_right>32:raise ValueError('needs_design: terminal_extension_exceeds32/'+p['id'])
  dock=[face-normal*24,wanted];p['position']=dock
  cell=[int(face/128)if normal<0 else int(face/128)-1,int((wanted-78)/128)];edge='W'if normal<0 else'E';point=anchor(cell,edge)
  grid=dict(cell=cell,edge=edge,profile='ground64/v1',stagingPosition=dock)
  block_ports[p['id']]=dict(position=point,normal=p['normal'][:],grid=grid,crossing_offset=[0,14],aperture=[point[0]-32,point[1]-32,64,64])
  edits.append(dict(port=p['id'],support_index=idx,before=before,after=r[:],bank_top_delta=delta,original_body_y=old_y,new_dock=dock))
  for s in c['reward_sites']:
   if before[0]<=s['position'][0]<=before[0]+before[2]and abs(s['position'][1]+18-before[1])<1:
    s['position'][1]+=delta;s['region'][1]+=delta
 a=next(p for p in c['ports']if p['id']=='A')['position'];b=next(p for p in c['ports']if p['id']=='B')['position']
 # Original input sequence is reached by real supported movement, never a
 # transform/resource reset. No persistent settle is inserted before source.
 prefix=[cmd('axis',value=1),wait_x(80),cmd('axis',value=0),ground(),cmd('wait',8)]
 c['control_plan']=prefix+c['control_plan'];c['control_plan'][-1]['target_x']=b[0]
 c.update(id=f'b30-blockbridge-v1-i{interface}-c{control}',spawn=a[:],entry_port=a[:],exit_port=b[:],goal=[b[0]-7,b[1]-4,14,8],max_frames=1200,native_scene=NATIVE_SCENE)
 c['rule_parameters'].update(block_size=128,source_case_id=source_id,source_translation=[0,dy],old_bridge=c['latches'][0]['gate'],new_bridge=c['latches'][0]['paired_gate'],terminal_adaptations=edits,actual_core_entry=[80,334],owner_margin_pixels=32)
 body_cells=set(map(tuple,SEED['interfaces'][str(interface)]['source_body_cells']));margin_cells=set(map(tuple,SEED['interfaces'][str(interface)]['owner_margin_cells']))
 extra=[l['paired_gate']for l in c['latches']]+[[s['position'][0]-18,s['position'][1]-18,36,36]for s in c['reward_sites']]+[[p['position'][0]-12,p['position'][1]-18,24,36]for p in c['ports']]
 physical=set()
 for region in regions(dict(case=c,action_clearance=[]))+extra:physical |= raster(region)
 forbidden={(p['grid']['cell'][0]+p['normal'][0],p['grid']['cell'][1]+p['normal'][1])for p in block_ports.values()}
 if (physical|body_cells)&forbidden:raise ValueError('needs_design: actual geometry/source body occupies external Port neighbor')
 cells=physical|body_cells|(margin_cells-forbidden)
 if not connected(cells):raise ValueError('needs_design: reservation disconnected without cutting recovery')
 c['block_reservations']=extra+rows(body_cells)
 c['block_ports']=block_ports
 c['block_grid']=dict(schema='map-notes/block-grid/v1',size=128,origin=[0,0],cells=sorted(map(list,cells)),port_bindings=[dict(port_id=k,**p['grid'])for k,p in block_ports.items()],occupancy_coverage='All original terrain including recovery, both actual gates, interactions and source-seeded conservative action ownership',action_coverage='partial; new actual body sweeps checked separately; no generic input guarantee',source_map_commit='a685faebdb7596b0808538ab9ef299d6455d2320')
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_ports','block_grid']})
 c['layout_title']='Block128换脚桥 / '+('横向断拱'if interface==0 else'紧凑升层')
 c['generation_rule']=dict(id='batch30/blockbridge',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'],source_parent='batch30/C01/v3',upstream_map_commit='a685faebdb7596b0808538ab9ef299d6455d2320')
 c['map_specification']=specification(interface,c)
 return c

def specification(interface,c):
 size=c['block_grid']['size'];xs=[v[0]for v in c['block_grid']['cells']];ys=[v[1]for v in c['block_grid']['cells']]
 return dict(schema='map-notes/challenge-specification/v1',id=f'block-demand/C01/{interface}',source_type='map_contract_driven_adaptation',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=interface,physical_layout_sha256=c['layout_uid'],core='same airborne original shot removes actual launch support A and creates first landing support B, then real ground renewal and onward jump',map_constraint_source='a685faebdb7596b0808538ab9ef299d6455d2320',independent_new_family_claim=False),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[p['normal']for p in c['ports']],block_profiles=['ground64/v1']),relations=[dict(from_port='A',to_port='B',role='main',route_id='support-swap')],space=dict(block_size=size,block_dimensions=[max(xs)-min(xs)+1,max(ys)-min(ys)+1],max_width=(max(xs)-min(xs)+1)*size,max_height=(max(ys)-min(ys)+1)*size,boundary_policy='open',ownership_shape='Explicit4connected true cells, not a rectangular outer wall'),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='Original supported fresh A dock; actual walk reaches original sequence start, no transform/resource writes',exit='Only observed stable B dock and real chest. Boundary anchor is distinct, arbitrary entry/continuation UNKNOWN'),return_conditions='All old recovery terrain retained. New exact failure-recovery fixture still requires validation; B->A and generic boundary crossing UNKNOWN',budget=dict(generator_candidates=2,director_revisions=0))

def purpose(c,r):
 q=parent_rules.purpose(c,r);cells=set(map(tuple,c['block_grid']['cells']));outside=[]
 for f in r.get('frames',[]):
  if not raster([f['x']-12,f['y']-18,24,36])<=cells:outside.append(dict(frame=f['frame'],body=[f['x']-12,f['y']-18,24,36]))
 first=q.get('causal',{}).get('first_shot_frame',-1)
 entered=any(f.get('grounded')and f['frame']<first and abs(f['x']-80)<=12 and abs(f['y']-334)<1 for f in r.get('frames',[]))
 if not entered:q['reasons'].append('real_walk_to_original_core_entry_missing')
 if outside:q['reasons'].append('actual_complete_body_outside_frozen_block_ownership')
 q['causal'].update(block_body_outside=outside[:8],outside_body_frames=len(outside),real_original_entry_observed=entered,staging_scope='Exact local dock witness only; boundary crossing UNKNOWN')
 q['ok']=not q['reasons'];return q
