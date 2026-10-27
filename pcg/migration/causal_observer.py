"""Attribute an actual causal episode instead of assuming the first shot did it.

This is a narrow measurement repair for two existing assertions. It neither
filters the recorded trace nor makes extra shots/jumps an admissible cost. Each
correction needs an unambiguous accepted real projectile, its impact and the
specific bell opening, followed by the original complete-body/world outcome.
"""
from __future__ import annotations
import copy
import math


METHOD='pcg/actual-causal-episode-observer/v1'


def _same_direction(a,b):
    return isinstance(a,list)and isinstance(b,list)and len(a)==len(b)==2 and max(abs(x-y)for x,y in zip(a,b))<1e-5


def _beam_contains(origin,impact):
    if not all(k in origin for k in ('muzzle','direction'))or'point'not in impact:return False
    dx,dy=origin['direction'];x=impact['point'][0]-origin['muzzle'][0];y=impact['point'][1]-origin['muzzle'][1]
    return x*dx+y*dy>=-.05 and abs(x*dy-y*dx)<.1


def _projectile_episodes(raw):
    frames={f['frame']:f for f in raw.get('frames',[])}
    events=raw.get('plains',{}).get('events',[])
    origins=[]
    for origin in events:
        if origin.get('type')!='shot_origin':continue
        frame=frames.get(origin.get('frame'))
        if frame is None:continue
        accepted=[a for a in frame.get('accepted',[])if a.get('type')=='shot'and a.get('serial')==origin.get('shot_id')
                  and _same_direction(a.get('direction'),origin.get('direction'))]
        if len(accepted)!=1:continue
        previous=frames.get(origin['frame']-1,raw.get('entry_snapshot',{}))
        if 'grounded'not in previous:continue
        origins.append(dict(origin=origin,frame=frame,previous=previous,airborne=previous['grounded']is False))
    result=[];consumed=set()
    for impact in sorted((e for e in events if e.get('type')=='projectile_impact'),key=lambda e:e['frame']):
        compatible=[o for o in origins if o['origin']['shot_id']not in consumed
            and o['origin']['frame']<=impact['frame']
            and _same_direction(o['origin'].get('direction'),impact.get('direction'))and _beam_contains(o['origin'],impact)]
        # Impact events do not carry serials. Ambiguous same-line projectiles do
        # not establish attribution; never choose a convenient one by proximity.
        if len(compatible)!=1:continue
        episode=compatible[0];consumed.add(episode['origin']['shot_id'])
        result.append({**episode,'impact':impact})
    return result


def _bell_episodes(case,raw):
    episodes=_projectile_episodes(raw)
    for latch in case.get('latches',[]):
        bell=latch.get('bell');gate=latch.get('gate')
        if not isinstance(bell,list)or len(bell)!=2 or not isinstance(gate,list)or len(gate)!=4:continue
        for hit in raw.get('plains',{}).get('events',[]):
            if hit.get('type')!='bell_open'or hit.get('id')!=latch.get('id'):continue
            candidates=[]
            for episode in episodes:
                point=episode['impact']['point']
                # Original ShotLatch receiver28x34, original PlayerProjectile
                # circle radius3. The opening is an actual engine event too.
                primary=abs(point[0]-bell[0])<=17.1 and abs(point[1]-bell[1])<=20.1
                if primary and 0<=hit['frame']-episode['impact']['frame']<=1:candidates.append(episode)
            if len(candidates)==1:yield latch,hit,candidates[0]


