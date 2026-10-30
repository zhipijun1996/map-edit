"""Complete driver predicates, real same-port format, and safe descent approach."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from .new_ideas_v1 import rows,label
from .prepare_review045_v1 import at,end

def main():
 for row in rows():
  if label(row)=='orbit':continue
  f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v1-cases.json',dict(cases=cs))
  for c in cs:
   c['generation_rule']['registration_source']='pcg/manual_review/ideas_author_v2.py';c['id']=c['id'].replace('newideas-v1','newideas-v3')
   if c['route_spec']['from_port']=='B':c['control_plan']=[dict(op='settle',target_x=24,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='drop_through',trigger=dict(after=1))]+at(24,c['exit_port'][1])+end(*c['exit_port'])
   for v in c['control_plan']:
    if v.get('trigger',{}).get('state')=='shot_ready_above':v['trigger']['state']='chain_final'
    if v.get('trigger',{}).get('state')=='chain_shot':v['aim_cell']['body_offset']=[0,12]
  doc=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':main()
