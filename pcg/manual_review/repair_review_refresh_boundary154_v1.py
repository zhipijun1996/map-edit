"""Only malformed exit fixtures are rerun; all original holdout bytes reused."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,copy,os
from pcg.migration import core,physics,review_boundary_repair_v4,pool_protocols
from .probe_review_refresh_v1 import AUTH

def run(row):
 n=row['reviewId'];v='v2';folder=core.REPO/('pcg/manual_review/implementation/review-refresh-final-'+v)/row['moduleId'];doc=core.read(folder/'module.mapnote.json');original=core.REPO/'pcg/results'/('approved-r024-'+n+'-qualified-final-'+v);old=core.read(original/'migration-physics.json');bad={p['id']for p in core.read(original/'boundary-probes.json')if not p['check']['passed']};assert len(bad)==1
 protocol=pool_protocols.runtime_protocol(folder)if old.get('holdoutPool')else physics.FULL_PROTOCOL;eng,cases,_=physics._engine(folder,'approved-r024-'+n+'-boundary-repair-v1',protocol);probes=[physics.continuous_exit(c,doc)for c in cases];probes=[c for c in probes if c['id']in bad];assert len(probes)==len(bad)
 core.write(eng.out/'repair-protocol.json',dict(maximumAttempts=len(probes),newIndependentHoldout=False,scope='Only rejected frame budgets and prematurely retargeted descent docks; original calibration, holdout, nominal inputs, engine and geometry unchanged'))
 rows=[]
 for c,r,e in eng.run(probes,'continuous-fixture-repair'):
  q=physics.crossing(c,r);rows.append(dict(id=c['id'],probe=c['migration_probe'],check=q,evidence=e));print(n,c['route_spec']['id'],q['passed'],r['reason'],flush=True)
 core.write(eng.out/'repair-checks.json',rows);assert all(v['check']['passed']for v in rows)
 for f in (eng.out/'physics').iterdir():os.link(f,original/'physics'/f.name)
 core.write(original/'batches-fixture-repair-v1.json',core.read(original/'batches.json')+core.read(eng.out/'batches.json'));fixes={v['id']:v for v in rows};core.write(original/'boundary-probes-fixture-repair-v1.json',[fixes.get(v['id'],v)for v in core.read(original/'boundary-probes.json')])
 report=copy.deepcopy(old);report.update(passed=True,actualAttempts=old['actualAttempts']+len(rows),batches=physics.artifact(original/'batches-fixture-repair-v1.json'),probes=physics.artifact(original/'boundary-probes-fixture-repair-v1.json'),boundaryRepair=dict(schema=review_boundary_repair_v4.SCHEMA,sourceReport=physics.artifact(original/'migration-physics.json'),repairBinding=physics.artifact(eng.out/'source_binding.json'),repairBatches=physics.artifact(eng.out/'batches.json'),repairChecks=physics.artifact(eng.out/'repair-checks.json'),newPhysicsAttempts=len(rows),newIndependentHoldout=False));target=original/'migration-physics-fixture-repair-v1.json';core.write(target,report);proof=physics.artifact(target);physics.verify_report(folder,proof,deep=True);core.write(folder/'qualification-repaired.json',dict(passed=True,report=proof,newPhysicsAttempts=len(rows),newIndependentHoldout=False));print(n,'DEEP_VERIFIED',flush=True)
if __name__=='__main__':
 for row in core.read(AUTH/'handoff.json')['rows']:
  if row['reviewId']in {'154'}:run(row)
