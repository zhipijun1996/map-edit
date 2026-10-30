"""Retain tested physics; apply approved interface deltas and control repair."""
import copy
from pcg.migration import core,physics,godot_package
from .continue_revision063_v1 import rows,label,AUTH,ROOT
from .revision063_content_v1 import decode
from .prepare_review045_v1 import at
from .prepare_ideas_v1 import settle
def old_folder(r):
 n=label(r);round='053' if n=='lift' else '058' if n.startswith(('lt-','lb-')) else '060' if n=='hq09' else '062'
 return core.REPO/f'pcg/manual_review/implementation/revision-{round}-final-v1'/r['moduleId']
def main():
 for r in rows():
  n=label(r);old=old_folder(r);f=core.REPO/r['outputDirectory'];assert not f.exists()
  doc=core.read(old/'module.mapnote.json');cs=core.read(old/'physics-input-cases.json')['cases'];design=core.read(r['designFile']);g=doc['generationContract'];impl=g['generation']['approvedImplementation']
  impl.update(authorization=physics.artifact(AUTH/'request.json'),priorImplementation=physics.artifact(old/'module.mapnote.json'),designFile=physics.artifact(r['designFile']),designVersion=r['designVersion'],productionApproval=False)
  for k in ['boundaryInputs','runtimeSource','decoderSource','observerSource']:impl.pop(k,None)
  if n=='hq09':
   for p in g['ports']:
    if p['id']=='T':
     p['permission']='OUTPUT';p['permissionStatus']='declared_pending_revision_validation';p['initialPermissionConditions']=dict(availableAbilitiesExact=cs[0]['capabilities'],requiresRevalidationWithAdditionalUpwardAbilities=True,reason='Initial extended upper thorns; user declares upper port OUTPUT only.')
   g['routes']=[v for v in g['routes'] if v['from']!='T'];cs=[c for c in cs if c['route_spec']['from_port']!='T']
  if n=='s09':
   changes={v['id']:v for v in design['visualObjects']}
   for o in doc['objects']:
    if o['id'] in changes and o['id'] in ['lower-wall','lower-rim']:
     for k in ['x','y','w','h']:o[k]=changes[o['id']][k]
   # IDs and exact changed fields are audited below rather than guessed.
   byid={o['id']:o for o in doc['objects']}
   for key,v in changes.items():
    if key in byid and v.get('y') in [288,304] and byid[key].get('y') in [272,288]:
     for k in ['x','y','w','h']:byid[key][k]=v[k]
  for route in g['routes']:route.update(availability='UNKNOWN',evidenceStatus='UNKNOWN',validationIds=[])
  allowed_routes={v['id'] for v in g['routes']}
  for v in g['relations']:
   v['status']='UNKNOWN';v['routeIds']=[i for i in v.get('routeIds',[]) if i in allowed_routes]
  g['validations']=[];content=decode(doc)
  for c in cs:
   for k in ['noise','module_sha256','factory_evidence','recorded_frames']:c.pop(k,None)
   c.update(copy.deepcopy(content));c['id']='approved-r063-'+n+'-'+c['route_spec']['id'];c['max_frames']=max(c['max_frames'],3600)
   c['approved_implementation'].update(designVersion=r['designVersion'])
   c['legal_port_mouths']=[{k:p[k] for k in ['id','position','face','surface','permission']} for p in g['ports']]
   if n=='hq07':
    c['generation_rule']['registration_source']='pcg/manual_review/revision063_author_v1.py'
    p=c['control_plan']
    if c['route_spec']['from_port']=='R':
     j=next(i for i,v in enumerate(p) if v.get('trigger',{}).get('state')=='pair_desired')
     k=next(i for i,v in enumerate(p) if v.get('fight_enemy')=='right-charger') if any(v.get('fight_enemy')=='right-charger' for v in p) else next(i for i,v in enumerate(p) if v.get('trigger',{}).get('state')=='revision_clear')
     fight=copy.deepcopy(p[k]);fight['guard_x']=800
     p=at(836,334)+p[1:j+1]+at(800,334)+[fight]+p[k+1:]
    for v in p:
     if v.get('trigger',{}).get('state')=='pair_desired' and 'direction' not in v:v['trigger']['state']='r063_pair_observe'
    c['control_plan']=p
  doc=godot_package.bind_case_behavior(doc,cs)
  core.write(f/'module.mapnote.json',doc);core.write(f/'cases.json',dict(cases=cs))
  meta=core.read(old/'migration.json');meta.pop('holdoutPool',None);meta.update(status='prepared_unverified',designVersion=r['designVersion']);core.write(f/'migration.json',meta)
  core.write(f/'parameters.json',dict(designVersion=r['designVersion'],content=content,authorization=physics.artifact(AUTH/'request.json'),previous=physics.artifact(old/'parameters.json'),controls=[dict(route=c['route_spec'],control_plan=c['control_plan']) for c in cs]));core.contract(f/'module.mapnote.json',refresh=True);print(n,'PREPARED',len(cs),flush=True)
if __name__=='__main__':main()
