"""Observe actual M departures, allowing a paid recoil hop and return onto M."""
from pathlib import Path
from . import rules_v2 as old
RECIPES=old.RECIPES;RUNNER_SCRIPT=old.RUNNER_SCRIPT;NATIVE_SCENE=old.NATIVE_SCENE
candidate=old.candidate
SOURCE_DEPENDENCIES=[Path(old.__file__),*old.SOURCE_DEPENDENCIES,Path(__file__)]

def purpose(c,r):
 q=old.purpose(c,r);legacy=dict(ok=q['ok'],reasons=q['reasons'][:],first_branch_shot=q['causal']['first_branch_shot'],first_branch_landing=q['causal']['first_branch_landing'])
 fs=r.get('frames',[]);target=c['route_spec']['to_port'];rect=c['latches'][0]['gate'if target=='B'else'paired_gate'];stages=[]
 for i,f in enumerate(fs[:-1]):
  if not old.over(f,c['platforms'][1])or not f.get('shot_charges')==1 or fs[i+1].get('grounded'):continue
  landed=next((g for g in fs[i+1:]if g.get('grounded')),None)
  if not landed:continue
  state=next((p for p in landed.get('workshop',{}).get('paired_gates',[])if p.get('id')=='wing-pair'),{})
  key='a'if target=='B'else'b'
  supported=bool(old.over(landed,rect)and state.get('gate_'+key+'_layer')==1 and state.get('gate_'+key+'_disabled')is False and landed.get('shot_charges')==1)
  stages.append(dict(last_M_frame=f['frame'],departure_frame=fs[i+1]['frame'],first_landing={k:landed.get(k)for k in ['frame','x','y','support_id','shot_charges']},actual_pair_state=state,corresponding_closed_bridge_supported=supported))
 valid=next((v for v in stages if v['corresponding_closed_bridge_supported']),None)
 # Only replace the ambiguous first-shot segmentation. All original real goal,
 # body ownership, HP/caps/no-reset and actual right-exchange checks remain.
 if valid:q['reasons']=[v for v in q['reasons']if v not in ['first_branch_landing_not_corresponding_bridge','actual_corresponding_bridge_collision_state_missing','actual_bridge_resource_renewal_missing']]
 q['causal'].update(legacy_first_shot_segmentation=legacy,actual_M_departure_stages=stages,actual_corresponding_bridge_stage=valid,paid_recoil_return_to_M_allowed=True)
 q['ok']=not q['reasons'];return q
