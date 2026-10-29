"""Two corrected native seam placements; original 50 nominal trials reused."""
import copy,os
from pcg.migration import core,physics,review_boundary_repair_v8 as lineage,pool_protocols
from pcg.manual_review.continue_revision053_v1 import rows
from pcg.manual_review.finalize_revision053_v2 import folder_for
r=next(r for r in rows()if r['reviewId']=='50');folder=folder_for(r);original=core.REPO/'pcg/results/approved-r053-50-qualified-final-v1';old=core.read(original/'migration-physics.json');bad={p['id']for p in core.read(original/'boundary-probes.json')if not p['check']['passed']};assert len(bad)==2
protocol=pool_protocols.runtime_protocol(folder)if old.get('holdoutPool')else physics.FULL_PROTOCOL;eng,cs,_=physics._engine(folder,'approved-r053-50-oneway-fixture-v1',protocol);doc=core.read(folder/'module.mapnote.json');cases=[c for c in physics.seam_cases(cs[0],doc)if c['id']in bad];assert len(cases)==2
core.write(eng.out/'repair-protocol.json',dict(maximumAttempts=2,newIndependentHoldout=False,reason='Only positive2px starts were initialized inside the one-way top; use distinct -4px above-top starts. Player, geometry, abilities, nominal program and all original seeds/trials unchanged.'))
checks=[]
for c,raw,e in eng.run(cases,'valid-oneway-top-starts'):checks.append(dict(id=c['id'],probe=c['migration_probe'],check=physics.crossing(c,raw),evidence=e))
core.write(eng.out/'repair-checks.json',checks);assert all(c['check']['passed']for c in checks)
for p in (eng.out/'physics').iterdir():os.link(p,original/'physics'/p.name)
core.write(original/'batches-oneway-repair-v1.json',core.read(original/'batches.json')+core.read(eng.out/'batches.json'));fixes={p['id']:p for p in checks};core.write(original/'probes-oneway-repair-v1.json',[fixes.get(p['id'],p)for p in core.read(original/'boundary-probes.json')])
report=copy.deepcopy(old);report.update(passed=True,actualAttempts=old['actualAttempts']+2,batches=physics.artifact(original/'batches-oneway-repair-v1.json'),probes=physics.artifact(original/'probes-oneway-repair-v1.json'),boundaryRepair=dict(schema=lineage.SCHEMA,sourceReport=physics.artifact(original/'migration-physics.json'),repairBinding=physics.artifact(eng.out/'source_binding.json'),repairBatches=physics.artifact(eng.out/'batches.json'),repairChecks=physics.artifact(eng.out/'repair-checks.json'),newPhysicsAttempts=2,newIndependentHoldout=False));target=original/'migration-physics-oneway-repair-v1.json';core.write(target,report);proof=physics.artifact(target);physics.verify_report(folder,proof,deep=True);core.write(folder/'qualification-repaired.json',dict(passed=True,report=proof,newPhysicsAttempts=2,newIndependentHoldout=False));print('50_REPAIRED_DEEP_PASS')
