"""Freeze one screened implementation, qualify once, deliver real native data."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,inspect
from pcg.migration import core,physics,holdout_guard,pool_protocols,godot_package
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from . import finalize_first40_v1 as shared
from .probe_review_refresh_v1 import AUTH
ROOT=core.REPO/'pcg/manual_review/implementation/review-refresh-final-v1'
def folder_for(row):return ROOT/row['moduleId']
def freeze(row):
    source=inspect.getsource(shared.freeze).replace('approved-first40-final-v1-','approved-review-refresh-final-v1-');scope={**shared.__dict__,'AUTH':AUTH,'ROOT':ROOT,'folder_for':folder_for};exec(compile(source,__file__,'exec'),scope);scope['freeze'](row)
def qualify(row):
    folder=folder_for(row);n=row['reviewId'];core.verify_artifacts(list(core.read(folder/'frozen.json').values()));protocol=physics.FULL_PROTOCOL;registration=None
    try:guard=holdout_guard.check(folder,protocol_path=protocol)
    except holdout_guard.HoldoutConflict:
        registration=holdout_guard.register_pool(folder,'approved-review-refresh-v1-'+n);protocol=pool_protocols.runtime_protocol(folder,new_run=True);guard=holdout_guard.check(folder,protocol_path=protocol)
    cases=core.read(folder/'physics-input-cases.json')['cases'];doc=core.read(folder/'module.mapnote.json');costs=dict(routes=sum(72 if c.get('enemies')or c.get('saws')or c.get('moving_platforms')else 50 for c in cases),boundaries=len(physics.seam_cases(cases[0],doc))+2*len(cases),counters=sum(len(physics.counter_cases(c))for c in cases));assert sum(costs.values())<=core.read(protocol)['maximumAttemptsPerModule']
    screens=sorted((core.REPO/'pcg/results').glob('approved-r024-'+n+'-control-screen-*/screen.json'));selection=next((p for p in reversed(screens)if core.read(p)['passed']and core.read(p)['sourceCases']['sha256']==core.sha(core.REPO/row['outputDirectory']/'cases.json')),None);assert selection,'unchanged_passed_screen_required:'+n
    core.write(folder/'preflight.json',dict(protocol=physics.artifact(protocol),guard=guard,registration=registration,costs=costs,maximumAttempts=sum(costs.values()),selection=physics.artifact(selection),stopping='one frozen formal run; calibration failure skips holdout; no threshold changes or reroll'))
    r=physics.run(folder,'approved-r024-'+n+'-qualified-final-v1',protocol_path=protocol);core.write(folder/'qualification.json',dict(passed=r['passed'],report=physics.artifact(core.REPO/'pcg/results'/('approved-r024-'+n+'-qualified-final-v1/migration-physics.json')),actualAttempts=r['actualAttempts']));print(n,'QUALIFIED',r['passed'],r['actualAttempts'],flush=True)
def deliver(row):
    folder=folder_for(row);n=row['reviewId'];protocol=pool_protocols.runtime_protocol(folder,new_run=False)if core.read(folder/'migration.json').get('holdoutPool')else physics.FULL_PROTOCOL
    eng,cases,authors=physics._engine(folder,'approved-r024-'+n+'-delivery-final-v1',protocol);items=[];checks=[]
    for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'delivery-final')for c in cases],'native-delivery')):
        q=checked_purpose(authors[i],c,r);checks.append(dict(case=c,check=q,evidence=e))
        if q['ok']:items.append(physics._recording(c,r))
    core.write(eng.out/'canonical.json',dict(rows=checks,passed=len(items)==len(cases)));assert len(items)==len(cases),'canonical_delivery_failed'
    core.write(folder/'playback-cases.json',dict(cases=items));godot_package.compile_package(folder/'module.mapnote.json',folder/'playback-cases.json',folder/'playable',stable_id=row['moduleId']);r=godot_package.run_package_validation(folder/'playable');core.write(folder/'package-result.json',r);print(n,'NATIVE',r['passed'],len(items),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','qualify','deliver']);p.add_argument('ids',nargs='+');a=p.parse_args()
    for row in core.read(AUTH/'handoff.json')['rows']:
        if row['reviewId']in a.ids:globals()[a.action](row)
