"""Exact approved TOP one-way transit, retaining full 24x36 crossing tests.

The owned top deck is 32px below the boundary: its resting center is14, so
4px of the body straddles the open Port. Ingress continues through that deck
until fully inside. Egress starts at a real interior Port, completes the frozen canonical
arrival, then uses an original jump. The explicit neighbor is within its own 128px Block.
"""
import copy
from . import core
VERSIONS={'idea-orbit-choice-001':'sha256:f665b6d2c9e342f2aac01a0cf27587a8261cb895664c94f47e4da0e84086b462','idea-0363f85c-16c0-4b5f-b3b0-461335608db7-enemies-2':'sha256:f0829bf856a234834748750c4a4fec31042eaae8003d1f97bac7432b81f402b2','idea-0363f85c-16c0-4b5f-b3b0-461335608db7-enemies-3':'sha256:61124f9e700cb0b1400cdd5efda98cbdb4dc2c410cec33c632858178e199ffe6'}
def applies(case,port):
 s=case.get('approved_implementation',{});return VERSIONS.get(s.get('reviewId'))==s.get('designVersion')and port.get('face')=='TOP'and port.get('normal')==[0,-1]and port.get('surface')=='ONE_WAY_PLATFORM'and port.get('position',[None,None])[1]==0 and port.get('stagingPosition',[None,None])[1]==14

def dock_plan(x,y,after=1):return[dict(op='settle',target_x=x,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',trigger=dict(after=after,state='grounded',migration_goal=[x-4,y-3,8,6],timeout=240))]
def entered():return dict(op='wait',height_threshold=20,trigger=dict(after=1,state='descending_height',timeout=90))
def local(case,port,direction,doc,offset=0):
 x,y=port['stagingPosition'];outer=[x,-114]
 if direction=='ingress':
  target=[240,230]if case['approved_implementation']['reviewId']=='idea-orbit-choice-001'else[24,case['approved_implementation']['rectangle']['h']-50]
  plan=[dict(op='settle',target_x=x,deadband=2,trigger=dict(after=0)),dict(op='drop_through',trigger=dict(after=1))]+dock_plan(x,y)+[dict(op='drop_through',trigger=dict(after=1)),entered()]+dock_plan(*target)
 else:
  reference=doc['generationContract']['generation']['approvedImplementation']['boundaryInputs'];core.verify_artifacts([reference]);arrivals=core.read(core.resolve_artifact(reference['path']))['cases'];arrival=next(c for c in arrivals if c['route_spec']['to_port']==port['id']and c['route_spec']['from_port']!=port['id'])
  old=copy.deepcopy(case);case.clear();case.update(copy.deepcopy(arrival));case.update(id=old['id'],platforms=old['platforms'],one_way_platform_indices=old['one_way_platform_indices'],migration_probe=old['migration_probe']);case['spawn'][0]+=offset
  target=outer;plan=copy.deepcopy(arrival['control_plan'])+dock_plan(x,y,after=6)+[dict(op='jump',trigger=dict(after=1)),dict(op='jump_release',trigger=dict(after=24))]+dock_plan(*target)
 case['control_plan']=plan;case['goal']=[target[0]-9,target[1]-5,18,10];case['max_frames']=3300
 case['migration_probe']['ideasTopTransit']=dict(version=1,ownedStand=[x,y],fullBodyIngress='continues through owned top deck to a real interior support',egressPreparation='complete frozen canonical arrival from an interior Port, then original jump; original full-body crossing observer unchanged',neighborTop=-96)

def entry(case,doc,physics):
 port=next(p for p in doc['generationContract']['ports']if p['id']==case['route_spec']['from_port'])
 if not applies(case,port):return None
 v=physics.fresh(case,'continuous-entry');neighbor=physics.exterior_floor(v,port);x,y=port['stagingPosition'];v['spawn']=[x,neighbor['floor'][1]-18]
 v['control_plan']=[dict(op='settle',target_x=x,deadband=2,trigger=dict(after=0)),dict(op='drop_through',trigger=dict(after=1))]+dock_plan(x,y)+copy.deepcopy(case['control_plan']);v['max_frames']=min(3600,case['max_frames']+300)
 v['migration_probe']=dict(kind='continuous_entry',portId=port['id'],direction='ingress',boundary=port['position'],normal=port['normal'],neighbor=neighbor,body=[24,36],noIntermediateReset=True,originalRouteId=case['route_spec']['id'],scope='explicit neighbor through top owned deck and complete original route; no starting-dock-only claim',ideasTopTransit=dict(version=1,neighborTop=-96))
 v['module_sha256']=physics.module_hash(v);return v

def exit(case,doc,physics):
 port=next(p for p in doc['generationContract']['ports']if p['id']==case['route_spec']['to_port'])
 if not applies(case,port):return None
 v=physics.fresh(case,'continuous-exit');neighbor=physics.exterior_floor(v,port);x,y=port['stagingPosition'];target=[x,neighbor['floor'][1]-18]
 v['control_plan']+=dock_plan(x,y,after=6)+[dict(op='jump',trigger=dict(after=1)),dict(op='jump_release',trigger=dict(after=24))]+dock_plan(*target)
 v['goal']=[target[0]-9,target[1]-5,18,10];v['max_frames']=min(3600,case['max_frames']+300)
 v['migration_probe']=dict(kind='continuous_exit',portId=port['id'],direction='egress',boundary=port['position'],normal=port['normal'],neighbor=neighbor,body=[24,36],noIntermediateReset=True,originalRouteId=case['route_spec']['id'],scope='complete original landing/program before real upward Port exit',ideasTopTransit=dict(version=1,neighborTop=-96))
 v['module_sha256']=physics.module_hash(v);return v
