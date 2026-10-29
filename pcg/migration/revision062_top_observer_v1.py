"""Read-only original-neighbor contact proof, limited to exact second-round S12.
Uses the original PlayerMotor.safe_margin, actual support identity and AABB.
No physical data, quality thresholds, crossing/health/aperture gates are changed.
"""
import inspect,math
from . import revision061_top_observer_v1 as old
VERSION='sha256:d5a7213383ec21e98acab5299550d34c00165a09d67774b7919d84b54ed5e113'
SAFE_MARGIN=.0799999982118607

def native_neighbor_contact(case,frame,neighbor):
 floor=neighbor['floor'];indices=[i for i,p in enumerate(case['platforms'])if p==floor]
 if len(indices)!=1 or indices[0]not in case.get('one_way_platform_indices',[]):return False
 if frame.get('support_id')!='Platform'+str(indices[0]):return False
 bottom=frame['y']+18;gap=floor[1]-bottom
 return -.000001<=gap<=SAFE_MARGIN+.000001 and floor[0]<=frame['x']-12 and frame['x']+12<=floor[0]+floor[2]

_source=inspect.getsource(old.observe);needle="abs(f['y']+50)<=.05";assert needle in _source
_source=_source.replace(needle,'native_neighbor_contact(case,f,n)').replace('revision061_explicit_TOP_neighbor_caught_canonical_ascent','revision062_native_neighbor_contact_within_original_safe_margin')
_namespace={**old.__dict__,'VERSIONS':{'idea-spec02-s12-001':VERSION},'native_neighbor_contact':native_neighbor_contact};exec(compile(_source,__file__,'exec'),_namespace)
def observe(case,raw):
 result=_namespace['observe'](case,raw)
 if result:result.update(originalNativeSafeMargin=SAFE_MARGIN,requiresActualNeighborSupportId=True,requiresActualBodyInsideNeighbor=True)
 return result
