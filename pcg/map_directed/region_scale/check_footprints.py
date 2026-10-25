"""Extend the existing source audit with reserved dynamic/door footprints."""
import argparse,json
from pathlib import Path
from ..direct_join.audit import audit
from ..run import write

def enclosed(rect,w,h):
 x,y,a,b=rect
 return x>=0 and y>=0 and x+a<=w and y+b<=h

def check(c):
 result=audit(c);carriers=doors=0
 for m in c['modules']:
  w,h=m['spec']['space']['core_bounds'][2:]
  shared={p.get('shared_landing_index')for p in m['ports'].values()if p['kind']=='vertical'}
  for i,rect in enumerate(m['case']['platforms']):
   if not enclosed(rect,w,h) and i not in shared:raise ValueError('undeclared_solid_reservation_intrusion/'+m['id']+'/'+str(i))
  for f in m['case']['moving_platforms']:
   x,y=f['start'];a,b=f['finish'];u,v=f['size']
   env=[min(x,a)-u/2,min(y,b)-v/2,abs(x-a)+u,abs(y-b)+v]
   if not enclosed(env,w,h):raise ValueError('undeclared_carrier_envelope_intrusion/'+m['id']+'/'+f['platform_id'])
   carriers+=1
  for latch in m['case']['latches']:
   if not enclosed(latch['gate'],w,h):raise ValueError('undeclared_gate_intrusion/'+m['id']+'/'+latch['id'])
   doors+=1
 result.update(reserved_carrier_envelopes_checked=carriers,reserved_gate_bodies_checked=doors,
  static_solids_outside_reservation='declared shared landings only',actor_action_envelopes='UNKNOWN except finite whole-world witnesses',
  scope='Exact source/static/dynamic/door footprints; does not infer arbitrary-state action clearance or fun')
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('compiled');p.add_argument('out');a=p.parse_args();write(Path(a.out),check(json.loads(Path(a.compiled).read_text())))
