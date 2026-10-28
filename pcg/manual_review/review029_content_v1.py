import copy
from pcg.migration import godot_package as base
from pcg.manual_review.first30_content_v2 import decode as ordinary

def filtered(doc):
 d=copy.deepcopy(doc);d['objects']=[o for o in d['objects']if o.get('mechanics',{}).get('kind')!='player_enter_spawn_wave'];return d

def wave(doc):
 triggers=[o for o in doc['objects']if o.get('mechanics',{}).get('kind')=='player_enter_spawn_wave']
 if not triggers:return None
 assert len(triggers)==1
 t=triggers[0];assert t['mechanics']['kind']=='player_enter_spawn_wave'and t['mechanics']['oneShotPerAttempt']
 enemies=[o for o in doc['objects']if o['type']=='enemy'];assert len(enemies)==2 and set(t['targetIds'])=={e['id']for e in enemies}
 for e in enemies:
  assert e['spawnCondition']==dict(triggerId=t['id'],event='player_enter',initialPresent=False)
  assert e['movementIntent']['targetX']==512 and e['movementIntent']['speed']==18
 return dict(rect=base._rect(t),targetX=512,speed=18,oneShot=True)

def decode(doc):
 d=ordinary(filtered(doc));w=wave(doc)
 if w:d['review029_wave']=w
 return d
