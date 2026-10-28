"""Outcome and approved-footprint observation using original runtime consumers."""
from pathlib import Path

def purpose(case,raw):
    s=case['approved_implementation'];n=s['reviewId'];reasons=[];frames=raw.get('frames',[])
    if raw.get('rejected') or (not frames and str(raw.get('reason','')).startswith('rejected_')):
        return dict(ok=False,reasons=[raw.get('reason','rejected_before_physics')],causal=dict(physicsFrames=len(frames),actualPlayerHarm=False),behavior={k:raw.get(k)for k in('shots','jumps','ticks')})
    if not raw.get('ok'):reasons.append(raw.get('reason','not_stable'))
    if raw.get('plan_error'):reasons.append(raw['plan_error'])
    if raw.get('hp')!=5 or raw.get('plains',{}).get('player_damage'):reasons.append('actual_player_harm')
    if raw.get('returns'):reasons.append('world_reset')
    for k,cap in [('air_jumps','double_jump'),('wall_jumps','wall_jump'),('grapples','grapple')]:
        if raw.get(k,0)and cap not in case['capabilities']:reasons.append('forbidden_'+k)
    b=s['rectangle'];outside=[f['frame']for f in frames if f['x']-12<b['x']-.05 or f['x']+12>b['x']+b['w']+.05 or f['y']-18<b['y']-.05 or f['y']+18>b['y']+b['h']+.05]
    if outside:reasons.append('actual_body_outside_approved_rectangle')
    claimed={e.get('id')for e in raw.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')}
    if not set(case.get('required_rewards',[]))<=claimed:reasons.append('actual_reward_missing')
    if raw.get('workshop',{}).get('coins',0)<case.get('expected_reward',0):reasons.append('actual_wallet_amount_missing')
    contacts=[c['source_id']for c in raw.get('original_hook_contacts',[])]
    if n=='39'and not case.get('migration_counter')and contacts!=['relay_a','relay_b']:reasons.append('actual_original_hook_sequence_missing')
    return dict(ok=not reasons,reasons=sorted(set(reasons)),causal=dict(approvedDesignVersion=s['designVersion'],outsideFrames=outside,actualHookContacts=contacts),behavior={k:raw.get(k)for k in('shots','jumps','ticks')})
