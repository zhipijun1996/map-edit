"""Approved lift Cell mapping into the existing original native consumers."""
import sys,types
from . import godot_package as base, ideas_runtime_v2 as previous
from pcg.manual_review.lift_idea_v1 import decode,consumer_document
VERSION='foundation-data-runtime/approved-lift-v1'
SCENES=previous.SCENES
dependencies=previous.dependencies
def audit_cases(doc,cases,*,require_replay=True):
    content=decode(doc)
    _,audit=base.audit_cases(consumer_document(doc),cases,require_replay=require_replay,_extension=True)
    audit.update(approvedGeometryUnchanged=True,designMotionDecodedFromExactApprovedCells=True,originalPhysics=True)
    return content,audit
def decorate_manifest(m,stage):
    previous.decorate_manifest(m,stage)
    m['approvedLift']=dict(compiler=dict(path='pcg/migration/lift_runtime_v1.py',sha256=base.sha(__file__)),decoder=dict(path='pcg/manual_review/lift_idea_v1.py',sha256=base.sha(base.ROOT/'pcg/manual_review/lift_idea_v1.py')),hazardGlyphs='gears mapped to original saw Cell; exact centers/radii/motion; no rectangular fallback')
def compile_package(*a,**kw):return base.compile_package(*a,**kw,_extension=sys.modules[__name__])
def verify_package(folder,require_loaded=True):return base.verify_package(folder,require_loaded=require_loaded,_extension=sys.modules[__name__])
def run_package_validation(*a,**kw):
    f=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__);f.__kwdefaults__=base.run_package_validation.__kwdefaults__;return f(*a,**kw)
