"""A bounded spatial grammar: two valley routes + one cross-level shortcut."""
import copy
NODES=[
 ('west','entry','西风崖口',[0,640,460,680],[100,820]),
 ('ridge','challenge','迎风脊',[460,460,460,350],[833.317182305169,460]),
 ('lookout','landmark','风铃望台',[920,460,400,210],[1160,460]),
 ('arch','junction','断索悬桥',[1320,340,420,360],[1600,580]),
 ('east','exit','东岸旧门',[1600,600,710,750],[2160,640]),
 ('hollow','detour','回声谷底',[460,940,590,360],[760,1020]),
 ('bell','reward','下层鸣钟台',[1050,520,550,790],[1160,1040])]
CONTACTS=[
 ('e0','west','ridge',460,640,'side'),('e1','ridge','lookout',920,460,'side'),
 ('e2','lookout','arch',1320,520,'side'),('e3','arch','east',1740,600,'side'),
 ('e4','west','hollow',460,940,'side'),('e5','hollow','bell',1050,1040,'side'),
 ('e6','bell','east',1600,1040,'side'),('e7','bell','arch',1462,520,'vertical')]

def requests():
 nodes=[dict(id=k,role=r,label=l,grants=[],opens=[],reward=0)for k,r,l,_,_ in NODES]
 graph=dict(schema='map-notes/exploration-graph/v1',region='plains',seed='open-valley-sample-0',entry='west',goal='east',initial_abilities=['move','jump','shot_recoil'],nodes=nodes,
  edges=[dict(id=e,**{'from':a,'to':b},bidirectional=True,requires=[],switch=None,cost=1.2 if kind=='vertical'else 1.)for e,a,b,x,y,kind in CONTACTS])
 specs=[];seams=[]
 for key,role,label,bounds,center in NODES:
  dx,dy,W,H=bounds;ports=[]
  for eid,a,b,x,y,kind in CONTACTS:
   if key not in [a,b]:continue
   normal=([0,-1]if key==a else[0,1])if kind=='vertical'else([1,0]if key==a else[-1,0])
   dock=[x,y]if kind=='vertical'else[x-normal[0]*24,y]
   ports.append(dict(id=eid,position=[x-dx,y-dy],normal=normal,kind=kind,dock_world=dock,
       aperture=[x-dx-96,y-dy-100,192,200],connection_mode='open_landing'if kind=='vertical'else'continuous_terrain'))
  specs.append(dict(schema='map-notes/challenge-specification/v1',id='open-valley/'+key,node_id=key,region='plains',
   node=next(n for n in nodes if n['id']==key),placement=[dx,dy],space={'core_bounds':[0,0,W,H]},ports=ports,
   objective=label,boundary_policy='open',enclosing_walls=False,shared_air='compatible clearance may overlap; no collider inferred from bounds',
   capabilities={'version':1,'status':'defined','allOf':['move','jump','shot_recoil'],'anyOfGroups':[]},
   risk_reward={'role':role,'optional_challenge':key=='bell','value':8 if key=='bell'else 0},
   forbidden=['automatic box walls','L4 filler platforms','post-placement navigation repair'],budget={'generator_candidates':1,'unbounded_retry':False}))
 for eid,a,b,x,y,kind in CONTACTS:seams.append(dict(id=eid,a=a,b=b,kind=kind,position=[x,y]))
 mission=dict(schema='map-notes/mission-graph/v1',entry='west',goal='east',objectives=[
  dict(id='reach_east',location='east',role='main'),dict(id='recognize_wind_bell',location='lookout',role='landmark'),
  dict(id='bell_cache',location='bell/reward',role='optional',requires=['shot_recoil'],reward=8)],
  spatial_intent=['upper ridge / lower hollow fork and east reunion','shared open valley, visible lower reward from upper route','bell-to-arch return shortcut'],
  scope='One deterministic authored grammar sample, not a broad-seed benchmark; physical routes verified separately')
 return graph,specs,seams,mission
