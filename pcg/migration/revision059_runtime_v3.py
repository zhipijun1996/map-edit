"""Explicit HQ01 frozen-example metadata belongs to the group Cell, not platform API."""
import copy,sys,types
from .revision059_runtime_v1 import *
from . import revision059_runtime_v1 as previous
VERSION='foundation-data-runtime/approved-revision059-v3'
def audit_cases(doc,cases,*,require_replay=True):
 d,custom=split(doc);cs=copy.deepcopy(cases)
 for o in d['objects']:
  params=o.get('mechanics',{}).get('runtimeParameters',{})
  if 'designState'in params:
   state=params.pop('designState');assert state in ['FROZEN_EXAMPLE','MOVING_EXAMPLE']
   if state=='FROZEN_EXAMPLE':assert any(s['kind']=='group_motion'for s in custom)
 for c in cs:
  c.pop('approved_hq_cells',None)
  for p in c.get('moving_platforms',[]):p.pop('designState',None)
 _,audit=base.audit_cases(d,cs,require_replay=require_replay,_extension=True);content=decode(doc)
 for c in cases:
  for k,v in content.items():base._equal(v,c.get(k,[]),'approved-hq/'+k,c['id'])
 audit.update(exactApprovedGeometry=True,explicitCustomCells=custom,originalPhysics=True,frozenExampleUsesOriginalBellControl=True);return content,audit

def compile_package(*a,**kw):return base.compile_package(*a,**kw,_extension=sys.modules[__name__])
def verify_package(f,require_loaded=True):return base.verify_package(f,require_loaded=require_loaded,_extension=sys.modules[__name__])
def run_package_validation(*a,**kw):
 f=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__);f.__kwdefaults__=base.run_package_validation.__kwdefaults__;return f(*a,**kw)
