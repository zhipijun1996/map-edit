"""Original classifier plus an observed extra-jump staged internal A detour."""
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import counter_classification as original,external_outcome,checked_purpose
from pcg.prototype.creative_batches.batch30_blockn12 import counter_policy_v1 as stable_source
stable_goal=stable_source.stable_goal
SOURCE_DEPENDENCIES=[Path(stable_source.__file__)]
CAUSES={'actual_top_open_side_closed_exchange_missing','complete_body_upward_crossing_actual_open_top_missing','first_post_airshot_landing_not_real_fixed_upper_refill'}
def classify(case,raw,check,outcome,baseline=None):
 result=original(case,raw,check,outcome,baseline)
 if not(result['invalidates_design']and case.get('counterexample_kind')and case['route_spec']['from_port']=='A'and case['route_spec']['to_port']=='C'and set(check.get('reasons',[]))==CAUSES and outcome.get('ok')and baseline and baseline.get('ok')and checked_purpose(rules,case,baseline)['ok']and external_outcome(case,baseline)['ok']):return result
 ca=stable_goal(case,raw);ba=stable_goal(case,baseline)
 if not(ca and ba):return result
 safe=raw.get('hp')==5 and not raw.get('returns')and not raw.get('plains',{}).get('player_damage')and not any(raw.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])
 resources=all(ca.get(k,0)>=ba.get(k,0)for k in ['shot_charges','energy','hp'])and ca.get('jumps_used',1)<=ba.get('jumps_used',0)and ca.get('shot_cooldown',1)<=ba.get('shot_cooldown',0)
 not_cheaper=raw.get('shots',0)>=baseline.get('shots',0)and raw.get('jumps',0)>baseline.get('jumps',0)and ca['frame']>=ba['frame']
 stages=[];after=-1
 for support in ['Platform1','Platform2','Platform3','Platform4','Platform5']:
  f=next((f for f in raw.get('frames',[])if f['frame']>after and f.get('grounded')and f.get('support_id')==support and f.get('shot_charges')==1 and f.get('jumps_used')==0 and f.get('shot_cooldown',1)<=1e-9),None)
  if not f:return result
  after=f['frame'];stages.append({k:f.get(k)for k in ['frame','x','y','support_id','shot_charges','energy','jumps_used','shot_cooldown']})
 if not(safe and resources and not_cheaper):return result
 result.update(invalidates_design=False,reason='Actualwithin-ownedM/B/fixedupper/relay/Cdetourpaysanextrarealjumpandnoearlierstablearrival; nominalsame-shotupwardexchange remainsstrictdemonstration.',scope='internal_paid_staged_alternative',accepted_internal_counter_witness=True,canonical_route_certification=False,alternative_robustness='UNKNOWN',nominal_body_purpose_unchanged=True,nominal_vertical_purpose_unchanged=True,actual_staged_resource_renewals=stages,actual_original_stable_goal=dict(required_frames=max(6,int(case.get('settle_frames',6))),nominal=ba['frame'],alternative=ca['frame'],delta=ca['frame']-ba['frame']),body_ownership='Originalsourcebody/sweepcheckhasnoownershipreason; noreservationgrowth.',world_state='PaidroutepreservesAclosed/Bopen; exactrequesthasnoextramandatoryfinalpaircondition. Noarbitraryworld-staterequestqualification.')
 return result
