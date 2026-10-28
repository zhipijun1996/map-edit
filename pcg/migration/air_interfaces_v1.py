"""Explicit AIR witness fixtures on the existing Harness, without neighbor floors."""
import copy
from . import core


def fixture(case,port,direction,offset=0,kind='local_boundary',label=None):
    from .physics import fresh
    if not case.get('approved_first30'):raise ValueError('air_fixture_requires_registered_air_consumer')
    if not((port['face']=='TOP'and port['permission']=='INPUT'and direction=='ingress')or(port['face']=='BOTTOM'and port['permission']=='OUTPUT'and direction=='egress')):
        raise ValueError('unsupported_air_direction_or_permission')
    value=fresh(case,label or f"{port['id']}-{direction}-{offset}");x,y=port['position']
    start=[x+offset,y-48];target=[x,y+48]
    value.update(spawn=start,entry_port=start[:],exit_port=target,goal=[x-9,y+43,18,10],
        control_plan=[dict(op='axis',value=0,trigger=dict(after=0))],max_frames=240,
        air_probe_points=[start,target],air_goal_probe=dict(portId=port['id'],direction=direction,boundary=[x,y]))
    neighbor=dict(portId=port['id'],source='explicit_test_neighbor_air',floor=None,
        airRectangle=dict(x=x-64,y=y-128 if direction=='ingress'else y,w=128,h=128),copiedIntoModule=False)
    value['migration_probe']=dict(kind=kind,portId=port['id'],direction=direction,boundary=[x,y],normal=port['normal'],neighbor=neighbor,body=[24,36],
        noIntermediateReset=True,originalRouteId=case['route_spec']['id'],scope='actual downward full-body AIR crossing, not grounded docking or arbitrary incoming velocity')
    return value


def local_cases(case,port):
    direction='ingress'if port['permission']=='INPUT'else'egress'
    return[fixture(case,port,direction,offset)for offset in(-2,0,2)]


def entry(case,port):
    return fixture(case,port,'ingress',kind='continuous_entry',label='continuous-entry')


def exit(case,port):
    from .physics import fresh
    value=fresh(case,'continuous-exit');x,y=port['position']
    value['migration_probe']=dict(kind='continuous_exit',portId=port['id'],direction='egress',boundary=[x,y],normal=port['normal'],
        neighbor=dict(portId=port['id'],source='explicit_test_neighbor_air',floor=None,airRectangle=dict(x=x-64,y=y,w=128,h=128),copiedIntoModule=False),
        body=[24,36],noIntermediateReset=True,originalRouteId=case['route_spec']['id'])
    return value
