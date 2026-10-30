"""Freeze real control repairs separately from immutable batch-001 evidence."""
import argparse
import copy
from pcg.migration import core, physics, holdout_guard, pool_protocols
from pcg.prototype.factory.core.quality import digest

ROOT=core.REPO
AUTH=ROOT/'feedback/manual-review/implementation-results/first-30-v2/authorization'


def folder_for(row):return ROOT/'pcg/manual_review/implementation/first-30-v3'/row['moduleId']


def freeze(row):
    n=row['reviewId'];old=ROOT/row['outputDirectory'];folder=folder_for(row)
    selection_run='approved-b001-'+n+'-repair-v'+{'02':'7','03':'11'}[n]
    if folder.exists():raise ValueError('repair_already_frozen')
    selection=core.read(ROOT/'pcg/results'/selection_run/'repair-check.json')
    chosen=selection['selected'];assert chosen is not None
    doc=core.read(old/'module.mapnote.json');cases=core.read(old/'cases.json')['cases']
    for i,c in enumerate(cases):
        if c['route_spec']['id']==chosen['route_spec']['id']:c=copy.deepcopy(chosen)
        for k in ('noise','module_sha256','factory_evidence','factory_id','recorded_frames'):c.pop(k,None)
        c['generation_rule']['registration_source']='pcg/manual_review/approved_r'+n+'_v3.py'
        c['id']='approved-first30-v3-'+n+'-'+c['route_spec']['id'];cases[i]=c
    g=doc['generationContract'];g['generation']['approvedImplementation'].update(
        authorization=physics.artifact(AUTH/'request.json'),controlProgramsSha256=digest([c['control_plan']for c in cases]),
        repairSelection=physics.artifact(ROOT/'pcg/results'/selection_run/'repair-check.json'))
    core.write(folder/'cases.json',dict(cases=cases));core.write(folder/'physics-input-cases.json',dict(cases=cases))
    core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True)
    meta=core.read(old/'migration.json');meta.pop('holdoutPool',None)
    core.write(folder/'migration.json',meta)
    core.write(folder/'parameters.json',dict(designVersion=row['designVersion'],
        geometry=physics.artifact(old/'module.mapnote.json'),designGeometryChanged=False,
        content=__import__('pcg.migration.godot_package',fromlist=['content_from_objects']).content_from_objects(doc),
        controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])for c in cases]))
    core.write(folder/'frozen.json',dict(module=physics.artifact(folder/'module.mapnote.json'),
        cases=physics.artifact(folder/'cases.json'),parameters=physics.artifact(folder/'parameters.json'),
        originalBatchUnchanged=True,selection=physics.artifact(ROOT/'pcg/results'/selection_run/'repair-check.json')))
    print(n,'frozen',flush=True)


def qualify(row):
    folder=folder_for(row);n=row['reviewId'];doc=core.read(folder/'module.mapnote.json')
    frozen=core.read(folder/'frozen.json');core.verify_artifacts([frozen[k]for k in ('module','cases','parameters')])
    cases=core.read(folder/'physics-input-cases.json')['cases']
    routes=sum((36 if c.get('enemies')or c.get('saws')or c.get('moving_platforms')else 25)*2 for c in cases)
    probes=len(physics.seam_cases(cases[0],doc))+2*len(cases)
    counters=sum(len(physics.counter_cases(c))for c in cases)
    assert routes+probes+counters<=core.read(physics.FULL_PROTOCOL)['maximumAttemptsPerModule']
    registration=holdout_guard.register_pool(folder,'approved-first30-v3-'+n)
    selected=pool_protocols.runtime_protocol(folder,new_run=True)
    guard=holdout_guard.check(folder,protocol_path=selected)
    core.write(folder/'preflight.json',dict(registration=registration,guard=guard,
        effectiveProtocol=physics.artifact(selected),maximumAttempts=routes+probes+counters,
        costs=dict(routes=routes,boundaries=probes,counters=counters),geometryChanges=False))
    report=physics.run(folder,'approved-b001-'+n+'-qualified-v6',protocol_path=selected)
    core.write(folder/'qualification.json',dict(report=physics.artifact(ROOT/'pcg/results'/f'approved-b001-{n}-qualified-v6/migration-physics.json'),
        passed=report['passed'],actualAttempts=report['actualAttempts']))
    print(n,'qualified',report['passed'],report['actualAttempts'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','qualify']);p.add_argument('ids',nargs='+',choices=['01','02','03']);a=p.parse_args()
    rows=core.read(AUTH/'handoff.json')['rows']
    for n in a.ids:globals()[a.action](next(r for r in rows if r['reviewId']==n))
