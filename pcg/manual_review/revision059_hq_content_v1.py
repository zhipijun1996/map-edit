"""Exact approved HQ objects; custom Cell definitions explicitly decoded and audited."""
from .revision058_content_v1 import consumer_document
from pcg.migration.godot_package import content_from_objects,_rect,_center

def split(doc):
 d=consumer_document(doc);n=doc['id'];custom=[]
 if 'hq01' in n:
  bells=[o for o in d['objects']if o['type']=='bell'];custom=[dict(kind='group_motion',id='group-bell',bell=_center(next(o for o in bells if o['id']=='group-bell')),access=[_center(o)for o in bells if o['id']!='group-bell'],targets=['P','Q'])];d['objects']=[o for o in d['objects']if o not in bells]
 if 'hq04' in n:
  custom=[dict(kind='reward_pair',id='reward-pair',reward_id='reward',gate=_rect(next(o for o in d['objects']if o['id']=='gate-A')),paired_gate=_rect(next(o for o in d['objects']if o['id']=='gate-B')),initial_open='A')];d['objects']=[o for o in d['objects']if o['type']!='gate' and o.get('mechanics',{}).get('approvedCellType')!='triggerZone']
 if 'hq05' in n:
  turret=next(o for o in d['objects']if o.get('mechanics',{}).get('approvedCellType')=='hitTurret');custom=[dict(kind='hit_turret',id=turret['id'],rect=_rect(turret),muzzle=turret['mechanics']['muzzle'],direction=turret['mechanics']['fixedDirection'],cooldown=.6,delay=.05,speed=720.,lifetime=1.,latch_id='turret-target-bell')];d['objects']=[o for o in d['objects']if o.get('mechanics',{}).get('approvedCellType')!='hitTurret']
 return d,custom

def decode(doc):
 d,custom=split(doc);c=content_from_objects(d);c['approved_hq_cells']=custom;return c
