"""New closed door is an actual collision brake, observed through original Motor."""
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle,reward
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
CELL=HERE.parent/'batch30_cell'
RECIPES=('new-wall-collision-brake',)
RUNNER_SCRIPT=HERE/'runner_v1.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[HERE/n for n in ['protocol-v1.json','proposal-source-v1.json','contact_observer_v1.gd','runner_v1.gd','main_v1.gd','main_v1.tscn']]+[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn']]
def candidate(interface=0,control=0):
 if interface!=0:raise ValueError('Second-space waits for actual core collision and bounded counterexamples')
 c=base(f'b30-c07-v1-i0-c{control}');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil']
 c['platforms']=[[-160,180,400,120],[164,470,130,30],[550,360,230,80],[-160,800,1120,60],[-160,650,140,30],[760,650,160,30],[780,510,140,30]]
 c['latches']=[dict(id='brake-pair',bell=[450,365],gate=[490,-200,24,670],paired_gate=[140,300,24,170],initial_open='B')]
 c['ports']=[dict(id='A',position=[100,162],normal=[-1,0],support_index=0),dict(id='B',position=[650,342],normal=[1,0],support_index=2)]
 c.update(spawn=[100,162],entry_port=[100,162],exit_port=[650,342],goal=[625,338,50,8],interface=0,trace_all=False,max_frames=1300,production_recipe=RECIPES[0],idea_ids=['B30-C07'],native_scene='res://prototype/creative_batches/batch30_c07/main_v1.tscn')
 departure=[325,340,355,370][control]
 c['control_plan']=[cmd('axis',value=1),wait_x(departure),cmd('shoot',aim_cell=dict(kind='bell',id='brake-pair')),cmd('axis',value=-1,after=6),cmd('wait',45),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=1),wait_x(275),cmd('jump'),cmd('jump_release',8),cmd('shoot',6,direction=[-.8,.6]),settle(650,6)]
 c['reward_sites']=[];reward(c,650,342,12);c['required_rewards']=['visible-cache'];c['expected_reward']=12
 c['route_spec']=dict(id='brake',from_port='A',to_port='B',role='main',via_ports=[],require_bell=True,required_rewards=c['required_rewards'])
 c['required_pair_states']=[dict(id='brake-pair',open_a=True,open_b=False)]
 c['rule_parameters']=dict(interface=0,control=control,shot_at_actor_x=departure,core='same-shot opens forward gate and builds solid left brake, original wall contact then pocket support before onward jump',body=[24,36])
 c['layout_title']='关出一面能接住反冲的墙 / 横向浅袋'
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites']})
 c['generation_rule']=dict(id='batch30/C07',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 return c
def purpose(c,r):
 fs=r.get('frames',[]);why=[]
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('unexpected_reset')
 claimed={e['id']for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')}
 if not set(c['required_rewards'])<=claimed:why.append('reward_missing')
 pair=next((p for p in r.get('workshop',{}).get('paired_gates',[])if p['id']=='brake-pair'),{})
 events=[e for e in pair.get('events',[])if e.get('type')=='pair_switch'and e.get('open')=='A']
 if not events:why.append('actual_wall_build_missing')
 contacts=[dict(frame=f['frame'],actor=[f['x'],f['y']],velocity=[f['vx'],f['vy']],contact=h)for f in fs for h in f.get('original_slide_contacts',[])if h['body']=='PairGateB_brake-pair'and h['normal'][0]>.7]
 if not contacts:why.append('actual_new_wall_side_contact_missing')
 pocket=[f for f in fs if f.get('grounded')and f.get('support_id')=='Platform1']
 if not pocket:why.append('actual_receiving_pocket_support_missing')
 if contacts and pocket and min(f['frame']for f in pocket)<=contacts[0]['frame']:why.append('pocket_support_not_after_wall_contact')
 if any(pair.get(k)!=v for k,v in dict(open_a=True,open_b=False).items()):why.append('world_state_wrong')
 shots=[dict(frame=f['frame'],x=f['x'],y=f['y'],airborne=not f.get('grounded'))for f in fs if any(a.get('type')=='shot'for a in f.get('accepted',[]))]
 return dict(ok=not why,reasons=why,causal=dict(wall_side_contacts=contacts[:12],wall_contact_frames=len(contacts),pocket_frames=len(pocket),first_pocket_frame=min((f['frame']for f in pocket),default=None),switches=events,shots=shots),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')))
