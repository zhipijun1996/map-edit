"""Cross the small slalom gear during the initial safe part of a downward burst."""
import copy,shutil,inspect,math
from pcg.migration import core,physics,godot_package
from .probe_review_refresh_v1 import AUTH
from .prepare_review_refresh_v1 import at,end
from .repair_review_refresh_v3 import gunhop

def main():
 row=next(r for r in core.read(AUTH/'handoff.json')['rows']if r['reviewId']=='154');folder=core.REPO/row['outputDirectory'];before=folder/'revisions/before-control-v14';before.mkdir(parents=True,exist_ok=False)
 for name in ('module.mapnote.json','cases.json','parameters.json','thumbnail.svg'):shutil.copy2(folder/name,before/name)
 doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'cases.json')['cases'];c=cases[0];c['id']+='-control-v14';z=next(p for p in doc['generationContract']['ports']if p['id']==c['route_spec']['to_port']);x,y=z['stagingPosition']
 c['control_plan']=gunhop(145,282,335,282,250,[-1,0],stationary=True)+[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=c['saws'][0]['source_id'],window=[.05,.08]),timeout=480))]+gunhop(418,282,520,282,235,[-math.sqrt(1-.04**2),-.04],stationary=True)+gunhop(545,282,735,282,250,[-1,0],stationary=True)+end(x,y)
 doc=godot_package.bind_case_behavior(doc,cases);doc['generationContract']['generation']['approvedImplementation'].update(repairSource=physics.artifact(__file__),runtimeSource=physics.artifact(physics.runner_for(c,physics.author_for(c))),observerSource=physics.artifact(inspect.getsourcefile(physics.author_for(c).purpose)))
 core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True);core.write(folder/'cases.json',dict(cases=cases));p=core.read(folder/'parameters.json');p.update(controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])]);core.write(folder/'parameters.json',p)
if __name__=='__main__':main()
