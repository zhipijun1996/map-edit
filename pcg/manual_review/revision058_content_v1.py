"""Native decoded geometry from exact approved objects, without generator fallback."""
import copy
from pcg.migration import godot_package as native
from .lift_idea_v1 import consumer_document as motions

def consumer_document(doc):
 d=motions(doc)
 for o in d['objects']:
  if o.get('designMotion'):
   m=o['designMotion'];o['duration']=m.get('period',m.get('travel_duration'));o['dwell']=m.get('dwell_duration',0);o['initialPhase']=m['initial_phase']
 for o in d['objects']:
  if o['type']=='bell':
   x,y=native._center(o);o.update(x=x-14,y=y-17,w=28,h=34)
 return d

def decode(doc):
 d=consumer_document(doc)
 # Existing native pair supports one return receiver. The third same-group
 # access is installed against that SAME latch by the explicit native binding.
 extra=[o for o in d['objects']if o.get('mechanics',{}).get('extraPairAccess')]
 d['objects']=[o for o in d['objects']if o not in extra]
 c=native.content_from_objects(d)
 for o in extra:
  latch=next(l for l in c['latches']if l['id']==o['mechanics']['groupSourceId']);latch['additional_pair_access']=native._center(o)
 return c
