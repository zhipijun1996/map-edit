import copy
from .revision059_hq_content_v1 import split as previous_split
from .revision058_content_v1 import consumer_document
from pcg.migration.godot_package import content_from_objects,_rect,_center

def split(doc):
 n=doc['id']
 if 'hq01'in n or 'hq02'in n:return previous_split(doc)
 d=consumer_document(doc);custom=[]
 if 'interface-s12'in n:
  custom.append(dict(kind='native_one_way_carriers',ids=['P','Q']))
 if 'hq08'in n:
  custom.append(dict(kind='support_start_motion',id='P'));d['objects']=[o for o in d['objects']if o.get('mechanics',{}).get('approvedCellType')!='triggerZone']
 if 'hq09'in n:
  obs={o['id']:o for o in d['objects']};turret=obs['fixed-turret'];direction=turret['mechanics']['fixedDirection'];center=_center(turret);muzzle=[center[i]+direction[i]*24 for i in range(2)];custom +=[dict(kind='projectile_barrier',id='P'),dict(kind='retract_thorns',id='exit-platform-thorns',bell=_center(obs['target-bell']),access=_center(obs['return-bell']),hazards=[dict(id=k,rect=_rect(obs[k]))for k in ['exit-thorns-top','exit-thorns-bottom']]),dict(kind='hit_turret',id=turret['id'],rect=_rect(turret),muzzle=muzzle,direction=direction,cooldown=.6,delay=.05,speed=720.,lifetime=1.,latch_id='target-bell')]
  for o in d['objects']:
   if o['id']=='P':o['type']='platform'
  omit=['fixed-turret','target-bell','return-bell','exit-thorns-top','exit-thorns-bottom'];d['objects']=[o for o in d['objects']if o['id']not in omit]
 return d,custom

def decode(doc):
 d,custom=split(doc);c=content_from_objects(d);c['approved_hq_cells']=custom;return c
