"""Correct the original one-sided reporting assumption for below-floor routes.

Same conservative24x36 swept bounding rectangles as originalworkshop evaluate;
this is observation of actual frames, never a replacement physics solver.
"""
def inspect(case,result):
    frames=result.get('frames',[]);hits=[];gaps=[];rects=[];channel=[]
    for thorn in case.get('thorns',[]):
        p=case['platforms'][thorn['platform_index']]
        rect=[p[0]+thorn['start_offset'],p[1]+p[3]if thorn['face']=='bottom'else p[1]-thorn['depth'],thorn['length'],thorn['depth']]
        rects.append(dict(surface_id=thorn['surface_id'],rect=rect))
        x,y,w,h=rect
        for a,b in zip(frames,frames[1:]):
            x0=min(a['x'],b['x'])-12;x1=max(a['x'],b['x'])+12;y0=min(a['y'],b['y'])-18;y1=max(a['y'],b['y'])+18
            overlap=x0<x+w and x1>x and y0<=y+h and y1>=y
            if overlap:hits.append(dict(frame=b['frame'],surface=thorn['surface_id'],sweep=[x0,y0,x1-x0,y1-y0],thorn=rect))
            if x0<x+w and x1>x:
                if y1<=y:gaps.append(y-y1)
                elif y0>=y+h:gaps.append(y0-y-h)
                else:gaps.append(-min(y1-y,y+h-y0))
    if len(rects)==2:
        upper=next(v['rect']for v in rects if v['surface_id']=='upper-slot');lower=next(v['rect']for v in rects if v['surface_id']=='lower-slot')
        left=max(upper[0],lower[0]);right=min(upper[0]+upper[2],lower[0]+lower[2]);top=upper[1]+upper[3];bottom=lower[1]
        channel=[f['frame']for f in frames if left<=f['x']<=right and f['y']-18>=top and f['y']+18<=bottom]
    return dict(body=[24,36],thorn_rects=rects,swept_intersections=hits,minimum_vertical_clearance_when_x_overlaps=min(gaps,default=None),air_channel_fullbody_frames=channel,method='Originalconservative segmentboundingAABB, properfull2Dintersection; actualGodotHP/hazardsremainauthoritative')
