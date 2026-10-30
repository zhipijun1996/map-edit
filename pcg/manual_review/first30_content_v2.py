"""Decode approved cells through the existing decoder, with one additive group Cell."""
import copy
from pcg.migration import godot_package as native


def decode(doc):
    ordinary=copy.deepcopy(doc);objects=ordinary['objects']
    groups=[];accesses=[]
    for bell in list(objects):
        m=bell.get('mechanics',{})
        if bell.get('type')=='bell' and m.get('service')=='ShotLatch.add_access_bell' and m.get('returnSideOnly')is False:
            accesses.append(dict(id=bell['sourceId'].removesuffix('/return'),position=native._center(bell)))
            objects.remove(bell)
    bells=[o for o in objects if o.get('type')=='bell' and o.get('mechanics',{}).get('kind')=='retractable_gears/v1']
    for bell in bells:
        bands=[o for o in objects if o.get('mechanics',{}).get('kind')=='retractable_gears/v1' and o.get('type')=='hazard' and o['mechanics']['bellId']==bell['id']]
        if len(bands)!=2:raise ValueError('approved_06_requires_exactly_two_group_bands')
        groups.append(dict(id=bell['sourceId'],bell=native._center(bell),initial_extended=True,
            bands=[dict(id=o['id'],rect=native._rect(o))for o in bands]))
        removed={bell['id'],*(o['id']for o in bands)}
        objects[:]=[o for o in objects if o['id']not in removed]
    content=native.content_from_objects(ordinary)
    for access in accesses:
        latch=next(l for l in content['latches']if l['id']==access['id'])
        latch.update(return_access=access['position'],return_access_side_policy='any')
    if groups:
        content['retractable_groups']=groups
        content['latches'] += [dict(id=g['id'],bell=g['bell'],gate=[*g['bell'],1,1],open_seconds=0,kind='retractable_gears/v1')for g in groups]
    return content
