import copy
from .revision060_content_v1 import decode as hqdecode
from .revision061_content_v2 import decode as seconddecode
from .revision058_content_v1 import consumer_document
from pcg.migration.godot_package import content_from_objects,_center

def split(doc):
 d=consumer_document(doc);custom=[];obs={o['id']:o for o in d['objects']}
 if 'spec02-s04'in doc['id']:
  for p,main,access in [('P','p-bell','p-low-access'),('Q','q-bell','q-top-access')]:custom.append(dict(kind='group_motion',id=p+'-bell',bell=_center(obs[main]),access=[_center(obs[access])],targets=[p]))
  d['objects']=[o for o in d['objects']if o['type']!='bell']
 if 'spec02-s06'in doc['id']:custom.append(dict(kind='rigid_mounted_bell',id='under-bell',mount='P',offset=[0,64]))
 return d,custom

def decode(doc):
 if 'plains-hq'in doc['id']:return hqdecode(doc)
 if any(x in doc['id']for x in ['spec02-s10','spec02-s12']):return seconddecode(doc)
 d,custom=split(doc);c=content_from_objects(d);c['approved_hq_cells']=custom;return c
