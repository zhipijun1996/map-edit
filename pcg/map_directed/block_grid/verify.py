"""Measure actual boundary crossings and state handoffs from frozen Motor traces."""
from .contracts import placed_cells,raster

def verify(c,case,result):
    errors=[];crossings=[];by={m['id']:m for m in c['modules']};frames=result.get('frames',[])
    owned=set().union(*(placed_cells(m,m['spec']['placement'])for m in c['modules']))
    outside=[]
    for f in frames:
        if not raster([f['x']-12,f['y']-18,24,36])<=owned:outside.append(f['frame'])
    if outside:errors.append('body_left_reserved_map_blocks')
    if any(f.get('actor_epoch',1)!=1 for f in frames):errors.append('actor_epoch_changed')
    steps=case['r2_semantics']['logical_route'];logs=result.get('pilot',{}).get('legs',[])
    for i,step in enumerate(steps):
        eid=step['edge_id'];source,dest=step['from'],step['to'];prefix=f'{i:03d}-{eid}-'
        legs=[q for q in logs if q['id'].startswith(prefix)]
        if not legs or not all(q.get('ok')for q in legs):continue
        start,end=legs[0]['start']['frame'],legs[-1]['end']['frame'];m=by[source];p=m['ports'][eid];offset=m['spec']['placement']
        normal=p['normal'];axis=0 if normal[0]else 1;axis_key='x'if axis==0 else'y';tangent='y'if axis==0 else'x';half=18 if axis==0 else 12
        plane=p['position'][axis]+offset[axis];a=p['aperture'];lo=a[1-axis]+offset[1-axis];hi=lo+a[3-axis]
        samples=[f for f in frames if start<=f['frame']<=end];found=[]
        for left,right in zip(samples,samples[1:]):
            before=(left[axis_key]-plane)*normal[axis];after=(right[axis_key]-plane)*normal[axis]
            if before<=0<after:
                fraction=(plane-left[axis_key])/(right[axis_key]-left[axis_key]);at=left[tangent]+fraction*(right[tangent]-left[tangent])
                fits=at-half>=lo-.1 and at+half<=hi+.1
                found.append(dict(frame=right['frame'],tangent=at,aperture_ok=fits,
                    before={k:left.get(k)for k in ['x','y','vx','vy','grounded','shot_charges','shot_cooldown','jumps_used','energy','hp','traversal_state','module_clock']},
                    after={k:right.get(k)for k in ['x','y','vx','vy','grounded','shot_charges','shot_cooldown','jumps_used','energy','hp','traversal_state','module_clock']}))
        if not found:errors.append('boundary_crossing_missing/'+str(i)+'/'+eid)
        elif any(not f['aperture_ok']for f in found):errors.append('boundary_aperture_bypass/'+str(i)+'/'+eid)
        crossings.append(dict(step=i,edge=eid,**{'from':source,'to':dest},source_version=m['content_version'],destination_version=by[dest]['content_version'],samples=found))
    return dict(ok=result['ok']and not errors,physics_ok=result['ok'],errors=sorted(set(errors)),unreserved_body_frames=outside[:10],crossings=crossings,
        scope='Concrete trajectory/pose/state only; no arbitrary input, ability-lock or human fun proof')
