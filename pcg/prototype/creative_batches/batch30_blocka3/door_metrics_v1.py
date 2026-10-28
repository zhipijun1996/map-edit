"""Direction-aware observation of the same actual original gate/body/shot trace."""
def inspect(c,r,sign=None,start=0,end=None):
    sign=sign or(1 if c['route_spec']['from_port']=='A'else-1)
    fs=[f for f in r.get('frames',[])if f['frame']>=start and(end is None or f['frame']<=end)]
    latch=c['latches'][0];gx,gy,gw,gh=latch['gate'];pid=latch['id']
    shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))]
    hits=[e for e in r.get('plains',{}).get('events',[])if e.get('type')=='bell_open'and e.get('id')==pid and e['frame']>=start and(end is None or e['frame']<=end)]
    door=[f for f in fs if f['x']-12<gx+gw and f['x']+12>gx and f['y']-18<gy+gh and f['y']+18>gy]
    first_shot=shots[0]['frame']if shots else None;hit=hits[0]['frame']if hits else None
    clear=next((f['frame']for f in fs if first_shot is not None and f['frame']>=first_shot and(f['x']-12>=gx+gw if sign>0 else f['x']+12<=gx)),None)
    bad=[f['frame']for f in door if next((b.get('open')for b in f.get('plains',{}).get('bells',[])if b.get('id')==pid),False)is not True]
    closed=[f['frame']for f in fs if next((b.get('open')for b in f.get('plains',{}).get('bells',[])if b.get('id')==pid),True)is False]
    fired=next((v for v in r.get('fired_commands',[])if v.get('op')=='shoot'and v.get('frame')==first_shot),{})
    first_air=bool(shots and not fired.get('grounded',shots[0].get('grounded',True))and not any(e.get('type')=='ground_jump'for e in shots[0].get('accepted',[]))and hit is not None and hit>=first_shot and(len(shots)==1 or hit<shots[1]['frame']))
    return dict(direction=sign,actual_shot_frames=[dict(frame=f['frame'],grounded=f.get('grounded'),x=f['x'],y=f['y'],shot_charges=f.get('shot_charges'))for f in shots],actual_bell_open_events=hits,first_shot_frame=first_shot,first_hit_frame=hit,body_door_frames=[f['frame']for f in door],full_body_clear_frame=clear,projectile_flight_ticks=hit-first_shot if hit is not None and first_shot is not None else None,hit_to_full_body_clear_ticks=clear-hit if clear is not None and hit is not None else None,configured_open_ticks=round(latch['open_seconds']*60),closed_during_body_overlap=bad,actual_closed_frames=closed,first_air_shot_open=first_air,anti_pinch='OriginalShotLatch gate_rect.grow(24) + originalcollisiondeferredclose unchanged')
