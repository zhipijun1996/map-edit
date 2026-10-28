"""Append one actual exit-dock repair in the reserved run, preserving its trials."""
import copy,os
from pcg.migration import core,physics,review_boundary_repair_v3,pool_protocols
from .finalize_first40_repair17_v2 import AUTH,folder_for

def main():
    row=next(r for r in core.read(AUTH/'handoff.json')['rows']if r['reviewId']=='17');folder=folder_for(row);doc=core.read(folder/'module.mapnote.json');original=core.REPO/'pcg/results/approved-b040-17-qualified-first40-repair17-v2';old=core.read(original/'migration-physics.json')
    protocol=pool_protocols.runtime_protocol(folder);eng,cases,_=physics._engine(folder,'approved-b040-17-exit-dock-repair-v1',protocol)
    core.write(eng.out/'protocol.json',dict(maximumAttempts=1,newIndependentHoldout=False,scope='complete the actual C landing and 12-coin claim before crossing its side aperture; no new calibration or held-out execution'))
    probe=physics.continuous_exit(cases[0],doc);results=[]
    for c,r,e in eng.run([probe],'earned-C-exit-dock-repair'):
        q=physics.crossing(c,r);results.append(dict(id=c['id'],probe=c['migration_probe'],check=q,evidence=e));print(q,flush=True)
    core.write(eng.out/'repair-checks.json',results);assert all(v['check']['passed']for v in results)
    # Append files with unique batch names; original batches/report/probes untouched.
    for f in (eng.out/'physics').iterdir():os.link(f,original/'physics'/f.name)
    core.write(original/'batches-exit-repair-v1.json',core.read(original/'batches.json')+core.read(eng.out/'batches.json'))
    fixes={v['id']:v for v in results};core.write(original/'boundary-probes-exit-repair-v1.json',[fixes.get(v['id'],v)for v in core.read(original/'boundary-probes.json')])
    report=copy.deepcopy(old);report.update(passed=True,actualAttempts=old['actualAttempts']+1,batches=physics.artifact(original/'batches-exit-repair-v1.json'),probes=physics.artifact(original/'boundary-probes-exit-repair-v1.json'),boundaryRepair=dict(schema=review_boundary_repair_v3.SCHEMA,sourceReport=physics.artifact(original/'migration-physics.json'),repairBinding=physics.artifact(eng.out/'source_binding.json'),repairBatches=physics.artifact(eng.out/'batches.json'),repairChecks=physics.artifact(eng.out/'repair-checks.json'),newPhysicsAttempts=1,newIndependentHoldout=False))
    target=original/'migration-physics-exit-repair-v1.json';core.write(target,report);proof=physics.artifact(target);physics.verify_report(folder,proof,deep=True);core.write(folder/'qualification-repaired.json',dict(passed=True,report=proof,newPhysicsAttempts=1,newIndependentHoldout=False,freshCReturn='UNKNOWN',actualEarnedReturn='whole A-C-A passed calibration and independent held-out gates'));print('17 whole earned return deeply verified',flush=True)
if __name__=='__main__':main()
