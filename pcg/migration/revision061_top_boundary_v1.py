"""Exact new TOP one-way layouts: complete canonical transit, original body observer."""
import copy
from . import core
VERSIONS={'idea-spec02-s02-001': 'sha256:0bda2758e549614457cf07f0010e524b27abe6d5807bdd1f4d55a408ac927121', 'idea-spec02-s07-001': 'sha256:2e7b95062f7b71e0c43f1aaa3a417a391e517384fa8aaf6be8f195a53ce45e4b', 'idea-spec02-s08-001': 'sha256:bf6273dbd6f8c910e5e440fc5bb81217601f18ea789010a7a51f52832d0270a0', 'idea-spec02-s10-001': 'sha256:0f6dc21ed04b996082548b16856841672a93b9fea3514548792cb7b41c0ad4a7', 'idea-spec02-s11-001': 'sha256:ca5de5b99d80a1104ceec354e144cbde7654ad9266a82790ac92586a5f424056', 'idea-spec02-s12-001': 'sha256:d5a7213383ec21e98acab5299550d34c00165a09d67774b7919d84b54ed5e113', 'idea-spec02-s13-001': 'sha256:bea219b40406f2f6baee66350af2f55218e55fefc6ba96abdba298493e386532'}
def applies(case,port):
 s=case.get('approved_implementation',{});return VERSIONS.get(s.get('reviewId'))==s.get('designVersion')and port.get('face')=='TOP'and port.get('surface')=='ONE_WAY_PLATFORM'and port.get('stagingPosition',[0,0])[1]==14

def side_start(case,port,offset):
 s=case.get('approved_implementation',{})
 if VERSIONS.get(s.get('reviewId'))==s.get('designVersion')and port.get('surface')=='ONE_WAY_PLATFORM'and port['normal'][0]and offset==2:case['spawn'][1]=port['stagingPosition'][1]-4

def dock(x,y,after=1):return[dict(op='settle',target_x=x,deadband=.6,trigger=dict(after=0)),dict(op='wait',trigger=dict(after=after,state='grounded',migration_goal=[x-4,y-3,8,6],timeout=240))]
def prefix(x,y):return[dict(op='drop_through',trigger=dict(after=1))]+dock(x,y)
def local(case,port,direction,doc,offset=0):
 if not applies(case,port):return False
 ref=doc['generationContract']['generation']['approvedImplementation']['boundaryInputs'];core.verify_artifacts([ref]);cs=core.read(core.resolve_artifact(ref['path']))['cases'];old=copy.deepcopy(case)
 route=next(c for c in cs if c['route_spec']['from_port'if direction=='ingress'else'to_port']==port['id']and c['route_spec']['from_port']!=c['route_spec']['to_port']);case.clear();case.update(copy.deepcopy(route));case.update(id=old['id'],platforms=old['platforms'],one_way_platform_indices=old['one_way_platform_indices'],migration_probe=old['migration_probe'])
 x,y=port['stagingPosition']
 if direction=='ingress':case['spawn']=[x+offset,-50];case['control_plan']=prefix(x,y)+case['control_plan']
 else:case['spawn'][0]+=offset;case['control_plan']+=dock(x,y,6)+[dict(op='jump',trigger=dict(after=1)),dict(op='jump_release',trigger=dict(after=8))]+dock(x,-50);case['goal']=[x-9,-55,18,10]
 case['max_frames']=3600;case['migration_probe']['revision058Top']=dict(wholeCanonicalTransit=True,explicitNeighborTop=-32,originalFullBodyObserver=True);return True

def entry(case,doc,physics):
 port=next(p for p in doc['generationContract']['ports']if p['id']==case['route_spec']['from_port'])
 if not applies(case,port):return None
 v=physics.fresh(case,'continuous-entry');n=physics.exterior_floor(v,port);x,y=port['stagingPosition'];v['spawn']=[x,-50];v['control_plan']=prefix(x,y)+v['control_plan'];v['max_frames']=3600;v['migration_probe']=dict(kind='continuous_entry',portId=port['id'],direction='ingress',boundary=port['position'],normal=port['normal'],neighbor=n,body=[24,36],noIntermediateReset=True,originalRouteId=case['route_spec']['id'],scope='through owned top deck and complete frozen route to real interior support');v['module_sha256']=physics.module_hash(v);return v

def exit(case,doc,physics):
 port=next(p for p in doc['generationContract']['ports']if p['id']==case['route_spec']['to_port'])
 if not applies(case,port):return None
 v=physics.fresh(case,'continuous-exit');n=physics.exterior_floor(v,port);x,y=port['stagingPosition'];v['control_plan']+=dock(x,y,6)+[dict(op='jump',trigger=dict(after=1)),dict(op='jump_release',trigger=dict(after=8))]+dock(x,-50);v['goal']=[x-9,-55,18,10];v['max_frames']=3600;v['migration_probe']=dict(kind='continuous_exit',portId=port['id'],direction='egress',boundary=port['position'],normal=port['normal'],neighbor=n,body=[24,36],noIntermediateReset=True,originalRouteId=case['route_spec']['id'],scope='complete frozen route before short native upward jump to compatible adjacent deck');v['module_sha256']=physics.module_hash(v);return v
