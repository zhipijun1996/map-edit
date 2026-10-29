"""Finite native dependency set: later diagnostics cannot invalidate compiled packages."""
import sys,types
from .revision059_runtime_v4 import *
from . import revision058_runtime_v1 as stable
VERSION='foundation-data-runtime/approved-revision059-v5'
NATIVE_CELLS=['revision059_group_motion_v1.gd','revision059_hit_turret_v1.gd','revision059_hq_binding_v1.gd','revision059_hq_binding_v2.gd','revision059_reward_pair_v1.gd','revision059_turret_latch_v1.gd']
def dependencies(project):
 deps={v['path']:v for v in stable.dependencies(project)}
 names=['pcg/migration/runtime/module_loader_revision059_v2.gd']+['pcg/manual_review/runtime/'+n for n in NATIVE_CELLS]
 for name in names:deps[name]=dict(path=name,sha256=base.sha(base.ROOT/name))
 return[deps[k]for k in sorted(deps)]
def compile_package(*a,**kw):return base.compile_package(*a,**kw,_extension=sys.modules[__name__])
def verify_package(f,require_loaded=True):return base.verify_package(f,require_loaded=require_loaded,_extension=sys.modules[__name__])
def run_package_validation(*a,**kw):
 f=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__);f.__kwdefaults__=base.run_package_validation.__kwdefaults__;return f(*a,**kw)
