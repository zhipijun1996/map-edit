"""Freeze the first unchanged all-gates candidate; allocate at most one formal run."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect,sys
from pcg.migration import core,physics,holdout_guard,pool_protocols
from . import finalize_first40_v1 as shared
from .continue_revision053_v1 import rows,label,AUTH
from .prepare_revision053_v1 import decode
ROOT=core.REPO/'pcg/manual_review/implementation/revision-053-final-v1'
def folder_for(row):return ROOT/row['moduleId']
def freeze(row,version):
    draft=core.REPO/row['outputDirectory'];screen=core.REPO/('pcg/results/approved-r053-'+label(row)+'-control-screen-'+version+'/screen.json');native=draft/('native-preflight-'+version+'.json')
    assert core.read(screen)['passed']and core.read(native)['passed']and core.read(screen)['sourceCases']['sha256']==core.sha(draft/'cases.json')
    core.write(draft/'selection.json',dict(version=version,screen=physics.artifact(screen),native=physics.artifact(native),rule='first unchanged all-gates passing candidate'))
    source=inspect.getsource(shared.freeze).replace('approved-first40-final-v1-','approved-r053-final-v1-').replace('pcg/manual_review/first30_content_v2.py','pcg/manual_review/prepare_revision053_v1.py')
    namespace={**shared.__dict__,'AUTH':AUTH,'ROOT':ROOT,'folder_for':folder_for,'decode':decode};exec(compile(source,__file__,'exec'),namespace);namespace['freeze'](row)
def qualify(row):
    f=folder_for(row);protocol=physics.FULL_PROTOCOL;registration=None
    try:guard=holdout_guard.check(f,protocol_path=protocol)
    except holdout_guard.HoldoutConflict:
        registration=holdout_guard.register_pool(f,'approved-revision053-v1-'+label(row));protocol=pool_protocols.runtime_protocol(f,new_run=True);guard=holdout_guard.check(f,protocol_path=protocol)
    cs=core.read(f/'physics-input-cases.json')['cases'];doc=core.read(f/'module.mapnote.json');costs=dict(routes=sum(72 if c.get('enemies')or c.get('saws')or c.get('moving_platforms')else 50 for c in cs),boundaries=len(physics.seam_cases(cs[0],doc))+2*len(cs),counters=sum(len(physics.counter_cases(c))for c in cs));assert sum(costs.values())<=core.read(protocol)['maximumAttemptsPerModule']
    assert not list((core.REPO/'pcg/results').glob('approved-r053-'+label(row)+'-qualified*/holdout-*.json'))
    core.write(f/'preflight.json',dict(protocol=physics.artifact(protocol),guard=guard,registration=registration,costs=costs,maximumAttempts=sum(costs.values()),stopping='one selected formal version; no reroll or holdout tuning'))
    run='approved-r053-'+label(row)+'-qualified-final-v1';report=physics.run(f,run,protocol_path=protocol);core.write(f/'qualification.json',dict(passed=report['passed'],actualAttempts=report['actualAttempts'],report=physics.artifact(core.REPO/'pcg/results'/run/'migration-physics.json')));print(label(row),'QUALIFIED',report['passed'],report['actualAttempts'],flush=True)
if __name__=='__main__':
    for row in rows():
        wanted=sys.argv[3:]if sys.argv[1]=='freeze'else sys.argv[2:]
        if label(row)in wanted:(freeze(row,sys.argv[2])if sys.argv[1]=='freeze'else globals()[sys.argv[1]](row))
