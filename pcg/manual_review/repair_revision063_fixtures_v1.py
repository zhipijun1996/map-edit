"""Append four failed ingress fixtures; canonical/held-out evidence is untouched."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,sys,shutil
from pcg.migration import core,physics,pool_protocols
from pcg.migration.revision063_fixture_v2 import adjust
from pcg.migration.revision063_fixture_lineage_v1 import SCHEMA,validate_lineage
from .continue_revision063_v1 import rows,label,OUT
from .finalize_revision063_v1 import folder_for
def run(row):
 n=label(row);f=folder_for(row);original_q=core.read(f/'qualification.json');source=core.resolve_artifact(original_q['report']['path']);report=core.read(source);before=core.read(core.resolve_artifact(report['probes']['path']));bad=[q for q in before if not q['check']['passed']];assert len(bad)==4
 inputs=[];lineage=[]
 for q in bad:
  e=q['evidence'];path=source.parent/'physics'/(e['batch']+'.input.json');case=copy.deepcopy(core.read(path)['cases'][e['index']]);assert adjust(case);case['module_sha256']=physics.module_hash(case);inputs.append(case);lineage.append(dict(originalInput=physics.artifact(path),originalIndex=e['index']))
 eng,cs,authors=physics._engine(f,'approved-r063-'+n+'-fixture-repair-v1',pool_protocols.runtime_protocol(f));replacements={};checks=[]
 for i,(case,raw,e)in enumerate(eng.run(inputs,'r063-fixture-repair')):
  check=physics.crossing(case,raw);checks.append(dict(id=case['id'],check=check,evidence=e));replacements[case['id']]=dict(id=case['id'],probe=case['migration_probe'],check=check,evidence=e)
  lineage[i].update(correctedInput=physics.artifact(eng.out/'physics'/(e['batch']+'.input.json')),correctedIndex=e['index'])
  print(n,'FIXTURE',case['id'].split('-migration-')[-1],check['passed'],raw['reason'],flush=True)
 passed=all(q['check']['passed']for q in checks);core.write(eng.out/'fixture-check.json',dict(passed=passed,rows=lineage,checks=checks,replacedProbeIds=[q['id']for q in bad],canonicalProgramsChanged=False,newIndependentHoldout=False));assert passed,'native_fixture_repair_failed_raw_preserved'
 for file in (eng.out/'physics').iterdir():
  if file.is_file():
   target=source.parent/'physics'/file.name;assert not target.exists();shutil.copy2(file,target);assert core.sha(target)==core.sha(file)
 extra=core.read(eng.out/'batches.json');allbatches=core.read(core.resolve_artifact(report['batches']['path']))+extra;bp=source.parent/'batches-fixture-corrected-v1.json';pp=source.parent/'boundary-probes-fixture-corrected-v1.json';rp=source.parent/'migration-physics-fixture-corrected-v1.json'
 core.write(bp,allbatches);after=[replacements.get(q['id'],q)for q in before];core.write(pp,after)
 updated=copy.deepcopy(report);updated.update(passed=all(r['passed']for r in report['routes']) and all(q['check']['passed']for q in after) and not any(c['adjudication']['invalidates_design']for c in core.read(core.resolve_artifact(report['counterexamples']['path']))),probes=physics.artifact(pp),batches=physics.artifact(bp),actualAttempts=report['actualAttempts']+len(inputs),fixtureCorrection=dict(schema=SCHEMA,sourceReport=original_q['report'],sourceProbes=report['probes'],supplementBinding=physics.artifact(eng.out/'source_binding.json'),supplementBatches=physics.artifact(eng.out/'batches.json'),supplementChecks=physics.artifact(eng.out/'fixture-check.json'),builder=physics.artifact(core.REPO/'pcg/migration/revision063_fixture_v2.py'),newPhysicsAttempts=4,newIndependentHoldout=False))
 core.write(rp,updated);validate_lineage(updated,rp)
 core.write(f/'qualification-before-fixture-repair.json',original_q);core.write(f/'qualification.json',dict(passed=updated['passed'],actualAttempts=updated['actualAttempts'],report=physics.artifact(rp),originalFailure=original_q,canonicalAndHeldoutInputsChanged=False,newIndependentHoldout=False))
 print(n,'AFTER_FIXTURE_REPAIR',updated['passed'],updated['actualAttempts'],flush=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:run(r)