def _timed_crossing(case,raw):
    frames=raw.get('frames',[])
    if not frames:return None
    rightward=case['goal'][0]+case['goal'][2]/2>=case['spawn'][0]
    for latch,hit,episode in _bell_episodes(case,raw):
        if not episode['airborne']or latch.get('open_seconds',0)<=0:continue
        gx,gy,gw,gh=latch['gate']
        if gh<=gw:continue # This assertion is specifically a vertical side door.
        crossings=[f for f in frames if f['x']-12<gx+gw and f['x']+12>gx and f['y']+18>gy and f['y']-18<gy+gh]
        if not crossings:continue
        first,last=crossings[0]['frame'],crossings[-1]['frame']
        before=[f for f in frames if f['frame']<=first and (f['x']+12<=gx if rightward else f['x']-12>=gx+gw)]
        clears=[f for f in frames if f['frame']>last and (f['x']-12>=gx+gw if rightward else f['x']+12<=gx)]
        if not before or not clears:continue
        clear=clears[0]['frame'];window=latch['open_seconds']*60
        if not(episode['origin']['frame']<=hit['frame']<=first and clear-hit['frame']<=window+1e-5):continue
        actual_open=all(any(b.get('id')==latch['id']and b.get('open')is True and b.get('open_count')==hit.get('count')
            for b in f.get('plains',{}).get('bells',[]))for f in crossings)
        if not actual_open:continue
        return dict(method=METHOD,kind='air_projectile_opens_actual_body_crossing_window',bellId=latch['id'],
            shotId=episode['origin']['shot_id'],shotFrame=episode['origin']['frame'],impactFrame=episode['impact']['frame'],
            hitFrame=hit['frame'],bodyDoorFrames=[f['frame']for f in crossings],bodyClearFrame=clear,bodySize=[24,36],
            actualGateOpenDuringEveryBodyOverlap=True,flightTicks=episode['impact']['frame']-episode['origin']['frame'],
            hitToWholeBodyClearTicks=clear-hit['frame'],timerTicks=window,rawTraceFiltered=False)
    return None


def _low_ray_recovery(case,raw):
    frames=raw.get('frames',[])
    if not case.get('platforms'):return None
    lip=case['platforms'][0];bottom=lip[1]+lip[3]
    for latch,hit,episode in _bell_episodes(case,raw):
        if not episode['airborne']:continue
        origin=episode['origin'];start=episode['frame'];previous=episode['previous']
        if origin['origin'][1]-18<=bottom or start['y']-18<=bottom:continue
        if previous.get('vy',0)<=0 or start.get('vy',0)>=0:continue
        airborne=[]
        for frame in frames:
            if frame['frame']<=origin['frame']:continue
            if frame.get('grounded'):break
            airborne.append(frame)
        rise=next((f for f in airborne if f['y']<start['y']-30),None)
        if rise is None:continue
        # A later propulsion cannot be credited to this bell-opening shot.
        assisted=any(any(a.get('type')in('shot','ground_jump','air_jump','wall_jump','anchor_jump')or a.get('state')in('wall_kick','hook_cast')
            for a in f.get('accepted',[]))for f in airborne if f['frame']<=rise['frame'])
        if assisted:continue
        return dict(method=METHOD,kind='actual_low_ray_bell_shot_reverses_fall_and_recovers',bellId=latch['id'],
            shotId=origin['shot_id'],shotFrame=origin['frame'],impactFrame=episode['impact']['frame'],hitFrame=hit['frame'],
            lipBottom=bottom,preShotBodyTop=origin['origin'][1]-18,postShotBodyTop=start['y']-18,
            preShotVy=previous['vy'],postShotVy=start['vy'],recoveryRiseFrame=rise['frame'],
            measuredRiseBeforeAnyLandingOrLaterPropulsion=start['y']-min(f['y']for f in airborne if f['frame']<=rise['frame']),
            rawTraceFiltered=False)
    return None


def correct(case,raw,check):
    """Keep every original reason unless its exact causal assertion is met."""
    family=case.get('family');reason=None;proof=None
    if family=='timed-cache'and'same_air_shot_gate_crossing_not_demonstrated'in check.get('reasons',[]):
        reason='same_air_shot_gate_crossing_not_demonstrated';proof=_timed_crossing(case,raw)
    elif family=='low-ray-recoil-return'and'low_ray_then_upward_recovery_missing'in check.get('reasons',[]):
        reason='low_ray_then_upward_recovery_missing';proof=_low_ray_recovery(case,raw)
    if proof is None:return check
    value=copy.deepcopy(check);value['reasons']=[r for r in value['reasons']if r!=reason]
    value.setdefault('causal',{}).setdefault('observerCorrections',[]).append(dict(originalReason=reason,proof=proof))
    value['ok']=not value['reasons']
    return value
