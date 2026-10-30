"""Preserve original route commands, then append real outward walking.

Replays only the affected horizontal continuations. Reuses every original
calibration and holdout byte, with strict supplemental lineage and no reroll.
"""
import copy,os
from pcg.migration import core,physics,review_boundary_repair_v5,pool_protocols
from .probe_review_refresh_v1 import AUTH

def run(row):
 n=row['reviewId'];v='v2'if n in('140','154')else'v1';folder=core.REPO/('pcg/manual_review/implementation/review-refresh-final-'+v)/row['moduleId'];doc=core.read(folder/'module.mapnote.json')
 pointer=next(p for p in [folder/'qualification-repaired.json',folder/'qualification-reanalysed.json',folder/'qualification.json']if p.exists());ref=core.read(pointer)['report'];source=core.resolve_artifact(ref['path']);old=core.read(source);original=source.parent
 protocol=pool_protocols.runtime_protocol(folder)if old.get('holdoutPool')else physics.FULL_PROTOCOL;eng,cases,_=physics._engine(folder,'approved-r024-'+n+'-continuous-flow-v2',protocol);probes=[physics.continuous_exit(c,doc)for c in cases];probes=[c for c in probes if c['migration_probe']['normal'][0]]
 core.write(eng.out/'repair-protocol.json',dict(maximumAttempts=len(probes),newIndependentHoldout=False,scope='Complete the unchanged original route and its real landing before appended outward movement. No new calibration, holdout, route selection or threshold changes.'))
 rows=[]
 for c,r,e in eng.run(probes,'original-route-then-exit-v2'):
  q=physics.crossing(c,r);rows.append(dict(id=c['id'],probe=c['migration_probe'],check=q,evidence=e));print(n,c['route_spec']['id'],q['passed'],r['reason'],flush=True)
 core.write(eng.out/'repair-checks.json',rows);assert all(v['check']['passed']for v in rows)
 for f in (eng.out/'physics').iterdir():os.link(f,original/'physics'/f.name)
 core.write(original/'batches-continuation-v2.json',core.read(core.resolve_artifact(old['batches']['path']))+core.read(eng.out/'batches.json'));fixes={v['id']:v for v in rows};core.write(original/'boundary-probes-continuation-v2.json',[fixes.get(v['id'],v)for v in core.read(core.resolve_artifact(old['probes']['path']))])
 report=copy.deepcopy(old);report.pop('offlineAnalysis',None);report.update(passed=True,actualAttempts=old['actualAttempts']+len(rows),batches=physics.artifact(original/'batches-continuation-v2.json'),probes=physics.artifact(original/'boundary-probes-continuation-v2.json'),boundaryRepair=dict(schema=review_boundary_repair_v5.SCHEMA,sourceReport=ref,repairBinding=physics.artifact(eng.out/'source_binding.json'),repairBatches=physics.artifact(eng.out/'batches.json'),repairChecks=physics.artifact(eng.out/'repair-checks.json'),newPhysicsAttempts=len(rows),newIndependentHoldout=False));target=original/'migration-physics-continuation-v2.json';core.write(target,report);proof=physics.artifact(target);physics.verify_report(folder,proof,deep=True);core.write(folder/'qualification-continuation-v2.json',dict(passed=True,report=proof,newPhysicsAttempts=len(rows),newIndependentHoldout=False));print(n,'DEEP_VERIFIED',flush=True)
if __name__=='__main__':
 for row in core.read(AUTH/'handoff.json')['rows']:
  if row['reviewId']!='157':run(row)
