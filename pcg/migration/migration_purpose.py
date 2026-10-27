"""Preserve authored internal-dock assertions after exporting outer Ports.

Only the explicitly named internal waypoint aliases are changed in the view
passed to the original causal checker. All geometry, real traces, rewards,
resources, shots, and directional endpoint contracts remain the actual inputs.
"""
import copy
from pathlib import Path
from pcg.prototype.creative_batches.plains50_ports import recipes_v2 as ORIGINAL_PORTS
from pcg.prototype.creative_batches.junction_bridges import rules_v3 as ORIGINAL_BRIDGES
from pcg.prototype.creative_batches.junction_windgap import rules_v3 as ORIGINAL_WINDGAP
from pcg.prototype.creative_batches.batch30_d04 import api_v3 as ORIGINAL_D04
from pcg.prototype.creative_batches.batch30_d04r2 import rules_v1 as ORIGINAL_D04R2

REPO=Path(__file__).resolve().parents[2]
_AUTHORS={Path(module.__file__).resolve().relative_to(REPO).as_posix():module
          for module in (ORIGINAL_PORTS,ORIGINAL_BRIDGES,ORIGINAL_WINDGAP,ORIGINAL_D04,ORIGINAL_D04R2)}
SOURCE_DEPENDENCIES=sorted({Path(module.__file__).resolve()for module in _AUTHORS.values()}|
    {Path(path).resolve()for module in _AUTHORS.values()for path in getattr(module,'SOURCE_DEPENDENCIES',[])})
RUNNER_SCRIPT=None


def original_view(case):
    binding=case.get('migration_purpose',{})
    if binding.get('schema')!='pcg/internal-waypoint-purpose-binding/v1':
        raise ValueError('missing_explicit_internal_waypoint_binding')
    author=_AUTHORS.get(binding.get('originalAuthorSource'))
    if author is None:raise ValueError('unsupported_original_internal_waypoint_author')
    view=copy.deepcopy(case)
    declared=set(view['route_spec'].get('via_waypoints',[]))
    points=binding.get('waypoints',[])
    if {p['id']for p in points}!=declared:raise ValueError('internal_waypoint_bindings_incomplete')
    old_via=[]
    for point in points:
        old_id=point['sourcePortId']
        if old_id in (view['route_spec']['from_port'],view['route_spec']['to_port']):
            raise ValueError('external_route_endpoint_cannot_be_reinterpreted_as_waypoint')
        if point.get('interpretation')!='original_grounded_internal_dock':
            raise ValueError('unsupported_waypoint_interpretation')
        port=next((p for p in view['ports']if p['id']==old_id),None)
        if port is None:raise ValueError('original_waypoint_port_alias_missing')
        port['position']=list(point['position'])
        old_via.append(old_id)
    # The original checker still checks each original required visit against
    # real frames. No assertion is dropped or replaced by a pass flag.
    view['route_spec']['via_ports']=old_via
    return author,view


def purpose(case,raw):
    author,view=original_view(case)
    result=author.purpose(view,raw)
    checks={}
    for point in case['migration_purpose']['waypoints']:
        x,y=point['position']
        checks[point['id']]=any(frame.get('grounded')and abs(frame['x']-x)<30 and abs(frame['y']-y)<1
                               for frame in raw.get('frames',[]))
        if not checks[point['id']]:result['reasons'].append('missing_actual_internal_waypoint/'+point['id'])
    result.setdefault('causal',{})['migration_internal_waypoints']=checks
    result['ok']=not result['reasons']
    return result


def fixture_task_outcome(case,raw):
    author,view=original_view(case)
    function=getattr(author,'fixture_task_outcome',None)
    if function is not None:return function(view,raw)
    result=purpose(case,raw)
    return dict(ok=result['ok'],internalWaypointVisits=result['causal']['migration_internal_waypoints'])
