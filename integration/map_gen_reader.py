"""Read a delivery package into map-gen's prototype.model template convention.

Does not call generate.prepare_library (which replaces templates with mocks).
Consumers MUST call validate_placement before accepting each placement.
"""
import hashlib,json
from pathlib import Path
ABILITY={'shot_recoil':'recoil'}

def read_library(root):
 root=Path(root);manifest=json.loads((root/'manifest.json').read_text())
 for name,digest in manifest['files'].items():
  if Path(name).is_absolute()or'..'in Path(name).parts:raise ValueError('unsafe_package_path')
  if hashlib.sha256((root/name).read_bytes()).hexdigest()!=digest:raise ValueError('changed_package_file:'+name)
 catalog=json.loads((root/'catalog.json').read_text());result={}
 for entry in catalog['modules']:
  mid=entry['id']
  if mid in result:raise ValueError('duplicate_module_id:'+mid)
  bs=entry['blockSize'];bounds=entry['bounds'];ports=[]
  for p in entry['ports']:
   at=p['position'];xy=[at[k]for k in ['x','y']]if isinstance(at,dict)else at
   local2=[2*(xy[i]-bounds[k])/bs for i,k in enumerate(['x','y'])]
   if any(abs(v-round(v))>1e-8 for v in local2):raise ValueError('non_block_port:'+mid+':'+p['id'])
   ports.append(dict(id=p['id'],face=p['face'],local2=[round(v)for v in local2],surface=p['surface'],permission=p['permission'],closure=None,initial_permission_conditions={**p.get('initialPermissionConditions',{}),**({'availableAbilitiesExact':[ABILITY.get(v,v)for v in p['initialPermissionConditions']['availableAbilitiesExact']if v!='move']}if p.get('initialPermissionConditions',{}).get('availableAbilitiesExact')is not None else{})}))
  pp={p['id']:p for p in ports};routes=[]
  for r in entry['routes']:
   a,b=pp[r['from']],pp[r['to']]
   # Initial one-way interfaces are not inferred from later mechanism states.
   if a['permission']=='OUTPUT'or b['permission']=='INPUT':continue
   caps=r['validation']['availableAbilities']
   routes.append(dict(id=r['id'],from_port=r['from'],to_port=r['to'],displacement=[(b['local2'][i]-a['local2'][i])/2 for i in [0,1]],required_abilities=[ABILITY.get(v,v)for v in caps if v!='move'],action_tags=r.get('actionTags',[]),difficulty=r['difficulty'].get('score'),estimated_duration=r.get('durationSeconds'),resource_profile=r.get('resourceProfile'),initial_conditions=r.get('initialConditions'),entry_exit_contract=r.get('transfer'),validation=r['validation'],capability_requirements=r['capabilityRequirements']))
  result[mid]=dict(id=mid,name=entry['title'],size_blocks=entry['sizeBlocks'],ports=ports,routes=routes,allow_mirror_x=False,reward=any(r.get('resourceProfile',{}).get('rewardSites')for r in entry['routes']),certification=dict(status='NATIVE_SCOPED',routes=True,seams=False,closures=False,mirror=False),allowed_configurations=entry['configurations'],content_version=entry['contentVersion'],scene=entry['scene'],scene_origin_offset=entry['sceneOriginOffsetPixels'],block_size=bs,package_version=manifest['version'],initial_configuration=entry['initialConfiguration'],host_profile=entry['hostProfile'])
 return result

def validate_placement(template,connected_port_ids,mirror=False,relocations=(),closures=()):
 if mirror or relocations or closures:raise ValueError('uncertified_transform_relocation_or_closure')
 if len(connected_port_ids)!=len(set(connected_port_ids)):raise ValueError('duplicate_connected_port')
 for config in template['allowed_configurations']:
  if set(config['connectedPortIds'])==set(connected_port_ids):return config['id']
 raise ValueError('uncertified_connected_port_subset')

def routes_for_abilities(template,available,native_profile_id=None):
 """Only exact witnessed ability sets; minimum requirements are not certified."""
 available=set(available)-{'move'}
 config=template['initial_configuration'];profile=config.get('nativeFixture')or config.get('nativeTuning')
 if profile and profile.get('id')!=native_profile_id:return[]
 ports={p['id']:p for p in template['ports']}
 return[r for r in template['routes']if set(r['required_abilities'])==available and all(p.get('initial_permission_conditions',{}).get('availableAbilitiesExact')is None or set(p['initial_permission_conditions']['availableAbilitiesExact'])==available for p in [ports[r['from_port']],ports[r['to_port']]])]
