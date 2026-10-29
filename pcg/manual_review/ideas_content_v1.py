"""Decode exact object geometry; reuse the existing N25 closed polyline Cell."""
import copy,math
from pcg.migration import godot_package as native
KIND='closed_polyline_loop/v1'
def reward_consumer_document(doc):
 d=copy.deepcopy(doc)
 for o in d['objects']:
  if o['type']!='reward'or not o.get('mechanics',{}).get('designGlyphOnly'):continue
  assert [o['w'],o['h']]in [[24,24],[24,28]] and o['mechanics']['service']=='SimpleRoomReward'
  x,y=native._center(o);o.update(x=x-18,y=y-18,w=36,h=36)
 return d
def decode(doc):
 d=copy.deepcopy(doc);loops=[];removed=set()
 for deck in doc['objects']:
  if deck.get('type')!='platform'or not deck.get('trackId'):continue
  track=next(o for o in doc['objects']if o['id']==deck['trackId'])
  if track.get('mode')!='loop':continue
  ps=[[p['x'],p['y']]for p in track['points']];assert len(ps)>=4 and math.dist(ps[0],ps[-1])<1e-6
  loops.append(dict(platform_id=deck['sourceId'],trajectory_kind=KIND,start=ps[0],finish=ps[-1],size=[deck['w'],deck['h']],travel_duration=track['duration'],dwell_duration=0,loop_period=track['duration'],loop_points=ps,initial_phase=track.get('initialPhase',0)))
  removed|={deck['id'],track['id']}
  for bell in doc['objects']:
   if bell.get('targetId')==deck['id']:removed.add(bell['id'])
 d['objects']=[o for o in d['objects']if o['id']not in removed];content=native.content_from_objects(reward_consumer_document(d))
 content['moving_platforms']+=loops
 for bell in doc['objects']:
  if bell['id']not in removed or bell['type']!='bell':continue
  deck=next(o for o in doc['objects']if o['id']==bell['targetId']);center=native._center(bell)
  content['latches'].append(dict(id=bell['sourceId'],bell=center,gate=[center[0],center[1],1,1],open_seconds=0,ferry_id=deck['sourceId'],kind='toggle_ferry',actuator_id=deck['sourceId']))
 return content
