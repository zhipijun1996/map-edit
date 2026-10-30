"""Rerun only the two incorrectly labelled docking fixtures, preserving history."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,os,shutil
from pcg.migration import core,physics,review_boundary_repair_v1
from .finalize_first30_v1 import AUTH,folder_for

def main():
    row=next(r for r in core.read(AUTH/'handoff.json')['rows']if r['reviewId']=='23');folder=folder_for(row);doc=core.read(folder/'module.mapnote.json')
    original=core.REPO/'pcg/results/approved-b001-first30-23-qualified-final-v1';old=core.read(original/'migration-physics.json')
    eng,cases,_=physics._engine(folder,'approved-b001-first30-23-entry-docks-repair-v1',physics.FULL_PROTOCOL)
    probes=[physics.continuous_entry(c,doc)for c in cases if c['route_spec']['to_port']=='C']
    core.write(eng.out/'protocol.json',dict(maximumAttempts=2,scope='entrance dock labels only; unchanged real worlds, inputs and resources',newIndependentHoldout=False))
    results=[]
    for c,r,e in eng.run(probes,'repaired-entrance-dock'):
        q=physics.crossing(c,r);results.append(dict(id=c['id'],probe=c['migration_probe'],check=q,evidence=e));print(c['id'],q['passed'],flush=True)
    core.write(eng.out/'repair-checks.json',results)
    assert all(v['check']['passed']for v in results)
    target=core.REPO/'pcg/results/approved-b001-first30-23-evidence-repaired-v1';shutil.copytree(original,target,copy_function=os.link)
    for f in (eng.out/'physics').iterdir():os.link(f,target/'physics'/f.name)
    batches=core.read(original/'batches.json')+core.read(eng.out/'batches.json');core.write(target/'batches.json',batches)
    fixes={v['id']:v for v in results};core.write(target/'boundary-probes.json',[fixes.get(v['id'],v)for v in core.read(original/'boundary-probes.json')])
    report=copy.deepcopy(old);report.update(passed=True,actualAttempts=old['actualAttempts']+2,batches=physics.artifact(target/'batches.json'),probes=physics.artifact(target/'boundary-probes.json'),boundaryRepair=dict(schema=review_boundary_repair_v1.SCHEMA,sourceReport=physics.artifact(original/'migration-physics.json'),repairBinding=physics.artifact(eng.out/'source_binding.json'),repairBatches=physics.artifact(eng.out/'batches.json'),repairChecks=physics.artifact(eng.out/'repair-checks.json'),newPhysicsAttempts=2,newIndependentHoldout=False,scope='two original route AIR destinations incorrectly overrode grounded entrance-dock goals; original failed raw retained',counterScope=physics.artifact(core.REPO/'pcg/migration/review_counter_scope_v2.py')))
    core.write(target/'migration-physics.json',report);proof=physics.artifact(target/'migration-physics.json');physics.verify_report(folder,proof,deep=True)
    core.write(folder/'qualification-repaired.json',dict(passed=True,report=proof,newPhysicsAttempts=2,newIndependentHoldout=False));print('23 repaired evidence deeply verified',flush=True)

if __name__=='__main__':main()
