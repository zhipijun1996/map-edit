"""Two same-world canonical witnesses; recovery is not a new Port/direction."""
from . import rules_v2 as rules
from .core_v2 import cases as core_cases
def candidate(route='normal'):
 if route not in ['normal','recovery']:raise ValueError('only normal/missedM recovery registered')
 c=rules.candidate(0)if route=='normal'else core_cases()[5]
 c.pop('counterexample_kind',None)
 c['id']='b30-blockn19-v2-i0-'+route
 c['fixture_kind']=route
 c['route_spec'].update(id='A-to-B'if route=='normal'else'A-to-B-missed-M-recovery',role='main'if route=='normal'else'recovery')
 c['map_specification']['objective']['required_canonical_witnesses']=['A-to-B','A-to-B-missed-M-recovery']
 c['map_specification']['relations']=[dict(from_port='A',to_port='B',role='main',route_id='A-to-B'),dict(from_port='A',to_port='B',role='recovery',route_id='A-to-B-missed-M-recovery')]
 c['map_specification']['return_conditions']='A-to-B normal plus exact missedM/realstair/airrecoil/Mretry witness required. FreshB-A, actualboundarycrossing, arbitraryfailure/recovery and wholeMap UNKNOWN.'
 return c
def purpose(c,r):
 q=rules.purpose(c,r)
 if c.get('fixture_kind')!='recovery':return q
 fs=r.get('frames',[]);events=q['causal']['actual_switches'];down=next((e for e in events if e['open']=='A'),None)
 step=next((f for f in fs if down and f['frame']>down['frame']and f.get('grounded')and f.get('support_id')=='Platform5'),None)
 middle=q['causal']['M_landing']
 recoil=next((f for f in fs if step and middle and step['frame']<f['frame']<middle['frame']and not f.get('grounded')and any(e.get('type')=='shot'for e in f.get('accepted',[]))),None)
 if not step or step.get('shot_charges',0)<1:q['reasons'].append('actual_missed_M_stair_ground_recovery_missing')
 if not recoil or recoil.get('shot_charges')!=0:q['reasons'].append('actual_recovery_airshot_consumption_missing')
 if not middle or middle.get('shot_charges',0)<1:q['reasons'].append('actual_recovery_M_recharge_missing')
 q['causal'].update(actual_recovery_step=({k:step.get(k)for k in ['frame','x','y','support_id','shot_charges']}if step else None),actual_recovery_recoil=({k:recoil.get(k)for k in ['frame','x','y','grounded','shot_charges']}if recoil else None))
 q['ok']=not q['reasons'];return q
