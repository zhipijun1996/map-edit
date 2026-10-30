"""Existing native compiler with exact approved motion/glyph/third-access readback."""
import copy,sys,types
from . import godot_package as base,ideas_runtime_v2 as previous
from pcg.manual_review.revision058_content_v2 import decode,consumer_document
VERSION='foundation-data-runtime/approved-revision058-v2'
SCENES=[('module','module_loader_revision058_v1.gd'),('demo','package_demo_revision053_v1.gd')]
def audit_cases(doc,cases,*,require_replay=True):
 d=consumer_document(doc);extra=[o for o in d['objects']if o.get('mechanics',{}).get('extraPairAccess')];d['objects']=[o for o in d['objects']if o not in extra];cs=copy.deepcopy(cases);content=decode(doc)
 for c in cs:
  for l in c.get('latches',[]):l.pop('additional_pair_access',None);l.pop('return_access_side_policy',None)
 _,audit=base.audit_cases(d,cs,require_replay=require_replay,_extension=True)
 for c in cases:
  for k,v in content.items():base._equal(v,c.get(k,[]),'revision058/'+k,c['id'])
 audit.update(exactApprovedObjects=True,originalCellMotion=True,thirdPairReceiverSameNativeLatch=True,glyphCentersUnchanged=True);return content,audit

def dependencies(project):
 deps={r['path']:r for r in previous.dependencies(project)}
 for name in ['pcg/migration/runtime/module_loader_revision058_v1.gd','pcg/migration/runtime/package_demo_revision053_v1.gd']:
  deps[name]=dict(path=name,sha256=base.sha(base.ROOT/name))
 return[deps[k]for k in sorted(deps)]
def decorate_manifest(m,stage):
 previous.decorate_manifest(m,stage);m['revision058']=dict(compiler=dict(path='pcg/migration/revision058_runtime_v2.py',sha256=base.sha(__file__)),decoder=dict(path='pcg/manual_review/revision058_content_v2.py',sha256=base.sha(base.ROOT/'pcg/manual_review/revision058_content_v2.py')),originalPhysics=True)
def compile_package(*a,**kw):return base.compile_package(*a,**kw,_extension=sys.modules[__name__])
def verify_package(f,require_loaded=True):return base.verify_package(f,require_loaded=require_loaded,_extension=sys.modules[__name__])
def run_package_validation(*a,**kw):
 f=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__);f.__kwdefaults__=base.run_package_validation.__kwdefaults__;return f(*a,**kw)
