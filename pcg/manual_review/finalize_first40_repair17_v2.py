"""Certify the outbound and the actual earned-return loop without fresh-C claims."""
import argparse,copy
from pcg.migration import core,physics,holdout_guard
from pcg.prototype.factory.core.quality import digest
from . import finalize_first40_v1 as shared
from .first30_content_v2 import decode
AUTH=shared.AUTH
ROOT=core.REPO/'pcg/manual_review/implementation/first-40-repair17-v2'
def folder_for(row):return ROOT/row['moduleId']

def freeze(row):
    old=core.REPO/'pcg/manual_review/implementation/first-30-final-v1'/row['moduleId'];folder=folder_for(row)
    if folder.exists():raise ValueError('repair_already_frozen')
    selection=core.REPO/'pcg/results/approved-b040-17-return-control-screen-v2/screen.json';chosen=core.read(selection)['selected'];assert chosen
    prior=core.REPO/'pcg/manual_review/implementation/first-40-repair17-v1'/row['moduleId'];main=core.read(prior/'cases.json')['cases'][0];loop=copy.deepcopy(chosen)
    for c in (main,loop):
        for k in ('noise','module_sha256','recorded_frames','factory_evidence'):c.pop(k,None)
    main['id']='approved-first40-repair17-v2-A-to-C';loop['id']='approved-first40-repair17-v2-A-C-A-earned-return'
    cases=[main,loop];doc=core.read(old/'module.mapnote.json');g=doc['generationContract'];previous_routes=copy.deepcopy(g['routes']);outbound=next(r for r in g['routes']if r['from']=='A')
    returned=copy.deepcopy(next(r for r in g['routes']if r['from']=='C'));returned.update(id='A-C-A-earned-return',**{'from':'A','to':'A'},localDisplacementBlocks=[0,0])
    returned['initialConditions']=copy.deepcopy(outbound['initialConditions']);returned['resourcePressure']['note']='Full actual A-C-A trace; earned bridge and C visit, no world rebuild or resource injection.'
    g['routes']=[outbound,returned]
    for p in g['ports']:p['routeRoles']=[r['id']+':'+('entry'if r['from']==p['id']else'exit')for r in g['routes']if p['id']in(r['from'],r['to'])]
    g['relations']=[dict(from_=p['id'])for p in []] if False else [dict(**{'from':a['id'],'to':b['id']},status='UNKNOWN',conditions='earned C-to-A is witnessed inside A-C-A, never an arbitrary fresh-C initial edge',routeIds=[r['id']for r in g['routes']if r['from']==a['id']and r['to']==b['id']])for a in g['ports']for b in g['ports']]
    impl=g['generation']['approvedImplementation'];impl.update(authorization=physics.artifact(AUTH/'request.json'),controlProgramsSha256=digest([c['control_plan']for c in cases]),repairSelection=physics.artifact(selection),designRouteTargets=previous_routes,measuredRouteInterpretation='A-C-A proves the exact conditional C-to-A design intent in the earned same world. Fresh-C-to-A remains UNKNOWN; A-A is an observed additional directed Route, not a new Module or Port.')
    core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True)
    core.write(folder/'cases.json',dict(cases=cases));core.write(folder/'physics-input-cases.json',dict(cases=cases));core.write(folder/'migration.json',core.read(old/'migration.json'))
    core.write(folder/'parameters.json',dict(designVersion=row['designVersion'],content=decode(doc),controls=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])for c in cases],designGeometryChanged=False,freshCReturn='UNKNOWN',sourceProgramSelection=physics.artifact(selection)))
    core.write(folder/'frozen.json',{k:physics.artifact(folder/v)for k,v in dict(module='module.mapnote.json',cases='physics-input-cases.json',parameters='parameters.json').items()})
    print('17 repaired outbound and same-world loop frozen',flush=True)

# Reuse the existing complete runner, under this explicit new version and folder.
def operation(name,row):
    import inspect
    if name=='qualify':
        from pcg.migration import pool_protocols
        folder=folder_for(row);registration=holdout_guard.register_pool(folder,'approved-first40-repair17-v2');protocol=pool_protocols.runtime_protocol(folder,new_run=True);guard=holdout_guard.check(folder,protocol_path=protocol)
        cases=core.read(folder/'physics-input-cases.json')['cases'];doc=core.read(folder/'module.mapnote.json');costs=dict(routes=144,boundaries=len(physics.seam_cases(cases[0],doc))+2*len(cases),counters=sum(len(physics.counter_cases(c))for c in cases));assert sum(costs.values())<=core.read(protocol)['maximumAttemptsPerModule']
        core.write(folder/'preflight.json',dict(protocol=physics.artifact(protocol),guard=guard,registration=registration,costs=costs,maximumAttempts=sum(costs.values()),freshCReturn='UNKNOWN',selection='first all-seven-pass loop after bounded corridor screen'))
        report=physics.run(folder,'approved-b040-17-qualified-first40-repair17-v2',protocol_path=protocol);core.write(folder/'qualification.json',dict(report=physics.artifact(core.REPO/'pcg/results/approved-b040-17-qualified-first40-repair17-v2/migration-physics.json'),passed=report['passed'],actualAttempts=report['actualAttempts']));print('17 v2 qualified',report['passed'],report['actualAttempts'],flush=True);return
    source=inspect.getsource(shared.deliver).replace('-delivery-final-v1','-delivery-first40-repair17-v2');scope={**shared.__dict__,'folder_for':folder_for};exec(compile(source,__file__,'exec'),scope);scope['deliver'](row)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','qualify','deliver']);a=p.parse_args();row=next(r for r in core.read(AUTH/'handoff.json')['rows']if r['reviewId']=='17')
    freeze(row)if a.action=='freeze'else operation(a.action,row)
