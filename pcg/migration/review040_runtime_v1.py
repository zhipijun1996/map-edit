"""Approved reward-commit support release; reuse the native compiler and AIR test."""
import sys,types
from . import godot_package as base,review_first30_runtime_v2 as air
from pcg.manual_review.prepare_review040_v3 import filtered,extension
VERSION='foundation-data-runtime/review040-v1'
SCENES=[('module','module_loader_review040_v1.gd'),('demo','package_demo_review_first30_v2.gd')]
def audit_cases(doc,cases,*,require_replay=True):
 content,audit=air.audit_cases(filtered(doc),cases,require_replay=require_replay)
 extra=extension(doc);assert extra
 for c in cases:base._equal(c.get('review040_release'),extra['review040_release'],'reward_committed_release_binding',c['id'])
 content.update(extra);audit['nativeRewardCommitRelease']=extra['review040_release'];return content,audit
def dependencies(project):
 rows=air.dependencies(project)
 for name in ['pcg/migration/runtime/module_loader_review040_v1.gd','pcg/manual_review/runtime/review040_reward_release_v1.gd','pcg/manual_review/runtime/air_port_definition_v1.gd']:rows.append(dict(path=name,sha256=base.sha(base.ROOT/name)))
 return sorted(rows,key=lambda r:r['path'])
def decorate_manifest(manifest,stage):manifest['rewardRelease']=dict(compiler=dict(path='pcg/migration/review040_runtime_v1.py',sha256=base.sha(__file__)),trigger='original SimpleRoomReward accepted transaction',physics='native StaticBody2D collision layer disabled after commit',resourcesWritten=False,playerTransformWritten=False)
def air_terminal(case,receipt):return air.air_terminal(case,receipt)
def compile_package(*args,**kwargs):return base.compile_package(*args,**kwargs,_extension=sys.modules[__name__])
def verify_package(output_dir,require_loaded=True):return base.verify_package(output_dir,require_loaded=require_loaded,_extension=sys.modules[__name__])
def run_package_validation(*args,**kwargs):
 runner=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__);runner.__kwdefaults__=base.run_package_validation.__kwdefaults__;return runner(*args,**kwargs)
