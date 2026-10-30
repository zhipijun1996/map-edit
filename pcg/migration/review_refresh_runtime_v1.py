"""Additional native Cell consumers; preserve the existing compiler and Actor."""
import sys
from . import godot_package as base,review_air_runtime as air
VERSION='foundation-data-runtime/review-refresh-v1'
SCENES=[('module','module_loader_review_refresh_v1.gd'),('demo','package_demo_v3.gd')]
def bindings(doc):
    content=base.content_from_objects(doc);repeat=[o['sourceId']for o in doc['objects']if o.get('mechanics',{}).get('service')=='ReopenableTimedLatch/v1'];carry=[]
    for o in doc['objects']:
        if o.get('type')!='enemy'or'carrying'not in o.get('mechanics',{}).get('supportPolicy',''):continue
        matching=[v for v in content['moving_platforms']if abs(o['y']+o['h']-(v['start'][1]-v['size'][1]/2))<.01 and abs(o['x']+o['w']/2-v['start'][0])+o['w']/2<=v['size'][0]/2]
        if len(matching)!=1:base._fail('carrier_requires_real_initial_support',object_id=o['id'])
        carry.append(dict(enemy=o['sourceId'],carrier=matching[0]['platform_id']))
    return repeat,carry

def required(doc,cases):return any(o.get('mechanics',{}).get('service')=='ReopenableTimedLatch/v1' or 'carrying'in o.get('mechanics',{}).get('supportPolicy','')for o in doc.get('objects',[]))
def audit_cases(doc,cases,*,require_replay=True):
    content,audit=base.audit_cases(doc,cases,require_replay=require_replay,_extension=True);repeat,carry=bindings(doc)
    for c in cases:
        base._equal(c.get('refresh_reopenable_latches',[]),repeat,'reopenable_latch_binding',c['id']);base._equal(c.get('refresh_carried_enemies',[]),carry,'collision_carrier_binding',c['id'])
    content.update(refresh_reopenable_latches=repeat,refresh_carried_enemies=carry);audit.update(reopenableTimedGates=repeat,nativeCollisionCarrying=carry,scriptedTransformAssignment=False,scriptedResources=False)
    return content,audit

def dependencies(project):
    rows=air.dependencies(project)
    for name in ('pcg/migration/runtime/module_loader_review_refresh_v1.gd','pcg/manual_review/runtime/refresh_cells_v1.gd','pcg/manual_review/runtime/refresh_timed_latch_v1.gd','pcg/manual_review/runtime/refresh_carrier_support_v1.gd'):rows.append(dict(path=name,sha256=base.sha(base.ROOT/name)))
    return sorted(rows,key=lambda r:r['path'])
def decorate_manifest(manifest,stage):manifest['approvedRefreshConsumers']=dict(compiler=dict(path='pcg/migration/review_refresh_runtime_v1.py',sha256=base.sha(__file__)),originalEnemyAndShotLatch=True,carrierMovement='native move_and_collide',scriptedResources=False)
def verify_package(output_dir,require_loaded=True):return base.verify_package(output_dir,require_loaded=require_loaded,_extension=sys.modules[__name__])
