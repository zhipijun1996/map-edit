"""Existing Motor collision projection; observations never grant success."""
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,validate,raster
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('wall-projection-unlock',)
RUNNER_SCRIPT=HERE/'runner_v1.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(__file__),*[HERE/n for n in ['protocol-v1.json','observe_v1.gd','runner_v1.gd','main_v1.gd','main_v1.tscn']],HERE.parent/'batch30_runtime/block_draw_v1.gd',HERE.parent/'batch30_blockpilot/rules_v1.py',HERE.parents[2]/'map_directed/block_grid/contracts.py',HERE.parents[2]/'creative-production/batch30/block-next-ideas-v4.json',HERE.parents[2]/'creative-production/batch30/map-constraint-source-v3/source-index.json']

def candidate(launch=596,hold=20):
 if launch not in [596,580,532,468] or hold not in [20,24]:raise ValueError('outsidepreregisteredN16domain')
 c=base('N16');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil']
 c['platforms']=[[0,608,608,96],[608,352,416,384],[128,864,768,48],[288,736,192,40]]
 c['latches']=[dict(id='wall-bell',bell=[520,568],gate=[848,0,24,352],open_seconds=0)]
 docks={'A':[24,590],'B':[1000,334]};ports={'A':block_port('A',[0,4],'W',docks['A']),'B':block_port('B',[7,2],'E',docks['B'])}
 c['ports']=[dict(id=k,position=docks[k][:],normal=ports[k]['normal'],support_index=i)for i,k in enumerate(['A','B'])];c['spawn']=docks['A'][:];c['entry_port']=docks['A'][:];c['exit_port']=docks['B'][:];c['goal']=[993,330,14,8]
 c['reward_sites']=[dict(id='crest-cache',position=[944,334],region=[920,328,48,12],amount=8)];c['required_rewards']=['crest-cache'];c['expected_reward']=8
 c['control_plan']=[cmd('axis',value=1),wait_x(launch),cmd('axis',value=0),ground(),cmd('wait',20),cmd('jump'),cmd('jump_release',hold),cmd('shoot',aim_cell=dict(kind='bell',id='wall-bell')),settle(1000),ground(),cmd('wait',20)]
 c.update(id=f'b31-blockn16-v1-i0-x{launch}-h{hold}',interface=0,max_frames=1300,trace_all=False,production_recipe=RECIPES[0],challenge_route=True,idea_ids=['B31-N16'],layout_title='贴壁，把斜反冲交给碰撞',native_scene='res://prototype/creative_batches/batch30_blockn16/main_v1.tscn',native_block_scene=str(NATIVE_SCENE.relative_to(HERE.parents[3])))
 c['route_spec']=dict(id='A-to-B',from_port='A',to_port='B',role='main',via_ports=[],require_bell=True,required_rewards=['crest-cache'])
 c['rule_parameters']=dict(launch=launch,hold=hold,wall_x=608,wall_top352=True,projection_observation_not_goal_predicate=True)
 proj=declare(dict(case=c,ports=ports,action_clearance=[]),[(x,y)for x in range(8)for y in range(8)]);assert not validate(proj),validate(proj);c['block_grid']=proj['block_grid'];c['block_ports']=ports;c['block_reservations']=[]
 c['layout_uid']=digest({k:c.get(k)for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['generation_rule']=dict(id='B31-N16/wall-collision-projection',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),source_map_contract='862b736c491502ae9934265bc7415805b4c122b9',parameters=c['rule_parameters'])
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='B31-N16/west-low-east-high-interface0',source_type='explicit_model_authored_interface_demand',region='plains',required_family=c['family'],objective=dict(recipe=RECIPES[0],physical_layout_sha256=c['layout_uid'],core='Originalsame-shotopensactualdoorandcrestswall;wallprojectionobservednotforcedcounterwords',new_family='UNKNOWN'),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port='A',to_port='B',role='main')],space=dict(block_size=128,max_width=1024,max_height=1024,max_port_span_x=1024,port_profiles=['ground64/v1']),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='ActualsupportedAoriginalfullresources;permanentdoorclosed',exit='ActualsupportedBdooropen/cacheonce;arbitrarytransferUNKNOWN'),return_conditions='Reverse/genericrecovery/seams/fullMapUNKNOWN;first8specificretryfixtureonly',budget=dict(generator_candidates=3,director_revisions=0))
 return c

def observations(c,r):
 fs=r.get('frames',[]);projected=[]
 for f in fs:
  n=f.get('n16',{});rv=n.get('recoil_velocity',[0,0]);wall=any(t.get('collider')=='Platform1' and t.get('normal',[0,0])[0]<-.7 for t in n.get('contacts',[]))
  if wall and n.get('burst_remaining',0)>0 and abs(rv[0])<1 and rv[1]<-100 and not f.get('grounded'):projected.append(f['frame'])
 shot=next((f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))),None)
 top=next((f for f in fs if f.get('grounded')and f.get('support_id')=='Platform1'),None)
 return dict(actual_projected_burst_wall_frames=projected,wall_projection_observed=bool(projected),first_shot={k:shot.get(k)for k in ['frame','x','y','vx','vy']}if shot else None,first_wall_top_support={k:top.get(k)for k in ['frame','x','y','shot_charges','jumps_used']}if top else None,maximum_whole_body_clearance_above_crest=352-min((f['y']+18 for f in fs),default=352))

def purpose(c,r):
 why=[];fs=r.get('frames',[])
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if r.get('returns'):why.append('world_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if 'crest-cache'not in {e['id']for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')}:why.append('actual_required_cache_missing')
 if not any(e.get('type')=='bell_open'and e.get('id')=='wall-bell'for e in r.get('plains',{}).get('events',[])):why.append('actual_high_gate_not_opened')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[b['frame']for a,b in zip(fs,fs[1:])if not raster([min(a['x'],b['x'])-12,min(a['y'],b['y'])-18,abs(a['x']-b['x'])+24,abs(a['y']-b['y'])+36])<=owned]
 if outside:why.append('actual_body_left_frozen_Block_ownership')
 obs=observations(c,r);obs['outside_body_sweep_frames']=outside[:20]
 return dict(ok=not why,reasons=why,causal=obs,behavior={k:r.get(k)for k in ['shots','jumps','ticks']})
