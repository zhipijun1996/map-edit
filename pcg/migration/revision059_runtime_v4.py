"""Same physical program; explicit native reward persistence adapter."""
import sys,types
from .revision059_runtime_v3 import *
from . import revision059_runtime_v3 as previous
VERSION='foundation-data-runtime/approved-revision059-v4'
SCENES=[('module','module_loader_revision059_v2.gd'),('demo','package_demo_revision053_v1.gd')]
def dependencies(project):
 deps={v['path']:v for v in previous.dependencies(project)}
 for name in ['pcg/migration/runtime/module_loader_revision059_v2.gd','pcg/manual_review/runtime/revision059_hq_binding_v2.gd']:
  deps[name]=dict(path=name,sha256=base.sha(base.ROOT/name))
 return[deps[k]for k in sorted(deps)]
def compile_package(*a,**kw):return base.compile_package(*a,**kw,_extension=sys.modules[__name__])
def verify_package(f,require_loaded=True):return base.verify_package(f,require_loaded=require_loaded,_extension=sys.modules[__name__])
def run_package_validation(*a,**kw):
 f=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__);f.__kwdefaults__=base.run_package_validation.__kwdefaults__;return f(*a,**kw)
