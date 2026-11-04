"""Copy genuine current candidates; preserve all earlier program/content bytes."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import sys
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision059_v1 import rows,label,AUTH
from .finalize_revision058_v1 import folder_for as previous_folder
from .prepare_review045_v1 import at,end,axis
from .prepare_ideas_v1 import settle
from .prepare_revision058_v2 import jump

def prepare(r):
 n=label(r);f=core.REPO/r['outputDirectory'];assert not f.exists();old=previous_folder(r);d=core.read(old/'module.mapnote.json');cs=core.read(old/'physics-input-cases.json')['cases'];m=core.read(old/'migration.json');m.pop('holdoutPool',None);m.update(status='prepared_unverified',designVersion=r['designVersion']);impl=d['generationContract']['generation']['approvedImplementation'];impl.update(authorization=physics.artifact(AUTH/'request.json'),priorImplementation=physics.artifact(old/'module.mapnote.json'))
 for k in ['runtimeSource','decoderSource','observerSource','boundaryInputs']:impl.pop(k,None)
 d['generationContract']['validations']=[]
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];g=c['exit_port'];p=c['control_plan'];c['id']='approved-r059-'+n+'-'+c['route_spec']['id'];c['generation_rule']['registration_source']='pcg/manual_review/revision059_repair_author_v1.py';c['max_frames']=3600
  if n=='s02'and a=='B':p=[dict(op='wait',trigger=dict(after=1,state='repair_board_dodge',timeout=1800)),settle(272),cmd('jump'),cmd('jump_release',24),dict(op='wait',carrier='P',trigger=dict(after=1,state='carrier_supported',timeout=240)),dict(op='settle',target_x=272,revision_follow='P',repair_follow_dodge=True,carrier_offset=-30,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',trigger=dict(after=1,state='repair_takeoff',timeout=900)),cmd('jump'),cmd('jump_release',24),cmd('shoot',4,direction=[0,1]),dict(op='wait',carrier='P',trigger=dict(after=1,state='carrier_supported',timeout=240)),dict(op='wait',carrier='P',exit_y=170,trigger=dict(after=1,state='carrier_exit',timeout=1200))]+jump(64,24)+end(*g)
  if n=='s02':c['migration_boundary_plans']={'bottom_full_body_alignment':True}
  if n=='s11'and a=='B':
   cut=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('migration_goal')==[260,299,8,6]);p=[axis(0),cmd('jump'),dict(op='wait',observed_y=dict(direction='lte',value=390),trigger=dict(after=1,state='observed_height',timeout=90)),settle(400),cmd('jump_release',16),cmd('shoot',1,aim_cell=dict(kind='bell',id='common-bell',receiver='additional')),settle(264)]+p[cut:]
  c['control_plan']=p
  for k in ['recorded_frames','factory_evidence','module_sha256','noise']:c.pop(k,None)
 core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(d,cs));core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs));core.write(f/'migration.json',m);core.write(f/'parameters.json',dict(designVersion=r['designVersion'],previous=physics.artifact(old/'parameters.json'),unchangedGeometry=True,controls=[dict(route=c['route_spec'],control_plan=c['control_plan'])for c in cs]))
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:prepare(r)
