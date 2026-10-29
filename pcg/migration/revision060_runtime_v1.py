import copy,sys,types
from . import godot_package as base,revision059_runtime_v5 as stable
from pcg.manual_review.revision060_content_v1 import split,decode
VERSION='foundation-data-runtime/approved-revision060-v1'
SCENES=[('module','module_loader_revision060_v1.gd'),('demo','package_demo_revision053_v1.gd')]
def audit_cases(doc,cases,*,require_replay=True):
 d,custom=split(doc);cs=copy.deepcopy(cases)
 for o in d['objects']:o.get('mechanics',{}).get('runtimeParameters',{}).pop('designState',None)
 for c in cs:
  c.pop('approved_hq_cells',None)
  for p in c.get('moving_platforms',[]):p.pop('designState',None)
 _,audit=base.audit_cases(d,cs,require_replay=require_replay,_extension=True);content=decode(doc)
 for c in cases:
  for k,v in content.items():base._equal(v,c.get(k,[]),'revision060/'+k,c['id'])
 audit.update(explicitCustomCells=custom,originalPhysics=True,authorizedRepairScope=True);return content,audit

def dependencies(project):
 deps={v['path']:v for v in stable.dependencies(project)}
 for name in ['pcg/migration/runtime/module_loader_revision060_v1.gd','pcg/manual_review/runtime/revision060_binding_v1.gd','pcg/manual_review/runtime/revision060_support_start_v1.gd','pcg/manual_review/runtime/revision060_thorn_latch_v1.gd','pcg/manual_review/runtime/revision059_interception_observer_v1.gd']:
  deps[name]=dict(path=name,sha256=base.sha(base.ROOT/name))
 return[deps[k]for k in sorted(deps)]
def decorate_manifest(m,stage):
 stable.decorate_manifest(m,stage);m['revision060']=dict(compiler=dict(path='pcg/migration/revision060_runtime_v1.py',sha256=base.sha(__file__)),decoder=dict(path='pcg/manual_review/revision060_content_v1.py',sha256=base.sha(base.ROOT/'pcg/manual_review/revision060_content_v1.py')),originalPhysics=True)
def compile_package(*a,**kw):return base.compile_package(*a,**kw,_extension=sys.modules[__name__])
def verify_package(f,require_loaded=True):return base.verify_package(f,require_loaded=require_loaded,_extension=sys.modules[__name__])
def run_package_validation(*a,**kw):
 f=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__);f.__kwdefaults__=base.run_package_validation.__kwdefaults__;return f(*a,**kw)
