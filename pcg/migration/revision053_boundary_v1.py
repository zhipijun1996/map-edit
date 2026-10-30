"""Exact user-revised, gated OUTPUT TOP fixtures; original crossing observer unchanged."""
import copy
from . import core
VERSIONS={'idea-0363f85c-16c0-4b5f-b3b0-461335608db7-enemies-3':'sha256:520f11823b852ac8501ea9b6ab55d7506c4172ce5aaac252a6a6119342676003','idea-96ba6bf1-9b60-470a-9128-54ae7ea44af3':'sha256:4d043ebce4d4b092a29242e0f31f28e49ddd3c5b7fab45d184ff5ce472c784d6'}
def applies(case,port):
 s=case.get('approved_implementation',{});f=case.get('explicit_exit_neighbor',{})
 return VERSIONS.get(s.get('reviewId'))==s.get('designVersion')and port.get('id')==f.get('portId')and port.get('face')=='TOP'and port.get('surface')=='ONE_WAY_PLATFORM'and port.get('permission')=='OUTPUT'and port.get('stagingPosition',[0,0])[1]==46

def neighbor(case,port):
 if not applies(case,port):return None
 f=case['explicit_exit_neighbor'];assert f['floor']==[port['position'][0]-48,-32,96,12]and f['copiedIntoModule']is False
 assert case['platforms'][f['index']]==f['floor']and f['index']in case['one_way_platform_indices']
 return dict(portId=port['id'],floor=f['floor'],source='explicit_test_neighbor',copiedIntoModule=False)

def local(case,port,direction,doc,offset=0):
 if not applies(case,port):return False
 assert direction=='egress'
 reference=doc['generationContract']['generation']['approvedImplementation']['boundaryInputs'];core.verify_artifacts([reference]);arrivals=core.read(core.resolve_artifact(reference['path']))['cases'];arrival=next(c for c in arrivals if c['route_spec']['to_port']==port['id']and c['route_spec']['from_port']!=port['id'])
 old=copy.deepcopy(case);case.clear();case.update(copy.deepcopy(arrival));case.update(id=old['id'],platforms=old['platforms'],one_way_platform_indices=old['one_way_platform_indices'],migration_probe=old['migration_probe']);case['spawn'][0]+=offset
 case['migration_probe']['userRevision053']=dict(wholeCanonicalArrival=True,realBellGate=True,neighborNotOwned=True,fullBodyOriginalObserver=True);case['max_frames']=min(3600,arrival['max_frames']);return True

def exit(case,doc,physics):
 port=next(p for p in doc['generationContract']['ports']if p['id']==case['route_spec']['to_port'])
 if not applies(case,port):return None
 v=physics.fresh(case,'continuous-exit');n=neighbor(v,port)
 # This frozen canonical program already shoots the real bell, jumps through
 # the original gate and lands on that same explicitly owned neighbor.
 v['migration_probe']=dict(kind='continuous_exit',portId=port['id'],direction='egress',boundary=port['position'],normal=port['normal'],neighbor=n,body=[24,36],noIntermediateReset=True,originalRouteId=case['route_spec']['id'],scope='complete canonical enemy/carrier arrival, actual bell opening and upward gate crossing; no second dock or duplicate neighbor')
 v['module_sha256']=physics.module_hash(v);return v
