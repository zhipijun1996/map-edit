"""Exact new TOP one-way layouts: complete canonical transit, original body observer."""
import copy
from . import core
VERSIONS={'idea-plains-hq01-001': 'sha256:f6789c34bba2d7c7075840f2a0dbfc36cfa57915e28c0a84433ca0d4eb75560d', 'idea-plains-hq02-001': 'sha256:a7aa4349d4c46250003af40b21eebd06991ece5da0017e8a919454a3a01a5792', 'idea-plains-hq05-001': 'sha256:61603ff895aba57db1c64c6875bc26ccdb39497629e5e725eb6453373aec7f38'}
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
