"""Repairs from v1 clean diagnostics only; keep failed v1 inputs immutable."""
import copy
from pcg.migration import core,godot_package
from .continue_revision063_v1 import rows,label
from .prepare_revision063_v1 import old_folder
from .prepare_review045_v1 import at
def main():
 for r in rows():
  n=label(r)
  if n not in ['hq07','lift']:continue
  f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];doc=core.read(f/'module.mapnote.json')
  for c in cs:
   if n=='lift' and c.get('explicit_exit_neighbor'):
    e=c['explicit_exit_neighbor'];e['index']=len(c['platforms']);c['platforms'].append(e['floor']);c['one_way_platform_indices'].append(e['index'])
   if n=='hq07':
    c['generation_rule']['registration_source']='pcg/manual_review/revision063_author_v2.py'
    if c['route_spec']['from_port']=='R':
     p=c['control_plan'];j=next(i for i,v in enumerate(p) if v.get('trigger',{}).get('state')=='revision_clear')
     c['control_plan']=p[:6]+at(784,334)+[dict(op='wait',enemy='charger',trigger=dict(after=1,state='r063_air_clear',timeout=1500))]+p[j+1:]
  core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True);print(n,'V2_PREPARED')
if __name__=='__main__':main()
