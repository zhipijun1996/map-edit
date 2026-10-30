"""Freeze first unchanged all-gates candidate, qualify once, then native delivery."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect,sys
from pcg.migration import core,physics,godot_package,revision058_runtime_v1,revision058_runtime_v3,revision058_runtime_v4,holdout_guard,pool_protocols,revision059_runtime_v3
from . import finalize_first40_v1 as shared,finalize_revision053_v1 as previous
from .continue_revision059_v1 import rows,label,AUTH
from .revision058_content_v2 import decode as new_decode
from .prepare_review045_v1 import decode as forest_decode
ROOT=core.REPO/'pcg/manual_review/implementation/revision-059-final-v1'
def folder_for(r):return ROOT/r['moduleId']
def decode(doc):
 from .revision059_hq_content_v1 import decode as hq
 return hq(doc)if 'plains-hq'in doc['id']else new_decode(doc)if doc['id'].startswith('idea-')else forest_decode(doc)
def freeze(row,version):
 f=core.REPO/row['outputDirectory'];screen=core.REPO/f'pcg/results/approved-r059-{label(row)}-control-screen-{version}/screen.json';native=f/f'native-preflight-{version}.json';assert core.read(screen)['passed']and core.read(native)['passed']and core.read(screen)['sourceCases']['sha256']==core.sha(f/'cases.json')
 decoder_path='pcg/manual_review/revision059_hq_content_v1.py'if label(row).startswith('hq')else'pcg/manual_review/prepare_review045_v1.py'if label(row)=='42'else'pcg/manual_review/revision058_content_v2.py'if label(row)=='s07'else'pcg/manual_review/revision058_content_v1.py'
 source=inspect.getsource(shared.freeze).replace('approved-first40-final-v1-','approved-r059-final-v1-').replace('pcg/manual_review/first30_content_v2.py',decoder_path);namespace={**shared.__dict__,'AUTH':AUTH,'ROOT':ROOT,'folder_for':folder_for,'decode':decode};exec(compile(source,__file__,'exec'),namespace);namespace['freeze'](row)
 final=folder_for(row);d=core.read(final/'module.mapnote.json');d['generationContract']['generation']['approvedImplementation']['boundaryInputs']=physics.artifact(final/'physics-input-cases.json');core.write(final/'module.mapnote.json',d);core.write(final/'static-check.json',core.contract(final/'module.mapnote.json',refresh=True));frozen=core.read(final/'frozen.json');frozen['module']=physics.artifact(final/'module.mapnote.json');core.write(final/'frozen.json',frozen);core.write(final/'selection.json',dict(version=version,allGatesPassed=True,screen=physics.artifact(screen),native=physics.artifact(native),rule='first unchanged all-gates candidate'))
def qualify(row):
 f=folder_for(row);protocol=pool_protocols.runtime_protocol(f,new_run=True)if core.read(f/'migration.json').get('holdoutPool')else physics.FULL_PROTOCOL;registration=None
 try:guard=holdout_guard.check(f,protocol_path=protocol)
 except holdout_guard.HoldoutConflict:
  registration=holdout_guard.register_pool(f,'approved-revision059-v1-'+label(row));protocol=pool_protocols.runtime_protocol(f,new_run=True);guard=holdout_guard.check(f,protocol_path=protocol)
 assert core.read(protocol)['schema']=='pcg/module-migration-protocol/v2','explicit_FULL_v2_protocol_required_before_any_factory_run'
 cs=core.read(f/'physics-input-cases.json')['cases'];doc=core.read(f/'module.mapnote.json');costs=dict(routes=sum(72 if c.get('enemies')or c.get('saws')or c.get('moving_platforms')else 50 for c in cs),boundaries=len(physics.seam_cases(cs[0],doc))+2*len(cs),counters=sum(len(physics.counter_cases(c))for c in cs));assert sum(costs.values())<=core.read(protocol)['maximumAttemptsPerModule']
 assert not list((core.REPO/'pcg/results').glob('approved-r059-'+label(row)+'-qualified*/holdout-*.json'))
 core.write(f/'preflight.json',dict(protocol=physics.artifact(protocol),guard=guard,registration=registration,costs=costs,maximumAttempts=sum(costs.values()),stopping='one selected formal version; no reroll or holdout tuning'))
 run='approved-r059-'+label(row)+'-qualified-final-v1';report=physics.run(f,run,protocol_path=protocol);core.write(f/'qualification.json',dict(passed=report['passed'],actualAttempts=report['actualAttempts'],report=physics.artifact(core.REPO/'pcg/results'/run/'migration-physics.json')));print(label(row),'QUALIFIED',report['passed'],report['actualAttempts'],flush=True)
def deliver(row):
 from . import finalize_revision053_v2 as delivery
 source=inspect.getsource(delivery.deliver).replace('approved-r053-','approved-r059-').replace("revision053_runtime_v1 if n in ['196','three','lift']else godot_package","revision059_runtime_v3 if n.startswith('hq')else revision058_runtime_v3 if n=='s07'else revision058_runtime_v4 if n=='s11'else revision058_runtime_v1 if n!='42'else godot_package")
 namespace={**delivery.__dict__,'folder_for':folder_for,'label':label,'revision059_runtime_v3':revision059_runtime_v3,'revision058_runtime_v1':revision058_runtime_v1,'revision058_runtime_v3':revision058_runtime_v3,'revision058_runtime_v4':revision058_runtime_v4};exec(compile(source,__file__,'exec'),namespace);namespace['deliver'](row)
if __name__=='__main__':
 for r in rows():
  wanted=sys.argv[3:]if sys.argv[1]=='freeze'else sys.argv[2:]
  if label(r)in wanted:(freeze(r,sys.argv[2])if sys.argv[1]=='freeze'else globals()[sys.argv[1]](r))
