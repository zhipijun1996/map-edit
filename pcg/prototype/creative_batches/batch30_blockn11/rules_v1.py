"""Actual A4 same-face Block docks; mirror receives independent physics."""
import copy
from pathlib import Path
from pcg.prototype.workshop import rules as source
from pcg.prototype.workshop.rules import cmd,wait_x,settle
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,raster,regions,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('block128-underledge-brake-return',)
RUNNER_SCRIPT=HERE.parents[1]/'workshop/runner.gd';NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(source.__file__),HERE/'protocol-v1.json',HERE/'idea-source-v1.json',HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_runtime/block_draw_v1.gd']
def candidate(interface=0,width=75,control=0):
 if interface not in [0,1]or width not in [75,96]or control not in [0,1]:raise ValueError('outsideN11registered4candidates/interface')
 c=copy.deepcopy(source.brake(interface));mirror=interface==1;sign=-1 if mirror else 1;dx=70 if mirror else -70;dy=28
 def point(p):return[sign*p[0]+dx,p[1]+dy]
 def rect(r):return[(-r[0]-r[2]if mirror else r[0])+dx,r[1]+dy,r[2],r[3]]
 c['platforms']=[rect(r)for r in c['platforms']];c['world_bounds']=rect(c['world_bounds'])
 upper=c['platforms'][0];beforeA=upper[:];bottom=upper[1]+upper[3];upper[1]=224;upper[3]=bottom-224
 if not mirror:upper[2]+=upper[0]+256;upper[0]=-256
 else:upper[2]=256-upper[0]
 bag=c['platforms'][1];beforeB=bag[:];bottom=bag[1]+bag[3];bag[1]=480;bag[3]=bottom-480;bag[0]=-width if mirror else 0;bag[2]=width
 assert upper[3]>0 and bag[3]>0
 a=[232 if mirror else -232,206];b=[-24 if mirror else 24,462]
 ca=[1,1]if mirror else[-2,1];cb=[-1,3]if mirror else[0,3];edge='E'if mirror else'W';normal=[1,0]if mirror else[-1,0]
 ports={'A':block_port('A',ca,edge,a),'B':block_port('B',cb,edge,b)}
 c['ports']=[dict(id='A',position=a[:],normal=normal[:],support_index=0),dict(id='B',position=b[:],normal=normal[:],support_index=1)]
 c['spawn']=a[:];c['entry_port']=a[:];c['exit_port']=b[:];c['goal']=[b[0]-7,458,14,8]
 lip=upper[0]if mirror else upper[0]+upper[2];offset=([95,105]if mirror else[105,110])[control];shoot_x=lip+sign*offset
 c['control_plan']=[cmd('axis',value=sign),wait_x(shoot_x,sign),cmd('shoot',direction=[sign,0]),cmd('axis',value=-sign,after=9),settle(b[0],6)]
 for s in c['reward_sites']:
  s['position']=point(s['position']);s['position'][1]=462;s['region']=[s['position'][0]-30,457,60,10]
 c.update(id=f'b30-blockn11-v1-i{interface}-w{width}-c{control}',family=RECIPES[0],capabilities=['move','jump','shot_recoil'],interface=interface,production_recipe=RECIPES[0],challenge_route=True,max_frames=1500,trace_all=False,expected_reward=10,required_rewards=['visible-cache'],idea_ids=['B31-N11'],layout_title='同侧折返·反冲入檐袋 / '+('东向镜像'if mirror else'西向'),native_scene='res://prototype/creative_batches/batch30_blockn11/main_v1.tscn',native_block_scene=str(NATIVE_SCENE.relative_to(HERE.parents[3])))
 c['route_spec']=dict(id='A-to-B',from_port='A',to_port='B',role='main',via_ports=[],required_rewards=['visible-cache'],require_bell=False)
 reserves=[[-512 if mirror else 0,0,512,708]];m=dict(case=c,ports=ports,action_clearance=reserves);cells=set().union(*(raster(v)for v in regions(m)));m=declare(m,cells);assert not validate(m),validate(m)
 c['block_grid']=m['block_grid'];c['block_ports']=ports;c['block_reservations']=reserves
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','reward_sites','block_grid','block_ports']})
 c['rule_parameters']=dict(interface=interface,width=width,control=control,mirror=mirror,translation=[dx,dy],outward_sign=sign,upper_lip=lip,shoot_x=shoot_x,outward_offset=offset,upper_before=beforeA,upper_after=upper[:],bag_before=beforeB,bag_after=bag[:],original_floor=c['platforms'][2][:],retained_original_bottoms=True,bounded_shore_edits=dict(A_side_extension=26,A_top=16,B_outward_trim=25,B_top=14 if not mirror else -16,B_inward_extension=width-75))
 c['generation_rule']=dict(id='batch30/N11',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id='batch30/N11/'+('E-E'if mirror else'W-W')+'/width'+str(width),source_type='B_CSP_shape_demand_and_model_registered_A4_adaptation',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=interface,physical_layout_sha256=c['layout_uid'],sameface_offset_demand=True,independent_new_family_claim=False,mirror_requires_freshphysics=True),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[normal[:],normal[:]]),relations=[dict(from_port='A',to_port='B',role='main',route_id='A-to-B')],space=dict(block_size=128,max_width=1408,max_height=768,max_port_span_x=256,port_profiles=['ground64/v1']),boundary_policy='open',enclosing_walls=False,rewards=[dict(kind='currency',amount=10,status='explicitpreservedallocation_needsMapbudgetbinding')],difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='Actualupperdockoriginalfreshresources; no externalingresspromise',exit='Observedstablebagdock/reward/originalrenewal'),return_conditions='B->A, arbitraryentrystate/genericboundarycrossing/fullMapUNKNOWN; originalfullbottomfloorpreserved',budget=dict(generator_candidates=4,director_revisions=0))
 return c

