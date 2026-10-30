"""Native data compiler for explicit approved HQ Cells, original protected game intact."""
import copy,sys,types
from . import godot_package as base,revision058_runtime_v1 as previous
from pcg.manual_review.revision059_hq_content_v1 import split,decode
VERSION='foundation-data-runtime/approved-revision059-v1'
SCENES=[('module','module_loader_revision059_v1.gd'),('demo','package_demo_revision053_v1.gd')]
def audit_cases(doc,cases,*,require_replay=True):
 d,custom=split(doc);cs=copy.deepcopy(cases)
 for c in cs:c.pop('approved_hq_cells',None)
 _,audit=base.audit_cases(d,cs,require_replay=require_replay,_extension=True)
 content=decode(doc)
 for c in cases:
  for k,v in content.items():base._equal(v,c.get(k,[]),'approved-hq/'+k,c['id'])
 audit.update(exactApprovedGeometry=True,explicitCustomCells=custom,originalPhysics=True);return content,audit

def dependencies(project):
 deps={v['path']:v for v in previous.dependencies(project)}
 files=[base.ROOT/'pcg/migration/runtime/module_loader_revision059_v1.gd',*(base.ROOT/'pcg/manual_review/runtime').glob('revision059_*.gd')]
 for p in files:deps[p.relative_to(base.ROOT).as_posix()]=dict(path=p.relative_to(base.ROOT).as_posix(),sha256=base.sha(p))
 return[deps[k]for k in sorted(deps)]
def decorate_manifest(m,stage):
 previous.decorate_manifest(m,stage);m['revision059']=dict(compiler=dict(path='pcg/migration/revision059_runtime_v1.py',sha256=base.sha(__file__)),decoder=dict(path='pcg/manual_review/revision059_hq_content_v1.py',sha256=base.sha(base.ROOT/'pcg/manual_review/revision059_hq_content_v1.py')),originalPhysics=True)
def compile_package(*a,**kw):return base.compile_package(*a,**kw,_extension=sys.modules[__name__])
def verify_package(f,require_loaded=True):return base.verify_package(f,require_loaded=require_loaded,_extension=sys.modules[__name__])
def run_package_validation(*a,**kw):
 f=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__);f.__kwdefaults__=base.run_package_validation.__kwdefaults__;return f(*a,**kw)
