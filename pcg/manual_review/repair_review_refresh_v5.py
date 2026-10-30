"""Bounded next input revision, source and failures preserved."""
import copy,shutil,inspect,math
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd
from .probe_review_refresh_v1 import AUTH
from .prepare_review_refresh_v1 import end
from .repair_review_refresh_v3 import gunhop
IDS={'122','140','150','154','157','159'}
def prepare(row):
 n=row['reviewId'];folder=core.REPO/row['outputDirectory'];before=folder/'revisions/before-control-v5';before.mkdir(parents=True,exist_ok=False)
 for name in ('module.mapnote.json','cases.json','parameters.json','thumbnail.svg'):shutil.copy2(folder/name,before/name)
 doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'cases.json')['cases'];g=doc['generationContract']
 for c in cases:
  z=next(p for p in g['ports']if p['id']==c['route_spec']['to_port']);x,y=z['stagingPosition'];p=copy.deepcopy(c['control_plan'][:-3]);c['id']+='-control-v5';c['max_frames']=3600
  if n=='140':c['generation_rule']['registration_source']='pcg/manual_review/review_refresh_resource_v5.py'
  elif n=='150':
   for i,v in enumerate(p):
    if v.get('aim_cell',{}).get('id')=='design-ground-enemy-3':v['height_threshold']=685
  elif n=='154':p=gunhop(145,282,335,282,250,[-1,0],stationary=True)+[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=c['saws'][0]['source_id'],window=[.8,.9]),timeout=480))]+gunhop(300,282,520,282,235,[-math.sqrt(1-.02**2),.02])+gunhop(545,282,735,282,250,[-1,0],stationary=True)
  elif n=='157':p=[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=c['saws'][0]['source_id'],window=[0,.02]),timeout=600))]+gunhop(110,282,370,282,235,[-math.sqrt(1-.04**2),.04])+gunhop(370,282,690,282,235,[-math.sqrt(1-.04**2),.04])
  c['control_plan']=p+end(x,y)
 doc=godot_package.bind_case_behavior(doc,cases);g=doc['generationContract'];g['generation']['approvedImplementation'].update(repairSource=physics.artifact(__file__),runtimeSource=physics.artifact(physics.runner_for(cases[0],physics.author_for(cases[0]))),observerSource=physics.artifact(inspect.getsourcefile(physics.author_for(cases[0]).purpose)))
 core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True);core.write(folder/'cases.json',dict(cases=cases));params=core.read(folder/'parameters.json');params.update(controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])for c in cases]);core.write(folder/'parameters.json',params);print(n,'control-v5',flush=True)
if __name__=='__main__':
 for r in core.read(AUTH/'handoff.json')['rows']:
  if r['reviewId']in IDS:prepare(r)
