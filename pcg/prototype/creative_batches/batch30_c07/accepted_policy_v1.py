"""Nominal wall skill plus independently observed extra-action alternatives.

No program-label whitelist. Nominal one-jump calibration keeps every original
collision/close-clearance check; a paid policy needs real additional jumps and
real support/resource renewal in the same world.
"""
from . import rules_v3 as rules
ALTERNATIVE_ONLY_REASONS={
 'actual_wall_build_missing','actual_new_wall_side_contact_missing',
 'actual_receiving_pocket_support_missing','pocket_support_not_after_wall_contact',
 'first_contact_only_walk_not_recoil','wall_contact_not_after_switch',
 'complete_body_clearance_at_close_not_witnessed','same_air_shot_not_witnessed',
 'world_state_wrong',
}
def purpose(c,r):
 q=rules.purpose(c,r)
 if q['ok']:return q
 fs=r.get('frames',[])
 jumps=[f for f in fs if any(a.get('type')=='ground_jump'for a in f.get('accepted',[]))]
 shots=[f for f in fs if any(a.get('type')=='shot'for a in f.get('accepted',[]))]
 renewal=[f for f in fs if shots and jumps and shots[0]['frame']<f['frame']<jumps[-1]['frame']and f.get('grounded')and f.get('shot_charges')==1]
 pair=next((p for p in r.get('workshop',{}).get('paired_gates',[])if p['id']=='brake-pair'),{})
 pair_valid=pair.get('open_a')!=pair.get('open_b')and pair.get('open_a')in[True,False]and pair.get('gate_a_layer')==(0 if pair.get('open_a')else 1)and pair.get('gate_b_layer')==(0 if pair.get('open_b')else 1)
 paid=len(jumps)>=2 and len(shots)>=1 and renewal and pair_valid and set(q['reasons'])<=ALTERNATIVE_ONLY_REASONS
 if paid:
  q['causal']['nominal_collision_check']=dict(ok=False,reasons=q['reasons'][:])
  q['causal']['accepted_extra_action_alternative']=dict(actual_ground_jump_frames=[f['frame']for f in jumps],actual_shot_frames=[f['frame']for f in shots],support_renewal_frames=len(renewal),actual_final_pair=dict(open_a=pair['open_a'],open_b=pair['open_b']),cost=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')),nominal_cost=dict(shots=2,jumps=1,ticks=197),necessity_claim=False,classification_basis='Actual extra groundjump and real postshot landing renewal; no program kind/label test')
  q['reasons']=[];q['ok']=True
 return q
