"""Prospective input-only fixes from real diagnostic traces. No world edits."""
import copy,sys
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision053_v1 import rows,label
from .prepare_review045_v1 import at,axis
from .prepare_review_refresh_v1 import kill

def apply(row):
 n=label(row);f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v9-cases.json',dict(cases=cs))
 for c in cs:
  p=c['control_plan'];a,z=c['route_spec']['from_port'],c['route_spec']['to_port']
  if n in ['51','52']:
   if a=='exit':
    i=next(i for i,v in enumerate(p)if v['op']=='grapple'and v.get('aim_target')==[-35,-350]);p.insert(i+1,axis(-1))
    last=max(i for i,v in enumerate(p)if v['op']=='shoot');p[last]['direction']=[.9,.4358898944]
  elif n=='50':
   if a=='C'and z=='exit':
    ca=next(x for x in cs if x['route_spec']['from_port']=='C'and x['route_spec']['to_port']=='entry')
    out=next(x for x in cs if x['route_spec']['from_port']=='entry'and x['route_spec']['to_port']=='exit')
    tail=copy.deepcopy(out['control_plan'])
    for v in tail:
     if 'hook_count'in v:v['hook_count']+=3
    p=copy.deepcopy(ca['control_plan'])+tail;c['expected_hook_sequence']=ca['expected_hook_sequence']+out['expected_hook_sequence'];c['route_spec']['via_ports']=['entry']
  elif n=='220':
   if a=='B'and z=='A':
    for v in p:
     if v.get('target_x')==480:v['target_x']=500
     g=v.get('trigger',{}).get('migration_goal')
     if g and g[0]==475:g[0]=495
  elif n=='196':
   c['generation_rule']['registration_source']='pcg/manual_review/revision053_author_v7.py'
   if z=='entry':
    i=next(i for i,v in enumerate(p)if v.get('climb_target')==-240)
    assert p[i-1]['op']=='jump'and p[i-2]['op']=='axis'
    p[i-2]=axis(0)
    p[i:i]=[dict(op='wait',observed_y=dict(value=-90,direction='lte'),trigger=dict(after=1,state='observed_height',timeout=120)),axis(1)]
  elif n=='three':c['generation_rule']['registration_source']='pcg/manual_review/revision053_three_author_v4.py'
  if n in ['three','lift']:
   for v in p:
    if v.get('aim_cell',{}).get('kind')=='bell':v.pop('aim_cell');v['direction']=[0,-1]
  c['control_plan']=p;c['id']+='-r9'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:apply(r)
