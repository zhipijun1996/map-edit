import copy
from .revision058_content_v1 import consumer_document
from .ideas_content_v1 import reward_consumer_document
from pcg.migration.godot_package import content_from_objects,_center
KIND='clockwise_ellipse/v1'
def split(doc):
 d=reward_consumer_document(consumer_document(doc));custom=[];n=doc['id'];ellipse=None
 if 'spec02-s11' in n:
  d['objects']=[o for o in d['objects']if o['id']not in ['orbit-rail','P']];ellipse=dict(platform_id='P',trajectory_kind=KIND,start=[160,256],finish=[480,256],size=[112,16],travel_duration=8.,dwell_duration=0.,initial_phase=0.,ellipse_center=[320,256],ellipse_radii=[160,144],ellipse_period=8.)
 if 'spec02-s12'in n:
  obs={o['id']:o for o in d['objects']}
  for p,main,access in [('P','p-control',['p-bottom-access']),('Q','q-control',['q-top-access','q-right-access'])]:custom.append(dict(kind='group_motion',id=p+'-bell',bell=_center(obs[main]),access=[_center(obs[k])for k in access],targets=[p]))
  d['objects']=[o for o in d['objects']if o['type']!='bell']
 return d,custom,ellipse
def decode(doc):
 d,custom,ellipse=split(doc);c=content_from_objects(d);c['approved_hq_cells']=custom
 if ellipse:c['moving_platforms'].append(ellipse)
 return c
