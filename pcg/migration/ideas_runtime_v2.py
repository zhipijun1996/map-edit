"""Original diver binding, with the same exact loop/reward data audit."""
import sys,types
from . import godot_package as base,ideas_runtime_v1 as previous,review_air_runtime as air
VERSION='foundation-data-runtime/approved-ideas-v2'
SCENES=[('module','module_loader_ideas_v2.gd'),('demo','package_demo_v3.gd')]
audit_cases=previous.audit_cases
def dependencies(project):
 rows={r['path']:r for r in previous.dependencies(project)+air.dependencies(project)}
 name='pcg/migration/runtime/module_loader_ideas_v2.gd';rows[name]=dict(path=name,sha256=base.sha(base.ROOT/name));return[rows[k]for k in sorted(rows)]
def decorate_manifest(m,stage):
 previous.decorate_manifest(m,stage);m['approvedIdeas']['nativeDiverBinding']='existing air_enemy_binding_v1: original EnemyActor, definition, motor, attacks, HP and hit refunds';m['approvedIdeas']['compiler']=dict(path='pcg/migration/ideas_runtime_v2.py',sha256=base.sha(__file__))
def compile_package(*a,**kw):return base.compile_package(*a,**kw,_extension=sys.modules[__name__])
def verify_package(folder,require_loaded=True):return base.verify_package(folder,require_loaded=require_loaded,_extension=sys.modules[__name__])
def run_package_validation(*a,**kw):
 f=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__);f.__kwdefaults__=base.run_package_validation.__kwdefaults__;return f(*a,**kw)
