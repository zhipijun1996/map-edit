"""Bounded controls preserving approved terrain, ports and live enemies."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,shutil,inspect
from pcg.migration import core,physics,godot_package
from pcg.prototype.workshop.rules import cmd,settle
from .probe_review_refresh_v1 import AUTH
from .prepare_review_refresh_v1 import at,end,leap
IDS={'122','150','159'}
def prepare(row):
 n=row['reviewId'];folder=core.REPO/row['outputDirectory'];before=folder/'revisions/before-control-v7';before.mkdir(parents=True,exist_ok=False)
 for name in ('module.mapnote.json','cases.json','parameters.json','thumbnail.svg'):shutil.copy2(folder/name,before/name)
 doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'cases.json')['cases'];g=doc['generationContract']
 for c in cases:
  z=next(p for p in g['ports']if p['id']==c['route_spec']['to_port']);x,y=z['stagingPosition'];p=copy.deepcopy(c['control_plan'][:-3]);c['id']+='-control-v7'
  if n=='122'and c['route_spec']['from_port']=='entry':
   p=p[:24]+[settle(390),cmd('jump'),dict(op='shoot',height_threshold=385,direction=[1,0],trigger=dict(state='height_at_most',timeout=100))]+at(390,380)+[cmd('jump_release')]
  elif n=='150':
   # More rising margin on the vertical one-way ascent under input aim noise.
   for v in p:
    if v.get('direction')==[0,1]:v['height_threshold']=680;v['direction']=[0,1]
   # Use the current stable bank rather than a toe takeoff for ordinary hops.
   for i,v in enumerate(p):
    if v['op']=='jump_release'and v.get('height_threshold')==400:v['height_threshold']=410
  elif n=='159':
   # Final diver is shot from a bank whose real leftward recoil remains on it.
   for i,v in enumerate(p):
    if v.get('skip_if_enemy_dead')=='design-air-enemy-3':
     if v['op']=='shoot':v['height_threshold']=600
    if v['op']=='settle'and v.get('target_x')==50 and i>=250:v['target_x']=85
    if i>=250 and v.get('trigger',{}).get('migration_goal')==[45,738,10,8]:v['trigger']['migration_goal']=[80,738,10,8]
  c['control_plan']=p+end(x,y)
 doc=godot_package.bind_case_behavior(doc,cases);g=doc['generationContract'];g['generation']['approvedImplementation'].update(repairSource=physics.artifact(__file__),runtimeSource=physics.artifact(physics.runner_for(cases[0],physics.author_for(cases[0]))),observerSource=physics.artifact(inspect.getsourcefile(physics.author_for(cases[0]).purpose)))
 core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True);core.write(folder/'cases.json',dict(cases=cases));params=core.read(folder/'parameters.json');params.update(controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])for c in cases]);core.write(folder/'parameters.json',params);print(n,'control-v7',flush=True)
if __name__=='__main__':
 for r in core.read(AUTH/'handoff.json')['rows']:
  if r['reviewId']in IDS:prepare(r)
