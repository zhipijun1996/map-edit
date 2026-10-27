"""Separate strong nominal demonstration from actual gentle-wall alternative."""
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common

def classify(case,raw,check,outcome,baseline=None):
 q=common.counter_classification(case,raw,check,outcome,baseline)
 if not q['invalidates_design']:return q
 # Never ignore scope, safety, missing world effects or missing body clearance.
 if set(check.get('reasons',[]))!={'first_contact_only_walk_not_recoil'}:return q
 causal=check.get('causal',{});hits=causal.get('wall_side_contacts',[]);switches=causal.get('switches',[])
 if not hits or not switches or causal.get('outside_count',0):return q
 hit=hits[0];event=switches[0];pre=causal.get('preimpact_velocity',[None,None])[0]
 clear=causal.get('close_clearances',[])
 real=(event.get('airborne')is True and event['frame']<hit['frame']
       and hit['contact']['normal'][0]>.7 and abs(hit['velocity'][0])<=1
       and isinstance(pre,(float,int))and pre<-1
       and causal.get('first_pocket_frame',-1)>hit['frame']
       and clear and min(c['axis_clearance']for c in clear)>=6)
 if real:
  q.update(invalidates_design=False,reason='Actual gentler new-wall collision absorbs leftward velocity, then supported pocket/renewal reaches same reward; strong400px/s threshold is nominal demonstration only',gentle_wall_witness=dict(preimpact_vx=pre,contact=hit,switch=event,first_pocket_frame=causal['first_pocket_frame']),nominal_strong_collision_unchanged=True)
 return q
