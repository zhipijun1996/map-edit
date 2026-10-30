"""Approved-design outcome/causal checks, not historical-geometry assertions."""
from pathlib import Path
from pcg.migration import core
RUNNER_SCRIPT=Path(__file__).parent/'runtime/first30_runner_v2.gd'
SOURCE_DEPENDENCIES=[Path(__file__),RUNNER_SCRIPT,Path(__file__).parent/'runtime/retractable_gears_v1.gd',
    Path(__file__).parent/'first30_content_v2.py']


def purpose(case,raw):
    reasons=[];spec=case['approved_first30'];n=spec['reviewId'];frames=raw.get('frames',[])
    if not raw.get('ok'):reasons.append(raw.get('reason','not_stable'))
    if raw.get('plan_error'):reasons.append(raw['plan_error'])
    player_commits=[e for e in raw.get('damage_commits',[])if str(e.get('target',e.get('target_id','')))in('player','player_health')]
    if raw.get('hp')!=5 or raw.get('plains',{}).get('player_damage') or player_commits:reasons.append('actual_player_harm')
    if raw.get('returns'):reasons.append('world_reset')
    if any(raw.get(k,0)for k in ('air_jumps','wall_jumps','grapples')):reasons.append('forbidden_ability')
    claims=[e for e in raw.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')]
    for identifier in case.get('required_rewards',[]):
        expected=next(v for v in case['reward_sites']if v['id']==identifier)
        actual=[e for e in claims if e['id']==identifier and e['amount']==expected['amount']]
        if len(actual)!=1:reasons.append('actual_reward_transaction_missing:'+identifier)
    if raw.get('workshop',{}).get('coins',0)<case.get('expected_reward',0):reasons.append('actual_wallet_amount_missing')
    b=spec['rectangle'];outside=[]
    for f in frames:
        if f['x']-12<b['x']-.05 or f['x']+12>b['x']+b['w']+.05 or f['y']-18<b['y']-.05 or f['y']+18>b['y']+b['h']+.05:
            air=next((p for p in case.get('air_port_contracts',[])if p['id']==case['route_spec']['to_port']and p['permission']=='OUTPUT'),None)
            if not(air and abs(f['x']-air['position'][0])+12<=32 and f['y']-18>=b['y'] and f['y']<=air['position'][1]+128 and f['vy']>0):outside.append(f['frame'])
    if outside:reasons.append('actual_body_outside_approved_rectangle')
    switches=[e for pair in raw.get('workshop',{}).get('paired_gates',[])for e in pair.get('events',[])if e.get('type')=='pair_switch']
    if n in ('07','25','30') and not switches:reasons.append('actual_complementary_switch_missing')
    if n=='25' and len(switches)<2:reasons.append('actual_return_side_gate_switch_missing')
    if n=='30':
        support=[f for f in frames if f.get('grounded') and str(f.get('support_id','')).startswith('PairGateB') and f.get('shot_charges')==1]
        if not support:reasons.append('actual_swapped_bridge_refill_missing')
    if n=='06':
        groups=raw.get('workshop',{}).get('retractable_groups',[])
        if len(groups)!=1:reasons.append('actual_retractable_group_missing')
        for g in groups:
            if len(g['band_enabled'])!=2 or any(v!=g['extended']for v in g['band_enabled']):reasons.append('gear_group_state_not_synchronous')
        if case['route_spec']['to_port']=='C' and not any(g['toggle_count']>0 and not g['extended']for g in groups):reasons.append('actual_gears_retraction_missing')
    if n=='10':
        carries=[f for f in frames if f.get('support_id')=='catch-deck']
        neutral=[f for f in carries if abs(f.get('axis',0))<.01]
        if len(carries)<6 or max((f['x']for f in neutral),default=0)-min((f['x']for f in neutral),default=0)<12:reasons.append('actual_carrier_interception_missing')
        if not any(e.get('type')=='carrier_toggle'and e.get('airborne')for e in raw.get('workshop',{}).get('events',[])):reasons.append('actual_airborne_carrier_control_missing')
    if n=='17' and not any(f.get('support_id')=='return-deck' for f in frames):reasons.append('actual_original_return_carrier_missing')
    if n in ('12','28') and case['route_spec'].get('require_bell'):
        if not any(e.get('type')=='bell_open'for e in raw.get('plains',{}).get('events',[])):reasons.append('actual_gate_open_missing')
    demonstration_missing=[r for r in reasons if r in {
        'actual_complementary_switch_missing','actual_return_side_gate_switch_missing',
        'actual_swapped_bridge_refill_missing','actual_gears_retraction_missing',
        'actual_carrier_interception_missing','actual_airborne_carrier_control_missing',
        'actual_original_return_carrier_missing','actual_gate_open_missing'}]
    # An omission counter may expose a legitimate additional route. Preserve
    # nominal demonstrations separately; never reject an alternative for
    # merely omitting the planned action. Safety, bounds and outcomes stay strict.
    if case.get('migration_counter'):reasons=[r for r in reasons if r not in demonstration_missing]
    if case.get('fixture_kind')=='same-world-A-C-A':
        c_visits=[f for f in frames if f.get('grounded') and abs(f['x']-1128)<=10 and abs(f['y']-676)<=2]
        after=min((f['frame']for f in c_visits),default=10**9)
        later=[f for f in frames if f['frame']>after]
        if len(c_visits)<6:reasons.append('actual_C_visit_missing')
        for name,y in [('return-deck',592),('Platform1',420),('Platform4',632)]:
            if sum(f.get('grounded') and f.get('support_id')==name and abs(f['y']-y)<=2 and f.get('shot_charges')==1 for f in later)<6:reasons.append('earned_return_support_missing:'+name)
        if len({f.get('actor_epoch')for f in frames})!=1 or any(b['module_clock']<=a['module_clock']for a,b in zip(frames,frames[1:])):reasons.append('same_world_continuity_broken')
    return dict(ok=not reasons,reasons=sorted(set(reasons)),
        causal=dict(approvedDesignVersion=spec['designVersion'],outsideFrames=outside,claims=claims,pairSwitches=switches,nominalDemonstrationMissing=demonstration_missing),
        behavior={k:raw.get(k)for k in ('shots','jumps','ticks')})
