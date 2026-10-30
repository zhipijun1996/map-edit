"""Add the approved one-shot ambush to the existing native compiler."""
import sys,types
from . import godot_package as base,review_air_runtime as air
from pcg.manual_review.review029_content_v1 import filtered,wave
VERSION='foundation-data-runtime/review029-v2'
SCENES=[('module','module_loader_review029_v2.gd'),('demo','package_demo_v3.gd')]
def audit_cases(doc,cases,*,require_replay=True):
 content,audit=base.audit_cases(filtered(doc),cases,require_replay=require_replay,_extension=True);w=wave(doc)
 assert w
 for c in cases:base._equal(c.get('review029_wave'),w,'approved_wave_binding',c['id'])
 content['review029_wave']=w;audit['nativeOneShotWave']=w;return content,audit
def dependencies(project):
 rows=air.dependencies(project)
 for name in ('pcg/migration/runtime/module_loader_review029_v2.gd','pcg/manual_review/runtime/review029_ambush_v1.gd','pcg/manual_review/runtime/review029_ambush_v2.gd'):
  rows.append(dict(path=name,sha256=base.sha(base.ROOT/name)))
 return sorted(rows,key=lambda r:r['path'])
def decorate_manifest(manifest,stage):manifest['approvedWaveConsumer']=dict(compiler=dict(path='pcg/migration/review029_runtime_v2.py',sha256=base.sha(__file__)),trigger='native Area2D body_entered',enemy='original EnemyActor/EnemyMotor',resourceWrites=False,playerTransformWrites=False)
def compile_package(*args,**kwargs):return base.compile_package(*args,**kwargs,_extension=sys.modules[__name__])
def verify_package(output_dir,require_loaded=True):return base.verify_package(output_dir,require_loaded=require_loaded,_extension=sys.modules[__name__])
def run_package_validation(*args,**kwargs):
 runner=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__);runner.__kwdefaults__=base.run_package_validation.__kwdefaults__;return runner(*args,**kwargs)
