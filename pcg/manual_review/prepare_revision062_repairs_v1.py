import copy
from pcg.migration import core,godot_package,physics
from pcg.prototype.workshop.rules import cmd
from .continue_revision062_v1 import rows,label,AUTH
from .revision062_repair_content_v1 import decode
from .finalize_revision060_v1 import folder_for as old60
from .finalize_revision061_v1 import folder_for as old61
from .prepare_revision060_v1 import wait,follow,supported
from .prepare_review045_v1 import at,end,axis
from .prepare_ideas_v1 import settle

def main():
 for row in rows():
  n=label(row)
  if row['implementationMode']!='repair_input_policy':continue
  old=(old60 if n.startswith('hq')else old61)(row);f=core.REPO/row['outputDirectory'];assert not f.exists();doc=core.read(old/'module.mapnote.json');cs=core.read(old/'physics-input-cases.json')['cases'];meta=core.read(old/'migration.json');meta.pop('holdoutPool',None);meta['status']='prepared_unverified';g=doc['generationContract'];g['validations']=[]
  for r in g['routes']:r.update(availability='UNKNOWN',evidenceStatus='UNKNOWN',validationIds=[])
  for r in g['relations']:r['status']='UNKNOWN'
  impl=g['generation']['approvedImplementation'];impl.update(authorization=physics.artifact(AUTH/'request.json'),priorImplementation=physics.artifact(old/'module.mapnote.json'))
  for k in ['boundaryInputs','runtimeSource','decoderSource','observerSource']:impl.pop(k,None)
  for c in cs:
   for k in ['noise','module_sha256','factory_evidence','recorded_frames']:c.pop(k,None)
   c['generation_rule']['registration_source']='pcg/manual_review/revision062_author_v1.py';c['id']='approved-r062-'+n+'-'+c['route_spec']['id'];c['max_frames']=3600;p=c['control_plan'];a,z=c['route_spec']['from_port'],c['route_spec']['to_port']
   if n=='hq01'and z=='L':
    for v in p:
     if v.pop('group_transfer_out',False):v['r062_group_transfer_out']=True
     if v.get('trigger',{}).get('state')=='r060_group_left':v['trigger']['state']='r062_left_window'
    j=max(i for i,v in enumerate(p)if v.get('group_command')is True and v.get('group_carrier')=='P');p[j-1]['r062_left_pose_entry']=True;k=max(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='r060_group_running'and v.get('running')is False);p=p[:k+1]+[wait('r062_left_pose_ok',timeout=120),follow('P',-40),supported('P'),dict(op='shoot',direction=[1,0],trigger=dict(after=1,state='grounded_shot_ready',timeout=180)),settle(24)]+end(24,334)
   if (n=='hq01'and z=='T')or(n=='rs12'and z=='T'):
    target='r060_top_aligned'if n=='hq01'else'r061_top_shot';j=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')==target);k=j-3;assert p[k]['op']=='settle'and p[k+1]['op']=='jump';p[j]['trigger']['state']='r062_top_vertical';p[j]['direction']=[0,1];p[j-1].pop('adaptive_q_hold',None);p[j-1]['trigger']['after']=24;p=p[:k]+[follow('Q',-28),supported('Q')]+p[k:]
   if n=='hq03'and a=='R':
    j=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='r060_fight');p=at(460,206)+[settle(368)]+at(368,270)+p[j:]
   if n=='hq07'and a=='L':
    j=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='descending_height');p[j+1]['trigger']=copy.deepcopy(p[j]['trigger']);p[j+1]['height_threshold']=p[j]['height_threshold'];p.pop(j)
   if n=='rs10'and a=='B':
    # Keep the successful B→low hop; replace only the two lateral recoil launches.
    j=next(i for i,v in enumerate(p)if v['op']=='settle'and v.get('target_x')==112 and i+1<len(p)and p[i+1]['op']=='jump');p=p[:j]+at(320,478)+[axis(0),cmd('jump'),settle(112),cmd('jump_release',24),cmd('shoot',1,direction=[.94,.341174442])]+at(112,350)+at(88,350)+[axis(0),cmd('jump'),settle(336),cmd('jump_release',24),cmd('shoot',0,direction=[-.85,.5267826876])]+end(336,206)
   if n=='rs12'and a=='R':
    j=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='observed_height'and v.get('observed_y',{}).get('value')==100);p[j+1].update(direction=[.9682458366,.25],observed_y=copy.deepcopy(p[j]['observed_y']),trigger=dict(after=1,state='observed_height',timeout=120));p.pop(j)
   c['control_plan']=p
  doc=godot_package.bind_case_behavior(doc,cs);core.write(f/'module.mapnote.json',doc);core.write(f/'cases.json',dict(cases=cs));core.write(f/'migration.json',meta);core.write(f/'parameters.json',dict(designVersion=row['designVersion'],content=decode(doc),authorization=physics.artifact(AUTH/'request.json'),previous=physics.artifact(old/'parameters.json'),geometryChanged=False,controls=[dict(route=c['route_spec'],control_plan=c['control_plan'])for c in cs]));core.contract(f/'module.mapnote.json',refresh=True);print(n,'REPAIR_PREPARED',len(cs),flush=True)
if __name__=='__main__':main()
