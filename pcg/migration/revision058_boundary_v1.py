"""Exact new TOP one-way layouts: complete canonical transit, original body observer."""
import copy
from . import core
VERSIONS={'42': 'sha256:9dca56de7eb4c3b97819c90f8b84fe71472384dc9a3e6e2f01e6ccb7d3bd0df7', 'idea-31639e2c-1a4a-487c-b1ea-c52522549fa8-left-top-1x2': 'sha256:1d5fdf9e4b2aa8ce9ca7146d75f9caac79965dd83034131295ec244949809469', 'idea-31639e2c-1a4a-487c-b1ea-c52522549fa8-left-bottom-1x2': 'sha256:8c5c858793977891842269f89ad480b9ea5d05f441571b44433e65f969a79159', 'idea-31639e2c-1a4a-487c-b1ea-c52522549fa8-left-top-2x1': 'sha256:8315ca17760b09df75cb1ea052a585078d01cbea69f8373340e90838fc49710c', 'idea-31639e2c-1a4a-487c-b1ea-c52522549fa8-left-bottom-2x1': 'sha256:235c8fa4afc3067b4d23de44d630ded9017b548890d676da6ea74358f16b823d', 'idea-31639e2c-1a4a-487c-b1ea-c52522549fa8-left-top-2x2': 'sha256:fd98f5f5678200e9c7c1f1d04d359cf3bb06fb42c5d7945dc3450207079d96fe', 'idea-31639e2c-1a4a-487c-b1ea-c52522549fa8-left-bottom-2x2': 'sha256:33e8e715ec5ff584ae239d525d18a18d30de8758dc12b2cd63ceacedd388e7bb', 'idea-interface-s02-001': 'sha256:04c2e467b022ced8d104b511957371680557b9293ad29ee56afb0bd4d35e31fe', 'idea-interface-s07-001': 'sha256:b8ab5b8d9d0ccde57364c5940570abe29ffcd803da965a6fb3ac2770f0dffa9a', 'idea-interface-s11-001': 'sha256:2466b9d1e6d36f235d5a9e1723d0a87713e8203cf61880ee5794e3c2313840c0', 'idea-interface-s15-001': 'sha256:bdf4d05125ab207e60879d17a9d74ea4b59f3a52cf88a551c08d59ae7c52e2f5', 'idea-interface-s09-001': 'sha256:fc7c50a764b74019fef1aa196ad9c74c32494ae491fb17822f9b246cab1c7033', 'idea-interface-s12-001': 'sha256:c0c0d7573e9ddf42681e19433325058c9c8e7f000f690e6207c913b491d19dd2'}
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
