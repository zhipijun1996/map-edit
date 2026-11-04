"""Real optional chest detour after the complete four-carrier ascent."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,inspect
from pcg.migration import core,physics,godot_package,revision053_runtime_v1 as backend
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .continue_revision063_v1 import rows,label,OUT
from .finalize_revision063_v1 import folder_for
from .prepare_review045_v1 import at
def main():
 row=next(r for r in rows()if label(r)=='lift');old=folder_for(row);f=OUT/'fixtures/lift-optional-chest-v1';assert not f.exists();doc=core.read(old/'module.mapnote.json');case=core.read(old/'physics-input-cases.json')['cases'][0];case['id']+='-optional-chest';p=case['control_plan'];j=next(i for i,v in enumerate(p)if v['op']=='shoot'and v.get('direction')==[0,-1]);p[j:j]=at(208,46)+at(192,46);case.update(required_rewards=['reward'],expected_reward=4)
 doc=godot_package.bind_case_behavior(doc,[case]);core.write(f/'module.mapnote.json',doc);core.write(f/'cases.json',dict(cases=[case]));core.write(f/'physics-input-cases.json',dict(cases=[case]));core.write(f/'migration.json',core.read(old/'migration.json'));core.write(f/'parameters.json',dict(optionalRewardDetour=True,sourceModule=physics.artifact(old/'module.mapnote.json'),ownedGeometryChanged=False,sourceReward=case['reward_sites']))
 eng,cs,authors=physics._engine(f,'approved-r063-lift-optional-chest-v1',physics.FULL_PROTOCOL);recordings=[];checks=[]
 for c,raw,e in eng.run([physics.fresh(case,'reward-detour')],'real-chest-detour'):
  q=checked_purpose(authors[0],c,raw);checks.append(dict(check=q,evidence=e));assert q['ok'],q
  assert raw['workshop']['coins']==4 and any(e.get('type')=='chest_claim'and e.get('accepted')and e.get('amount')==4 for e in raw['workshop']['events']);recordings.append(physics._recording(c,raw))
 core.write(eng.out/'reward-check.json',dict(passed=True,rows=checks,ascentBeforeReward=True,actualCoins=4,originalSimpleRoomReward=True,originalWorldAndEnemyPreserved=True));core.write(f/'playback-cases.json',dict(cases=recordings));backend.compile_package(f/'module.mapnote.json',f/'playback-cases.json',f/'playable',stable_id=row['moduleId']+'-optional-chest');result=backend.run_package_validation(f/'playable');core.write(f/'package-result.json',result);assert result['passed']
 receipt=core.read(f/'playable/load-evidence/case-0/receipt.json');assert receipt['coins']==4 and receipt['hp']==5 and not receipt['damage']and not receipt['returns'];core.write(f/'reward-evidence.json',dict(passed=True,actualCoins=4,nativeReceipt=physics.artifact(f/'playable/load-evidence/case-0/receipt.json'),physicalProof=physics.artifact(eng.out/'reward-check.json'),scene=physics.artifact(f/'playable/demo.tscn'),formalQualification=False))
 from . import record_revision058_native_v2 as movies
 source=inspect.getsource(movies.run).replace("'-v2'if n=='42'else'-v1'","'-v1'").replace('revision058_native_movie_v1','revision060_native_movie_v2');ns={**movies.__dict__,'label':lambda r:'lift-chest','folder_for':lambda r:f,'OUT':OUT};exec(compile(source,__file__,'exec'),ns);ns['run'](row)
 print('LIFT_OPTIONAL_CHEST_NATIVE_4_COINS_PASS',flush=True)
if __name__=='__main__':main()
