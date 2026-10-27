"""Repair actual PR-D02 sightline/height window on original carrier physics."""
from pathlib import Path
from pcg.prototype.creative_batches.descending_carrier.probe_v1 import candidates as original
from pcg.prototype.workshop.rules import cmd,wait_x,settle,reward
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
CELL=HERE.parent/'batch30_cell'
OLD=HERE.parent/'descending_carrier'
RECIPES=('descending-clearance-departure',)
RUNNER_SCRIPT=CELL/'runner_v3.gd'
NATIVE_SCENE=CELL/'main_v3.tscn'
SOURCE_DEPENDENCIES=[HERE/'proposal-source-v1.json',HERE/'protocol-v1.json',OLD/'probe_v1.py',OLD/'counters_v1.py',OLD/'protocol-v1.json',HERE.parents[2]/'feedback/workshop/descending-carrier-prepark-v1.json',*[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn']]]
def candidate(interface=0,control=0):
 if interface!=0:raise ValueError('Steep secondspace waits actualwidecore+oldcheap regression')
 c=original()[0];c['id']=f'b30-c11-v1-i0-c{control}';c['family']=RECIPES[0]
 c['platforms'][1]=[950,360,280,100];c['platforms'].append([300,100,30,210])
 c['moving_platforms'][0].update(start=[360,360],finish=[760,600])
 c['latches'][0]['bell']=[540,310];c['latches'][0].pop('return_access',None)
 retreat,advance=[(305,510),(305,530),(325,510),(325,530)][control]
 c['control_plan'][6]=wait_x(retreat,-1);c['control_plan'][8]=wait_x(advance);c['control_plan'][-1]=settle(1080,6)
 c.update(exit_port=[1080,342],goal=[1055,338,50,8],interface=0,production_recipe=RECIPES[0],native_scene='res://prototype/creative_batches/batch30_cell/main_v3.tscn',idea_ids=['B30-C11','PR-D02'],max_frames=1500)
 c['ports']=[dict(id='A',position=[80,272],normal=[-1,0],support_index=0),dict(id='B',position=[1080,342],normal=[1,0],support_index=1)]
 c['reward_sites']=[];reward(c,1080,342,8);c['required_rewards']=['visible-cache'];c['expected_reward']=8
 c['route_spec']=dict(id='descent',from_port='A',to_port='B',role='main',via_ports=[],require_bell=True,required_rewards=c['required_rewards'])
 c['rule_parameters']=dict(interface=0,control=control,retreat_x=retreat,forward_read_x=advance,roof=[560,60,160,350],receiver=[950,360,280,100],carrier_drop=240,departure_x=744,near_shore_tooth=[300,100,30,210],core='originalshot startsdescendingdeck and adjusts relativeposition; stay behind untilbodyclearslowroof then depart beforeheightlost',independent_new_family_claim=False)
 c['layout_title']='下沉渡台：先退后抢 / 缓降悬岩'
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites','thorns']})
 c['generation_rule']=dict(id='batch30/C11',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 return c
def purpose(c,r):
 fs=r.get('frames',[]);why=[];moving=[];relative=[]
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if r.get('returns'):why.append('world_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 claims={e['id']for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')}
 if not set(c['required_rewards'])<=claims:why.append('reward_missing')
 for f in fs:
  if not f.get('grounded')or f.get('support_id')!='descending-deck':continue
  p=next((p for p in f.get('moving_platforms',[])if p['id']=='descending-deck'),None)
  if p:
   relative.append(dict(frame=f['frame'],relative_x=f['x']-p['position'][0],actor=[f['x'],f['y']],platform=p['position']))
   if p.get('physics_velocity',[0,0])[1]>10:moving.append(f)
 drop=max((f['y']for f in moving),default=0)-min((f['y']for f in moving),default=0)
 if len(moving)<24 or drop<120:why.append('actual_moving_descent_support_bypassed')
 roof=c['platforms'][2];gaps=[]
 for a,b in zip(fs,fs[1:]):
  if max(a['x'],b['x'])+12<=roof[0]-10 or min(a['x'],b['x'])-12>=roof[0]+roof[2]:continue
  gaps.append(min(a['y'],b['y'])-18-(roof[1]+roof[3]))
 if not gaps or min(gaps)<-.1:why.append('complete_body_roof_clearance_missing')
 return dict(ok=not why,reasons=why,causal=dict(moving_supported_frames=len(moving),moving_supported_drop=drop,minimum_sampled_swept_body_roof_clearance=min(gaps,default=None),relative_range=[min((f['relative_x']for f in relative),default=None),max((f['relative_x']for f in relative),default=None)],relative_keyframes=relative[::20],rear_boarding_and_no_inverse_axis_accepted=True),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')))
