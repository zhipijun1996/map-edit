"""An additive native Cell binding; delegate compilation and validation to the existing package compiler."""
import sys
from . import godot_package as base
VERSION='foundation-data-runtime/review-air-v1'
SCENES=[('module','module_loader_review_air_v1.gd'),('demo','package_demo_v3.gd')]
def required(doc,cases):
    present=any(o.get('type')=='enemy'and o.get('definition')=='plains_diver'for o in doc.get('objects',[]))
    if present and any(c.get('original_pickups')or c.get('original_tuning_profile')or c.get('original_fixture_profile')for c in cases):
        base._fail('review_air_native_profile_combination_not_implemented')
    return present
def audit_cases(doc,cases,*,require_replay=True):
    return base.audit_cases(doc,cases,require_replay=require_replay,_extension=True)
def dependencies(project):
    rows=base._dependencies(project,base.EXTENDED_VERSION)
    for relative in ('pcg/migration/runtime/module_loader_review_air_v1.gd','pcg/manual_review/runtime/air_enemy_binding_v1.gd','pcg/prototype/godot/resources/enemies/plains_diver.tres'):
        row=dict(path=relative,sha256=base.sha(base.ROOT/relative))
        if relative.startswith('pcg/prototype/godot/'):row['resourcePath']='res://'+relative.removeprefix('pcg/prototype/godot/')
        rows.append(row)
    return sorted(rows,key=lambda r:r['path'])
def decorate_manifest(manifest,stage):
    manifest['reviewEnemyBinding']=dict(source='existing original EnemyActor diver behavior',physicsReimplemented=False)
def verify_package(output_dir,require_loaded=True):
    return base.verify_package(output_dir,require_loaded=require_loaded,_extension=sys.modules[__name__])
