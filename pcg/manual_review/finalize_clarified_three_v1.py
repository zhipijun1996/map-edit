"""Freeze screened controls; use existing full protocol, guard and native loader."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,inspect
from pcg.migration import core,physics,holdout_guard,pool_protocols,godot_package,review029_runtime_v2
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from . import finalize_first40_v1 as shared
from .repair_clarified_three_v1 import AUTH,FINAL
from .review029_content_v1 import decode
ROOT=FINAL
def folder_for(row):return ROOT/row['moduleId']
def freeze(row):
 text=inspect.getsource(shared.freeze).replace('approved-first40-final-v1-','approved-clarified-three-final-v1-')
 scope={**shared.__dict__,'AUTH':AUTH,'ROOT':ROOT,'folder_for':folder_for,'decode':decode};exec(compile(text,__file__,'exec'),scope);scope['freeze'](row)
def qualify(row):
 f=folder_for(row);n=row['reviewId'];core.verify_artifacts(list(core.read(f/'frozen.json').values()));protocol=physics.FULL_PROTOCOL;registration=None
 try:guard=holdout_guard.check(f,protocol_path=protocol)
 except holdout_guard.HoldoutConflict:
  registration=holdout_guard.register_pool(f,'approved-clarified-three-v1-'+n);protocol=pool_protocols.runtime_protocol(f,new_run=True);guard=holdout_guard.check(f,protocol_path=protocol)
 cs=core.read(f/'physics-input-cases.json')['cases'];doc=core.read(f/'module.mapnote.json');costs=dict(routes=sum(72 if c.get('enemies')or c.get('saws')or c.get('moving_platforms')else 50 for c in cs),boundaries=len(physics.seam_cases(cs[0],doc))+2*len(cs),counters=sum(len(physics.counter_cases(c))for c in cs));assert sum(costs.values())<=core.read(protocol)['maximumAttemptsPerModule']
 selection=core.resolve_artifact(core.read(core.REPO/row['outputDirectory']/'selection.json')['screen']['path']);assert core.read(selection)['passed'] and core.read(selection)['sourceCases']['sha256']==core.sha(core.REPO/row['outputDirectory']/'cases.json'),'unchanged_selected_screen_required'
 assert not list((core.REPO/'pcg/results').glob('approved-c3-'+n+'-qualified*/holdout-*.json')),'unreported_holdout_check'
 core.write(f/'preflight.json',dict(protocol=physics.artifact(protocol),guard=guard,registration=registration,costs=costs,maximumAttempts=sum(costs.values()),selection=physics.artifact(selection),stopping='one formal version; no holdout selection or retries; failures retained',derivedFrameLimit=3600))
 run='approved-c3-'+n+'-qualified-final-v1';r=physics.run(f,run,protocol_path=protocol);core.write(f/'qualification.json',dict(passed=r['passed'],report=physics.artifact(core.REPO/'pcg/results'/run/'migration-physics.json'),actualAttempts=r['actualAttempts']));print(n,'QUALIFIED',r['passed'],r['actualAttempts'],flush=True)
def deliver(row):
 f=folder_for(row);n=row['reviewId'];protocol=pool_protocols.runtime_protocol(f,new_run=False)if core.read(f/'migration.json').get('holdoutPool')else physics.FULL_PROTOCOL
 eng,cs,authors=physics._engine(f,'approved-c3-'+n+'-delivery-final-v1',protocol);items=[];checks=[]
 for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'delivery-final-v1')for c in cs],'native-delivery')):
  q=checked_purpose(authors[i],c,r);checks.append(dict(case=c,check=q,evidence=e))
  if q['ok']:items.append(physics._recording(c,r))
 core.write(eng.out/'canonical.json',dict(rows=checks,passed=len(items)==len(cs)));assert len(items)==len(cs),'canonical_delivery_failed'
 core.write(f/'playback-cases.json',dict(cases=items));backend=review029_runtime_v2 if n=='171'else godot_package
 backend.compile_package(f/'module.mapnote.json',f/'playback-cases.json',f/'playable',stable_id=row['moduleId']);r=backend.run_package_validation(f/'playable');core.write(f/'package-result.json',r);print(n,'NATIVE',r['passed'],len(items),flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['freeze','qualify','deliver']);p.add_argument('ids',nargs='+');a=p.parse_args()
 for r in core.read(AUTH/'handoff.json')['rows']:
  if r['reviewId']in a.ids:globals()[a.action](r)
