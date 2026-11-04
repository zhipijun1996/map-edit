"""Control-only 07/10 revision chosen by the predeclared bounded screens."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,copy
from pcg.migration import core,physics,holdout_guard,pool_protocols
from pcg.prototype.factory.core.quality import digest
from . import finalize_first30_v1 as prior

ROOT=core.REPO/'pcg/manual_review/implementation/first-30-final-v2'
AUTH=prior.AUTH

def folder_for(row):return ROOT/row['moduleId']

def freeze(row):
    n=row['reviewId'];old=prior.folder_for(row);folder=folder_for(row)
    if folder.exists():raise ValueError('already_frozen')
    selection=core.REPO/'pcg/results'/('approved-b001-first30-'+n+'-control-screen-'+('v1'if n=='07'else'v3'))/'screen.json'
    selected=core.read(selection)['selected'];assert selected
    for key in ('noise','module_sha256','factory_evidence','recorded_frames'):selected.pop(key,None)
    selected['id']='approved-first30-final-v2-'+n+'-'+selected['route_spec']['id'];cases=[selected]
    doc=core.read(old/'module.mapnote.json');doc['generationContract']['generation']['approvedImplementation'].update(controlProgramsSha256=digest([c['control_plan']for c in cases]),repairSelection=physics.artifact(selection))
    core.write(folder/'module.mapnote.json',doc);core.contract(folder/'module.mapnote.json',refresh=True)
    core.write(folder/'cases.json',dict(cases=cases));core.write(folder/'physics-input-cases.json',dict(cases=cases));core.write(folder/'migration.json',core.read(old/'migration.json'))
    params=core.read(old/'parameters.json');params['controls']=[dict(route=c['route_spec'],control_plan=c['control_plan'],max_frames=c['max_frames'])for c in cases];params['repairSelection']=physics.artifact(selection);core.write(folder/'parameters.json',params)
    core.write(folder/'frozen.json',{k:physics.artifact(folder/v)for k,v in dict(module='module.mapnote.json',cases='physics-input-cases.json',parameters='parameters.json').items()})
    print(n,'revised frozen',flush=True)

def qualify(row):
    folder=folder_for(row);n=row['reviewId'];core.verify_artifacts(list(core.read(folder/'frozen.json').values()))
    if n=='07':holdout_guard.register_pool(folder,'approved-first30-final-v2-'+n)
    protocol=pool_protocols.runtime_protocol(folder,physics.FULL_PROTOCOL if n=='10'else None,new_run=True)
    guard=holdout_guard.check(folder,protocol_path=protocol);cases=core.read(folder/'cases.json')['cases'];doc=core.read(folder/'module.mapnote.json')
    costs=dict(routes=sum((36 if c.get('enemies')or c.get('moving_platforms')or c.get('saws')else 25)*2 for c in cases),boundaries=len(physics.seam_cases(cases[0],doc))+2*len(cases),counters=sum(len(physics.counter_cases(c))for c in cases))
    assert sum(costs.values())<=core.read(protocol)['maximumAttemptsPerModule']
    core.write(folder/'preflight.json',dict(protocol=physics.artifact(protocol),guard=guard,costs=costs,maximumAttempts=sum(costs.values()),selection='first all-pass variant of immutable bounded calibration screen',automaticRetries=False))
    report=physics.run(folder,'approved-b001-first30-'+n+'-qualified-final-v2',protocol_path=protocol)
    core.write(folder/'qualification.json',dict(report=physics.artifact(core.REPO/'pcg/results'/('approved-b001-first30-'+n+'-qualified-final-v2/migration-physics.json')),passed=report['passed'],actualAttempts=report['actualAttempts']))
    print(n,'qualified v2',report['passed'],report['actualAttempts'],flush=True)

def deliver(row):
    # Existing delivery implementation, with only explicit output version binding.
    import types
    runner=types.FunctionType(prior.deliver.__code__,{**prior.__dict__,'folder_for':folder_for,'physics':physics},argdefs=prior.deliver.__defaults__)
    # Immutable v1 function embeds its run suffix. Use a separately saved v2
    # source instead of overwriting v1 evidence or rewriting case IDs.
    import inspect
    source=inspect.getsource(prior.deliver).replace('-delivery-final-v1','-delivery-final-v2')
    namespace={**prior.__dict__,'folder_for':folder_for};exec(compile(source,__file__,'exec'),namespace);namespace['deliver'](row)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','qualify','deliver']);p.add_argument('ids',nargs='+');a=p.parse_args()
    for row in core.read(AUTH/'handoff.json')['rows']:
        if row['reviewId']in a.ids:globals()[a.action](row)
