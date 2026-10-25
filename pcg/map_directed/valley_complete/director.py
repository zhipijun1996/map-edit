"""Incremental revision of the existing Mission/Exploration contract."""
from copy import deepcopy
from ..open_valley.director import requests as original_requests

def requests():
 graph,specs,seams,mission=deepcopy(original_requests())
 graph['seed']='valley-complete-v1'
 graph['nodes'].append(dict(id='relay',role='reward',label='巡风者宝库',grants=[],opens=[],reward=0))
 graph['edges'].append(dict(id='e8',**{'from':'east','to':'relay'},bidirectional=True,requires=[],switch=None,cost=2.5))
 seams.append(dict(id='e8',a='east',b='relay',kind='side',position=[2310,760]))
 next(s for s in specs if s['node_id']=='east')['ports'].append(dict(id='e8',position=[710,160],normal=[1,0],kind='side',dock_world=[2286,760],aperture=[614,60,192,200],connection_mode='continuous_terrain'))
 specs.append(dict(schema='map-notes/challenge-specification/v1',id='relay',node_id='relay',region='plains',
  node=graph['nodes'][-1],placement=[2310,700],space={'core_bounds':[0,0,790,480]},
  ports=[dict(id='e8',position=[0,60],normal=[-1,0],kind='side',dock_world=[2334,760],aperture=[-96,-40,192,200],connection_mode='continuous_terrain')],
  objective='空中命中巡风者回充后再次反冲，取得远端宝箱；下层安全回程',boundary_policy='open',enclosing_walls=False,
  capabilities={'version':1,'status':'defined','allOf':['move','jump','shot_recoil'],'anyOfGroups':[]},
  risk_reward={'role':'reward','optional_challenge':True,'value':16},forbidden=['L4 filler platforms'],budget={'generator_candidates':1,'unbounded_retry':False}))
 for s in specs:
  s['id']='valley-complete-v1/'+s['node_id']
  s['revision']='reward-chambers-and-motion-control-v1'
  s['mechanic_requirements']={
   'west':['airborne bell recoil','upper-route chokepoint; lower route is intentional'],
   'ridge':['airborne angled bell recoil','gate attached to receiving cliff'],
   'arch':['optional sealed cache','lower saw bridge is explicit alternative'],
   'bell':['sealed recoil cache','release then airborne park return carrier'],
   'hollow':['moving gear passage'],
   'relay':['enemy hit refund','second airborne recoil','remote treasure','lower return'],
   'lookout':['merchant; spend earned cache coins; no free balance'],
   'east':['reunion','region exit']}.get(s['node_id'],[])
  s['risk_reward']['value']=12 if s['node_id']=='arch' else 8 if s['node_id']=='bell' else 0
 mission['objectives'] += [dict(id='bridge_cache',location='arch',role='optional',reward=12),
  dict(id='trade_cache_coins',location='lookout',role='optional',price=8,item='damage_blue')]
 mission['gate_design']={'west':'protect upper entrance; lower detour remains legal',
  'ridge':'protect receiving cliff; lower detour remains legal',
  'arch':'sealed optional treasure, bridge below is intentionally ungated',
  'bell':'sealed optional treasure and upper return shortcut'}
 mission['scope']='Complete seven-Module small region with two loops, two physical treasure chambers and merchant. Region exit, no boss fight or campaign persistence.'
 return graph,specs,seams,mission
