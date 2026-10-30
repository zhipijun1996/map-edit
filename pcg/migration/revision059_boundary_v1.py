"""059 full-body bottom ingress; exact approved identity and explicit opt-in."""
import copy
from . import core

def entry(case,doc,physics):
 s=case.get('approved_implementation',{})
 if s.get('reviewId')!='idea-interface-s02-001' or s.get('designVersion')!='sha256:04c2e467b022ced8d104b511957371680557b9293ad29ee56afb0bd4d35e31fe' or not case.get('migration_boundary_plans',{}).get('bottom_full_body_alignment'):return None
 port=next(p for p in doc['generationContract']['ports']if p['id']==case['route_spec']['from_port'])
 if port['id']!='B':return None
 v=physics.fresh(case,'continuous-entry');n=physics.exterior_floor(v,port);x,y=case['spawn'];v['spawn']=[port['position'][0],n['floor'][1]-18];v['control_plan']=[dict(op='axis',value=0,cancel_settle=True,trigger=dict(after=0)),dict(op='jump',trigger=dict(after=1)),dict(op='wait',observed_y=dict(direction='lte',value=620),trigger=dict(after=1,state='observed_height',timeout=180)),dict(op='settle',target_x=x,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='jump_release',trigger=dict(after=24)),dict(op='wait',trigger=dict(after=24,state='grounded',migration_goal=[x-4,y-3,8,6],timeout=300))];v['goal']=[x-9,y-5,18,10];v['max_frames']=360;v['migration_probe']=dict(kind='continuous_entry',portId=port['id'],direction='ingress',boundary=port['position'],normal=port['normal'],neighbor=n,body=[24,36],noIntermediateReset=True,originalRouteId=case['route_spec']['id'],scope='Aligned original jump through complete 64px bottom aperture before lateral docking');v['module_sha256']=physics.module_hash(v);return v