def segment_hits_open_rect(a,b,r):
 lo=0.;hi=1.
 for axis in range(2):
  low=r[axis]+1e-4;high=r[axis]+r[axis+2]-1e-4;v=b[axis]-a[axis]
  if abs(v)<1e-10:
   if not low<a[axis]<high:return False
  else:
   u=(low-a[axis])/v;w=(high-a[axis])/v;lo=max(lo,min(u,w));hi=min(hi,max(u,w))
   if lo>=hi:return False
 return lo<hi
def purpose(c,r):
 fs=r.get('frames',[]);why=[];upper=c['platforms'][0];bag=c['platforms'][1];sign=c['rule_parameters']['outward_sign'];shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))]
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if r.get('returns'):why.append('world_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('workshop',{}).get('coins')!=10:why.append('actual_bag_10coin_missing')
 lowshots=[f for f in shots if not f.get('grounded')and f['y']-18>=upper[1]+upper[3]-1e-3]
 if not lowshots:why.append('actual_recoil_after_complete_body_below_lip_missing')
 first=lowshots[0]if lowshots else None;land=next((f for f in fs if first and f['frame']>first['frame']and f.get('grounded')and f.get('support_id')=='Platform1'and abs(f['y']+18-bag[1])<1),None)
 if not land:why.append('actual_bag_top_landing_missing')
 if land and land.get('shot_charges')!=1:why.append('actual_bag_original_ground_renewal_missing')
 phase=[f for f in fs if first and f['frame']>=first['frame']and(not land or f['frame']<=land['frame'])];expanded=[upper[0]-12,upper[1]-18,upper[2]+24,upper[3]+36]
 hits=[b['frame']for a,b in zip(phase,phase[1:])if segment_hits_open_rect([a['x'],a['y']],[b['x'],b['y']],expanded)]
 if hits:why.append('actual_complete_body_segment_enters_original_solid_lip')
 owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=owned]
 if outside:why.append('actual_body_outside_frozen_ownership')
 margin=min(land['x']-12-bag[0],bag[0]+bag[2]-land['x']-12)if land else None
 return dict(ok=not why,reasons=why,causal=dict(first_actual_low_shot={k:first.get(k)for k in ['frame','x','y','vx','vy','shot_charges']}if first else None,first_bag_landing={k:land.get(k)for k in ['frame','x','y','support_id','shot_charges']}if land else None,first_bag_body_horizontal_margin=margin,lip_bottom=upper[1]+upper[3],body=[24,36],actual_swept_solid_intersections=hits,outside_count=len(outside),outside_frames=outside[:12],paid_ground_recovery_allowed=bool(r.get('jumps',0)>0)),behavior={k:r.get(k)for k in ['shots','jumps','ticks']})
