"""Add N25 loop data and approved chest glyphs to the existing package compiler."""
import copy,sys,types
from . import godot_package as base
from pcg.manual_review.ideas_content_v1 import decode,reward_consumer_document,KIND
VERSION='foundation-data-runtime/approved-ideas-v1'
SCENES=[('module','module_loader_ideas_v1.gd'),('demo','package_demo_v3.gd')]
def audit_cases(doc,cases,*,require_replay=True):
 content=decode(doc);d=reward_consumer_document(doc);cs=copy.deepcopy(cases);removed=set()
 for o in d['objects']:
  if o.get('trackId')and next((t for t in d['objects']if t['id']==o['trackId']),{}).get('mode')=='loop':removed|={o['id'],o['trackId']}
 for o in d['objects']:
  if o.get('targetId')in removed:removed.add(o['id'])
 d['objects']=[o for o in d['objects']if o['id']not in removed]
 loopids={v['platform_id']for v in content['moving_platforms']if v.get('trajectory_kind')==KIND}
 for c in cs:
  c['moving_platforms']=[v for v in c['moving_platforms']if v['platform_id']not in loopids];c['latches']=[v for v in c['latches']if v.get('ferry_id')not in loopids]
 _,audit=base.audit_cases(d,cs,require_replay=require_replay,_extension=True)
 for c in cases:
  for key,value in content.items():base._equal(value,c.get(key,[]),'approved_ideas/'+key,c['id'])
 audit.update(closedLoopConsumer='existing batch30_blockn25 Cell and original ModuleMovingPlatform',nativeReward='original SimpleRoomReward, no collision body; diagram glyph normalized only for legacy consumer audit',approvedGeometryUnchanged=True,resourcesReset=False)
 return content,audit

def dependencies(project):
 rows=base._dependencies(project,base.EXTENDED_VERSION)
 for name in ['pcg/migration/runtime/module_loader_ideas_v1.gd','pcg/manual_review/runtime/ideas_definition_v1.gd','pcg/prototype/creative_batches/batch30_blockn25/install_v1.gd','pcg/prototype/creative_batches/batch30_blockn25/loop_definition_v1.gd']:rows.append(dict(path=name,sha256=base.sha(base.ROOT/name)))
 return sorted(rows,key=lambda v:v['path'])
def decorate_manifest(m,stage):m['approvedIdeas']=dict(compiler= dict(path='pcg/migration/ideas_runtime_v1.py',sha256=base.sha(__file__)),decoder=dict(path='pcg/manual_review/ideas_content_v1.py',sha256=base.sha(base.ROOT/'pcg/manual_review/ideas_content_v1.py')),originalPhysics=True,shotCapacity=1,noSeamResourceReset=True)
def compile_package(*a,**kw):return base.compile_package(*a,**kw,_extension=sys.modules[__name__])
def verify_package(folder,require_loaded=True):return base.verify_package(folder,require_loaded=require_loaded,_extension=sys.modules[__name__])
def run_package_validation(*a,**kw):
 f=types.FunctionType(base.run_package_validation.__code__,{**base.__dict__,'verify_package':verify_package},argdefs=base.run_package_validation.__defaults__);f.__kwdefaults__=base.run_package_validation.__kwdefaults__;return f(*a,**kw)
