"""Test whether omitted native group ownership caused parked-phase corruption."""
import copy
from pcg.migration import core,physics
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .continue_revision063_v1 import rows,label,OUT
from .finalize_revision063_v1 import folder_for
def main():
 row=next(r for r in rows()if label(r)=='s04');f=folder_for(row);canonical=core.read(f/'physics-input-cases.json')['cases'];ref=core.read(f/'qualification.json')['report'];report=core.read(core.resolve_artifact(ref['path']));root=core.resolve_artifact(ref['path']).parent;inputs=[];lineage=[]
 for route,template in zip(report['routes'],canonical):
  phases={p['platform_id']:p['initial_phase']for p in template['moving_platforms']};targets={p for s in template['approved_hq_cells'] if s['kind']=='group_motion' for p in s['targets']};assert targets=={'P','Q'}
  cal=core.read(core.resolve_artifact(route['calibration']['path']));failures=[r for r in cal['rows'] if not r['purpose']['ok']]
  for before in failures[:(3 if route['routeId']=='B-to-T' else 1)]:
   e=before['evidence'];p=root/'physics'/(e['batch']+'.input.json');old=core.read(p)['cases'][e['index']];new=copy.deepcopy(old);changes=[]
   for deck in new['moving_platforms']:
    if deck['platform_id']in targets:
     changes.append(dict(platform=deck['platform_id'],incorrectRandomParkedPhase=deck['initial_phase'],authoredNativeParkedPhase=phases[deck['platform_id']]));deck['initial_phase']=phases[deck['platform_id']]
   new['id']+='-native-group-initial-phase';new['module_sha256']=physics.module_hash(new);inputs.append(new);lineage.append(dict(originalInput=physics.artifact(p),originalIndex=e['index'],changed=changes,enemyAndAimTimingNoiseUnchanged=True,controlProgramUnchanged=True))
 assert len(inputs)==4
 eng,cs,authors=physics._engine(f,'approved-r063-s04-native-group-sampler-diagnostic-v1',physics.FULL_PROTOCOL);checks=[]
 for c,r,e in eng.run(inputs,'native-group-sampler-diagnostic'):
  q=checked_purpose(physics.author_for(c),c,r);checks.append(dict(check=q,evidence=e));print('S04_NATIVE_GROUP_PHASE_DIAGNOSTIC',q['ok'],q['reasons'],flush=True)
 core.write(eng.out/'diagnosis.json',dict(passed=all(v['check']['ok']for v in checks),checks=checks,lineage=lineage,sameFrozenCandidate=True,newIndependentHoldout=False,ordinarySampler='workshop.evaluate.instantiate excludes native latches.ferry_id from parked-phase randomization, but omits custom group_motion.targets',nativeBinding='Original ModuleMovingPlatform.bind_bell_control; no snapping or clock/resource writes.'))
if __name__=='__main__':main()
