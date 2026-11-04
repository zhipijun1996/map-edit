"""Earlier upper-ferry transfer and the first clean precision-gear candidate."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,shutil,inspect
from pcg.migration import core,physics,godot_package
from .probe_review_refresh_v1 import AUTH

def main():
 for row in core.read(AUTH/'handoff.json')['rows']:
  n=row['reviewId']
  if n not in {'157'}:continue
  folder=core.REPO/row['outputDirectory'];before=folder/'revisions/before-control-v13';before.mkdir(parents=True,exist_ok=False)
  for name in ('module.mapnote.json','cases.json','parameters.json','thumbnail.svg'):shutil.copy2(folder/name,before/name)
  doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'cases.json')['cases']
  for c in cases:
   c['id']+='-control-v13'
   if n=='122'and c['route_spec']['from_port']=='entry':c['control_plan']=[v for v in c['control_plan']if v['op']!='shoot']
   elif n=='157':
    for v in c['control_plan']:
     if v['op']=='settle'and v.get('target_x')==345:v['target_x']=315
     if v.get('trigger',{}).get('migration_goal')==[340,278,10,8]:v['trigger']['migration_goal']=[310,278,10,8]
  doc=godot_package.bind_case_behavior(doc,cases);doc['generationContract']['generation']['approvedImplementation'].update(repairSource=physics.artifact(__file__),runtimeSource=physics.artifact(physics.runner_for(cases[0],physics.author_for(cases[0]))),observerSource=physics.artifact(inspect.getsourcefile(physics.author_for(cases[0]).purpose)))
  core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True);core.write(folder/'cases.json',dict(cases=cases));p=core.read(folder/'parameters.json');p.update(controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])for c in cases]);core.write(folder/'parameters.json',p)
if __name__=='__main__':main()
