"""Expose explicit any-side native access policy without altering approved geometry."""
import copy
from .revision058_content_v1 import consumer_document as base_consumer,decode as previous

def compatible(doc):
 d=copy.deepcopy(doc)
 for o in d['objects']:
  if o['type']=='bell'and o.get('mechanics',{}).get('service')=='ShotLatch.add_access_bell'and o['mechanics'].get('returnSideOnly')is False:o['mechanics']['returnSideOnly']=True
 return d

def consumer_document(doc):return base_consumer(compatible(doc))
def decode(doc):
 c=previous(compatible(doc))
 for o in doc['objects']:
  if o['type']=='bell'and o.get('mechanics',{}).get('service')=='ShotLatch.add_access_bell'and o['mechanics'].get('returnSideOnly')is False:
   next(l for l in c['latches']if l['id']==o['sourceId'].removesuffix('/return'))['return_access_side_policy']='any'
 return c
