"""Correct only initial native carrier observer sampling; original collisions."""
import sys
from . import godot_package as base,review_refresh_runtime_v1 as old
VERSION='foundation-data-runtime/review-refresh-v2'
SCENES=[('module','module_loader_review_refresh_v2.gd'),('demo','package_demo_v3.gd')]
def required(doc,cases):return any(o.get('mechanics',{}).get('trackerWarmupPhysicsFrames')==2 for o in doc.get('objects',[]))
def audit_cases(doc,cases,*,require_replay=True):
    content,audit=old.audit_cases(doc,cases,require_replay=require_replay)
    if not content['refresh_carried_enemies']:base._fail('carrier_bootstrap_requires_actual_carrier')
    if any(c.get('refresh_carrier_warmup_frames')!=2 for c in cases):base._fail('carrier_observer_initialization_not_bound')
    content['refresh_carrier_warmup_frames']=2;audit['observerInitialSamples']=2
    return content,audit
def dependencies(project):
    rows=old.dependencies(project)
    for name in ('pcg/migration/runtime/module_loader_review_refresh_v2.gd','pcg/manual_review/runtime/refresh_carrier_bootstrap_v1.gd'):rows.append(dict(path=name,sha256=base.sha(base.ROOT/name)))
    return sorted(rows,key=lambda r:r['path'])
def decorate_manifest(manifest,stage):manifest['approvedRefreshConsumers']=dict(compiler=dict(path='pcg/migration/review_refresh_runtime_v2.py',sha256=base.sha(__file__)),observerInitialSamples=2,originalEnemyAndShotLatch=True,scriptedTransformAssignment=False)
def verify_package(output_dir,require_loaded=True):return base.verify_package(output_dir,require_loaded=require_loaded,_extension=sys.modules[__name__])
