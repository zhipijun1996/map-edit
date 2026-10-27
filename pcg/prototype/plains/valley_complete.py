"""Demand materialization through the existing open-landform Module producer.

Only explicit challenge chambers receive local rock caps. No bounding-box walls,
no map-level filler. Original geometry and failures remain reconstructible.
"""
from copy import deepcopy
from .open_landforms import generate as open_generate
from .synthesis import command
from ..factory.core.quality import digest
from .engine import ROOT
import json

def generate(spec):
 if spec['node_id']=='relay':return relay(spec)
 m=open_generate(spec);c=m['case'];key=m['id'];dx,dy=spec['placement']
 def rock(x,y,w,h):
  c['platforms'].append([x-dx,y-dy,w,h]);return len(c['platforms'])-1
 def gate(x,y,w,h):
  c['latches'][0]['gate']=[x-dx,y-dy,w,h]
 for latch in c['latches']:latch['open_seconds']=0 # permanent unlock, safe return
 if key=='west':
  # Local geological overhang + a readable 100wu door, rather than stretching
  # the gate art into a sky-high fence. The cap is real collision.
  gate(214,558,24,100)
  rock(214,360,246,150);rock(214,510,150,48)
  c['latches'][0]['return_access']=[400-dx,620-dy]
  m['port_to_center']['e0'].insert(0,dict(kind='module',target=m['ports']['e0']['dock'],control_plan=[command('axis',value=0),command('wait',30),command('shoot',direction=[-.874157,-.485643]),command('settle',30,target_x=436-dx,deadband=3)]))
 elif key=='ridge':
  gate(791.317182305169,298,24,180)
  rock(791.317182305169,160,128.682817694831,138)
  c['latches'][0]['return_access']=[870-dx,423.44-dy]
  rock(791.317182305169,478,68.682817694831,260)
 elif key=='arch':
  # A small treasure niche, not an outer room shell. Enter from the actual bell
  # gate; the lower gear bridge remains a legitimate non-reward alternative.
  gate(1631.317182305169,140,24,218)
  rock(1655.317182305169,358,84.682817694831,36)
  rock(1720,140,20,218);rock(1631.317182305169,116,108.682817694831,24)
 elif key=='bell':
  gate(1192,644,16,234)
  rock(1208,878,104,24);rock(1288,724,24,154);rock(1192,724,120,24)
  gate(1192,748,16,130)
  # A second original ShotLatch toggles the original carrier; it is a new
  # action relationship (airborne shot parks a moving receiver), not a skin.
  c['latches'].append(dict(id='parking-bell',bell=[1434-dx,530-dy],
   gate=[1340-dx,550-dy,16,16],open_seconds=0,prompt='SHOOT TO PARK',ferry_id='valley-return'))
  for leg in m['center_to_port']['e7']:
   if 'carrier_transfer' in leg:leg['carrier_transfer']['park_bell']='parking-bell'
  # The chest floor is now solid. Leave through the open entrance before
  # dropping; never ask the old one-way drop policy to tunnel through rock.
  m['core_visit_program'].insert(1,dict(kind='walk',target=dict(id='bell/cache-entrance',position=[1160-dx,860-dy],region=[1152-dx,856-dy,16,8],support_indices=[5],grounded=True)))
 elif key=='east':
  p=deepcopy(m['ports']['e8'])
  m['ports']['e8']=p
  m['center_to_port']['e8']=[dict(kind='drop',target=dict(id='east/spur',position=[560,160],region=[552,156,16,8],support_indices=p['dock']['support_indices'],grounded=True)),dict(kind='walk',target=p['dock'])]
  m['port_to_center']['e8']=[dict(kind='walk',target=dict(id='east/spur',position=[560,160],region=[552,156,16,8],support_indices=p['dock']['support_indices'],grounded=True)),dict(kind='jump',target=m['center'],hold_ticks=20)]
 c['reward_sites']=[];c['shop_sites']=[]
 if key in ['arch','bell']:
  c['reward_sites']=[dict(id='bridge-cache'if key=='arch'else'bell-cache',target=deepcopy(m['core']['exit']),required_bell='arch-bell'if key=='arch'else'valley-bell',reward=12 if key=='arch'else 8)]
 if key=='lookout':c['shop_sites']=[dict(id='merchant',position=[240,0],price=8,item='damage_blue')]
 m['origin']='Map-demand revision: gate/cliff attachment, treasure niches and original motion-toggle Cell'
 m['content_version']='sha256:'+digest({k:m[k]for k in ['case','ports','core','boundary_gates']})
 return m

def relay(spec):
 old=next(c for c in json.loads((ROOT/'results/plains-review-v1/review_cases.json').read_text())['cases']if c['family']=='enemy_refund')
 dx,dy=spec['placement'];ox,oy=2310,340
 c=deepcopy(old);c.pop('recorded_frames',None);c.update(id='valley-relay',family='plains_enemy_refund_cache',spawn=[80,60],entry_port=[80,60],world_bounds=[-32,-180,850,700],hazards=[],thorns=[],saws=[],latches=[],moving_platforms=[])
 c['platforms']=[[0,78,240,70],[old['platforms'][1][0],78,176,72],[240,278,550,100],[240,158,110,24]]
 c['one_way_platform_indices']=[3]
 for e in c['enemies']:e['position']=[e['position'][0],e['position'][1]-360]
 for op in c['control_plan']:
  if 'target_x' in op:pass # x coordinates already match the local placement
 exit_x=old['exit_port'][0]
 def target(x,y,label,support):return dict(id='relay/'+label,position=[x,y],region=[x-8,y-4,16,8],support_indices=[support],grounded=True)
 center=target(80,60,'center',0);reward=target(exit_x,60,'treasure',1);dock=target(24,60,'e8',0)
 core=dict(entry=center,exit=reward,control_plan=deepcopy(c['control_plan']),source='results/plains-review-v1/review_cases.json')
 c['reward_sites']=[dict(id='relay-cache',target=deepcopy(reward),required_bell='',required_enemy='ammo_sentry',reward=16)]
 c['shop_sites']=[]
 visit=[dict(kind='module',target=reward,control_plan=core['control_plan']),
  dict(kind='drop',target=target(exit_x+110,260,'return-bottom',2)),dict(kind='walk',target=target(380,260,'return-step',2)),
  dict(kind='jump',target=target(300,140,'return-ledge',3),hold_ticks=20),dict(kind='jump',target=target(220,60,'source-bank',0),hold_ticks=20),
  dict(kind='module',target=center,control_plan=[command('axis',value=-1),command('jump'),command('jump_release',8),command('shoot',2,aim_cell={'kind':'enemy','id':'ammo_sentry'},direction=[-1,0]),command('shoot',30,aim_cell={'kind':'enemy','id':'ammo_sentry'},direction=[-1,0]),command('settle',20,target_x=80,deadband=3)])]
 p=deepcopy(spec['ports'][0]);p.pop('dock_world');p['dock']=dock
 m=dict(id='relay',spec=deepcopy(spec),case=c,ports={'e8':p},center=center,
  center_to_port={'e8':[dict(kind='walk',target=dock)]},port_to_center={'e8':[dict(kind='walk',target=center)]},
  core=core,core_visit_program=visit,boundary_gates=[],assembly_created_geometry=False,
  quality={'human_fun':'unverified','production_admitted':False},origin='Existing measured enemy-refund action core, new Map demand and physically reverified return')
 m['content_version']='sha256:'+digest({k:m[k]for k in ['case','ports','core','boundary_gates']})
 return m
