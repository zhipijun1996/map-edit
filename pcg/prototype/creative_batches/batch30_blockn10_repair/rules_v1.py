"""One explicit original return-access extension, preserved normal physical plan."""
from pathlib import Path
from pcg.prototype.creative_batches.batch30_blockn10 import rules_v2 as source
from pcg.prototype.workshop.rules import cmd,wait_x
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=source.RECIPES;RUNNER_SCRIPT=HERE/'runner_v1.gd';NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(source.__file__),*source.SOURCE_DEPENDENCIES,*[HERE/n for n in ['protocol-v1.json','observe_v1.gd','runner_v1.gd','main_v1.gd','main_v1.tscn']]]
rest=source.rest;over=source.over
def candidate(control=0,route='normal'):
 if route not in ['normal','retry']:raise ValueError('outsideN10repairtwoA-Bcanonicalroutes')
 c=source.candidate(control);c['latches'][0]['return_access']=[1088,672]
 c['id']=c['id'].replace('blockn10-v2','blockn10-repair-v1')+'-'+route
 if route=='retry':
  p=c['control_plan'];j=max(i for i,v in enumerate(p)if v['op']=='jump');assert p[j-1]['op']=='axis'and p[j-1]['value']==-1
  late=[cmd('axis',value=1),wait_x(1108),*rest(),cmd('wait',140),cmd('jump'),cmd('shoot',11,aim_cell=dict(kind='bell',id='far')),cmd('jump_release'),cmd('axis',value=-1),source.old.ground(),cmd('axis',value=0),cmd('wait',8),cmd('axis',value=-1),wait_x(1080,-1),*rest()]
  c['control_plan']=p[:j-1]+late+p[j-1:];c['max_frames']=2400
 c['route_spec']['id']='A-to-B'if route=='normal'else'A-to-B-delayed-Near-retry';c['route_spec']['role']='main'
 c['rule_parameters'].update(canonical_route=route,near_return_access=[1088,672],retry_hold_x=1108,retry_delay=140)
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['generation_rule']=dict(id='batch30/N10/return-access-repair',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'],prior_failed_cycle=dict(cases=63,rules=2,held=0),new_cycle=dict(max_rules=1,max_probe_cases=17))
 c['native_scene']='res://prototype/creative_batches/batch30_blockn10_repair/main_v1.tscn';c['native_block_scene']=str(NATIVE_SCENE.relative_to(HERE.parents[3]))
 s=c['map_specification'];s['id']='batch30/N10/return-access-repair/explicit-lower-exit';s['objective'].update(physical_layout_sha256=c['layout_uid'],required_canonical_witnesses=['A-to-B','A-to-B-delayed-Near-retry'],restore_original_receiver=True)
 s['return_conditions']='OnlyA->B; independentB->AUNKNOWN. SameworldNearclosed/reactivated/Mrenewed/A->Bcanonicalrequiredforrecovery. Genericfloorretry/seam/fullMapUNKNOWN'
 return c
def core_purpose(c,r):
 q=source.purpose(c,r);age=q['causal'].get('actual_current_near_window_age_ticks')
 if age is not None and age>round(c['latches'][0]['open_seconds']*60)+1e-4:q['reasons'].append('actual_far_hit_only_after_nominal_timer_expiry_antipinch_hold')
 q['ok']=not q['reasons'];return q
def purpose(c,r):
 q=core_purpose(c,r)
 if c['route_spec']['id']!='A-to-B-delayed-Near-retry':return q
 fs=r.get('frames',[]);hits=q['causal']['actual_hits'];near=[e['frame']for e in hits if e['id']=='near'];far=[e['frame']for e in hits if e['id']=='far'];last=near[-1]if near else None;fhit=far[0]if far else None
 closed=[f for f in fs if len(near)>=2 and near[0]+20<f['frame']<near[1]and over(f,c['platforms'][1])and abs(f['x']-1108)<6 and any(v['id']=='near'and not v['open']and v['bell_layer']==8 and v['gate_layer']==1 and not v['gate_disabled']and any(a['layer']==8 for a in v.get('access',[]))for v in f.get('n10',[]))]
 impacts=[e for e in r.get('plains',{}).get('events',[])if e['type']=='projectile_impact'and len(near)>=2 and abs(e['frame']-near[1])<=1 and 1071<=e['point'][0]<=1105 and 652<=e['point'][1]<=692]
 recatch=[f for f in fs if len(near)>=2 and fhit is not None and near[1]<f['frame']<fhit and over(f,c['platforms'][1])and f.get('shot_charges')==1]
 if len(near)<2 or not far:q['reasons'].append('actual_closed_near_reopen_before_far_missing')
 if not closed:q['reasons'].append('actual_M_stable_outside_antipinch_Near_closed_access8_missing')
 if not impacts:q['reasons'].append('actual_restore_receiver_projectile_impact_missing')
 if not recatch:q['reasons'].append('actual_M_recatch_renewal_after_restore_missing')
 q['causal'].update(actual_closed_M_frames=[f['frame']for f in closed],actual_restore_receiver_impacts=impacts,actual_M_recatch_frames=[f['frame']for f in recatch],actual_latest_near_to_far_ticks=fhit-last if fhit is not None and last is not None else None,no_scene_reconstruction=True)
 q['ok']=not q['reasons'];return q
