"""Causal checks layered on original finite-sample factory quality policy."""
import copy,json,random
from ..plains.evaluation import observed
from ..factory.core.quality import counts,gate,POLICY

def purpose(c,r):
    frames=r.get('frames',[]);behavior=observed(c,r);reasons=[];causal={}
    if not r.get('ok'):reasons.append(r.get('reason','not_stable'))
    if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):reasons.append('player_harm')
    if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):reasons.append('forbidden_ability')
    family=c['family'];route=c.get('route_spec',{}).get('id','main')
    if route not in ['return','recovery','rejoin'] and r.get('shots',0)<1:reasons.append('no_recoil')
    expected=c.get('expected_reward',0 if route in ['low','return','recovery','rejoin']or not c['reward_sites']else c['reward_sites'][0]['amount'])
    if r.get('workshop',{}).get('coins',0)<expected:reasons.append('reward_not_actually_claimed')
    if family=='chase-landing':
        supported=[f for f in frames if f.get('support_id')=='chase-carrier']
        neutral=[f for f in supported if abs(f['axis'])<.01]
        toggles=[e for e in r.get('workshop',{}).get('events',[])if e['type']=='carrier_toggle']
        displacement=max((f['x']for f in neutral),default=0)-min((f['x']for f in neutral),default=0)
        causal.update(supported_frames=len(supported),neutral_supported_frames=len(neutral),neutral_carried_dx=displacement,toggles=toggles)
        if len(supported)<12 or displacement<12:reasons.append('real_carriage_not_demonstrated')
        if len(toggles)<2 or not toggles[0]['running']or toggles[1]['running']or not all(e['airborne']for e in toggles[:2]):reasons.append('airborne_start_pause_not_demonstrated')
    if family=='air-refund':
        if behavior['refunds']<1 or not behavior['continuous_two_air_shots']:reasons.append('no_actual_air_hit_refund_chain')
    if family=='thorn-slot':
        # Rectangle of every segment's swept 24x36 body, not a center-point
        # clearance check. Conservative for any diagonal interpolation.
        gaps=[];bad=[]
        for thorn in c['thorns']:
            p=c['platforms'][thorn['platform_index']]
            rect=[p[0]+thorn['start_offset'],p[1]+p[3]if thorn['face']=='bottom'else p[1]-thorn['depth'],thorn['length'],thorn['depth']]
            for a,b in zip(frames,frames[1:]):
                x0=min(a['x'],b['x'])-12;x1=max(a['x'],b['x'])+12
                if x1<=rect[0]or x0>=rect[0]+rect[2]:continue
                top=min(a['y'],b['y'])-18;bottom=max(a['y'],b['y'])+18
                gap=top-(rect[1]+rect[3])if thorn['face']=='bottom'else rect[1]-bottom
                gaps.append(gap)
                if gap<=0:bad.append(b['frame'])
        causal.update(body_size=[24,36],minimum_sampled_swept_thorn_clearance=min(gaps,default=None),intersections=bad)
        if bad:reasons.append('body_sweep_intersects_thorns')
    if family=='timed-cache':
        events=r.get('plains',{}).get('events',[]);hits=[e for e in events if e['type']=='bell_open']
        shots=[f for f in frames if any(e['type']=='shot'for e in f.get('accepted',[]))]
        gx,gy,gw,gh=c['latches'][0]['gate']
        crossing=[f['frame']for f in frames if f['x']-12<gx+gw and f['x']+12>gx and f['y']+18>gy and f['y']-18<gy+gh]
        complete=next((f['frame']for f in frames if f['x']-12>=gx+gw),None)
        hit=hits[0]['frame']if hits else None;shot=shots[0]['frame']if shots else None
        causal.update(shot_frame=shot,hit_frame=hit,body_door_frames=crossing,body_clear_frame=complete,
            projectile_flight_ticks=hit-shot if hit is not None and shot is not None else None,
            hit_to_body_clear_ticks=complete-hit if hit is not None and complete is not None else None,
            timer_ticks=c['latches'][0]['open_seconds']*60,anti_pinch='original ShotLatch.grow(24), unchanged')
        if not hits or not shots or shots[0]['grounded']or complete is None:reasons.append('same_air_shot_gate_crossing_not_demonstrated')
    if family=='brake-under-ledge':
        shots=[f for f in frames if any(e['type']=='shot'for e in f.get('accepted',[]))]
        lip=c['platforms'][0];causal['shot_below_lip']=bool(shots and shots[0]['y']-18>lip[1]+lip[3])
        if not causal['shot_below_lip']:reasons.append('braking_not_below_overhang')
    return dict(ok=not reasons,reasons=reasons,behavior=behavior,causal=causal)

def instantiate(c,seed,level,trial):
    rng=random.Random(seed+trial*104729+{'clean':0,'mild':1000003,'moderate':2000006}[level]);v=copy.deepcopy(c)
    v['id']+=f'-{level}-{trial}'
    if level!='clean':v['noise']=dict(seed=rng.randrange(2**30),timing_frames=1 if level=='mild'else 3,aim_degrees=2 if level=='mild'else 6)
    for e in v.get('enemies',[]):e['initial_idle_cooldown']=rng.uniform(0,.6)
    # Controlled platforms start at their authored parked dock; phase of their
    # later movement is affected by the independently disturbed real hit time.
    return v

def evaluate(engine,cases,seed,trials,stage):
    entries=[]
    for base in cases:
        rows=[];witness=None
        dynamic=bool(base.get('moving_platforms')or base.get('enemies')or base.get('saws'))
        expanded=[];labels={}
        for level in ['clean','mild','moderate']:
            for i in range(trials if level!='clean'or dynamic else 1):
                v=instantiate(base,seed,level,i);expanded.append(v);labels[v['id']]=(level,i)
        for c,r,e in engine.run(expanded,stage):
            level,trial=labels[c['id']];p=purpose(c,r)
            rows.append(dict(level=level,trial=trial,purpose=p,safe_stable=bool(r['ok']),evidence=e))
            if level=='clean' and p['ok']and witness is None:
                witness=dict(case=c,result=r,evidence=e)
        stats={l:counts([r for r in rows if r['level']==l])for l in ['clean','mild','moderate']}
        quality=gate(stats,False,dynamic)
        entry=dict(case=base,rows=rows,stats=stats,quality_gate=quality,witness=witness)
        entries.append(entry)
        (engine.out/'evaluations.json').write_text(json.dumps(entries))
        print(json.dumps(dict(id=base['id'],rates={k:v['rate']for k,v in stats.items()},quality=quality['status'],failures=sorted(set(s for r in rows for s in r['purpose']['reasons'])))),flush=True)
    return entries

if __name__=='__main__':
    import argparse
    from .engine import ROOT,WorkshopEngine
    from .rules import candidates,FAMILIES
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--families',nargs='+',choices=FAMILIES);a=p.parse_args()
    engine=WorkshopEngine(ROOT/'results'/a.name)
    evaluate(engine,[c for f in a.families or FAMILIES for v in range(2)for c in candidates(f,v)],26102501,12,'calibration-noise')
