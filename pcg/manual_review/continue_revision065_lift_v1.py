"""New explicitly approved relay geometry; old065 experiments never overwritten."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,subprocess
from pcg.migration import core,physics,godot_package
from .lift_idea_v1 import ID,decode
from .prepare_review045_v1 import at,end,axis
from pcg.prototype.workshop.rules import cmd
OUT=core.REPO/'feedback/manual-review/implementation-results/revision-065-v1';AUTH=OUT/'authorization'
ROOT=core.REPO/'pcg/manual_review/implementation/revision-065-drafts-v1';FINAL=core.REPO/'pcg/manual_review/implementation/revision-065-final-v1'
def rows():return core.read(AUTH/'handoff.json')['rows']
def label(row):return 'lift'
def wait(state,timeout=1200):return dict(op='wait',trigger=dict(after=1,state=state,timeout=timeout))
def settle(x):return dict(op='settle',target_x=x,deadband=.6,source_native_gain=5.5,trigger=dict(after=0))
def main():
 assert not AUTH.exists();row=copy.deepcopy(next(r for r in core.read('feedback/manual-review/implementation-handoff-v1.json')['rows']if r['reviewId']==ID));assert core.sha(row['designFile'])==row['designFileSha256']
 row['outputDirectory']=core.relative(ROOT/ID);f=core.REPO/row['outputDirectory'];base=core.REPO/'pcg/manual_review/implementation/revision-063-final-v1'/ID
 core.write(AUTH/'request.json',dict(verbatim='好的，加一个中继台',acceptedProposal='中层左侧增加64px中继台，台面y544；先不延长停留。',startCommit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),scope=[ID],newExplicitGeometryApproval=True,design=physics.artifact(row['designFile']),designReceipt=physics.artifact('feedback/manual-review/lift-relay-r065-receipt.json'),geometry=dict(added=dict(id='relay-dock',x=0,y=544,w=64,h=12),allExistingObjectsUnchanged=True),budget=dict(maximumExecutedSemanticVersions=12,diagnosticsPerRouteVersion=18,screen=dict(clean=1,mild=6,moderate=6,minimumModeratePasses=5,seed=271028029),selectedFormalCandidates=1,additionalFixtures=48,maximumNewGodotCases=5000),protocol=physics.artifact(physics.FULL_PROTOCOL),selection='First unchanged clean, screen and native passing candidate. One selected formal version, no holdout tuning or reroll. All failures retained.',originalPhysics=True,excluded='Other eleven prior modules; pending designs; speed/phase/dwell/enemy/hazard/interface changes.'))
 core.write(AUTH/'handoff.json',dict(rows=[row]));core.write(AUTH/'design.json',core.read(row['designFile']))
 doc=core.read(base/'module.mapnote.json');oldcases=core.read(base/'physics-input-cases.json')['cases'];g=doc['generationContract'];relay=copy.deepcopy(next(o for o in core.read(row['designFile'])['visualObjects']if o['id']=='relay-dock'));relay['sourceIndex']=2;doc['objects'].append(relay)
 g['space']['occupancy']['objectIds'].append(relay['id']);g['composition']['cells'].append(dict(id=relay['id'],objectIds=[relay['id']],contentVersion='sha256:'+'0'*64))
 impl=g['generation']['approvedImplementation'];impl.update(authorization=physics.artifact(AUTH/'request.json'),designFile=physics.artifact(row['designFile']),designVersion=row['designVersion'],priorImplementation=physics.artifact(base/'module.mapnote.json'));impl.pop('boundaryInputs',None)
 for r in g['routes']:r.update(availability='UNKNOWN',evidenceStatus='UNKNOWN',validationIds=[])
 for r in g['relations']:r['status']='UNKNOWN'
 g['validations']=[];cs=[]
 for c in oldcases:
  for k in ['recorded_frames','module_sha256','factory_evidence','noise']:c.pop(k,None)
  c.update(copy.deepcopy(decode(doc)));c['id']='approved-r065-lift-'+c['route_spec']['id'];c['approved_implementation']['designVersion']=row['designVersion'];c['generation_rule']['registration_source']='pcg/manual_review/revision065_lift_author_v1.py';c['max_frames']=3600
  if c['route_spec']['to_port']=='B':
   ix=len(c['platforms']);c['platforms'].append([144,-32,96,12]);c['one_way_platform_indices'].append(ix);c['explicit_exit_neighbor']['index']=ix
   c['control_plan']=at(192,846)+[wait('revision_lift_clear'),wait('relay065_choose_lower',2400),settle(20),wait('relay065_edge'),axis(0),cmd('jump'),cmd('jump_release',24),cmd('shoot',4,direction=[0,1]),wait('revision_lift_above_g1'),settle(66),wait('revision_lift_lower_support'),wait('relay065_deboard'),settle(20)]+at(20,526)+[wait('relay065_choose_upper',2400),axis(0),cmd('jump'),cmd('jump_release',24),wait('relay065_above_upper'),settle(66),wait('revision_lift_upper_support'),wait('relay065_finish'),axis(0),cmd('jump'),settle(20),cmd('jump_release',24),dict(op='shoot',direction=[-.87,.49],revision_final_shot=True,trigger=dict(after=0,state='relay065_final_shot',timeout=180)),settle(192)]+end(192,46)+[dict(op='shoot',aim_cell=dict(kind='bell',id='top-exit-bell'),direction=[0,-1],trigger=dict(after=4,state='grounded_shot_ready',timeout=300)),cmd('wait',12),cmd('jump'),cmd('jump_release',24)]+end(192,-50)
  cs.append(c)
 doc=godot_package.bind_case_behavior(doc,cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs));meta=core.read(base/'migration.json');meta.pop('holdoutPool',None);meta.update(status='prepared_unverified',designVersion=row['designVersion']);core.write(f/'migration.json',meta);core.write(f/'parameters.json',dict(designVersion=row['designVersion'],content=decode(doc),controls=[dict(route=c['route_spec'],control_plan=c['control_plan'])for c in cs],authorization=physics.artifact(AUTH/'request.json')))
 print('R065_RELAY_PREPARED',row['designVersion'],flush=True)
if __name__=='__main__':main()
