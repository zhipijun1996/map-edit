"""Guard final-port alignment and react to actual accepted ground recoil."""
from pcg.migration import core,godot_package
from .new_ideas_v1 import rows,label

def main():
 for row in rows():
  n=label(row);f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v3-cases.json',dict(cases=cs))
  for c in cs:
   c['generation_rule']['registration_source']='pcg/manual_review/ideas_author_v4.py';c['id']='approved-newideas-v5-'+n+'-'+c['route_spec']['id'];p=c['control_plan']
   if n=='orbit':
    i=next(i for i,v in enumerate(p)if v.get('jump_same_frame'));p[i].pop('jump_same_frame');p=p[:i+1]+[dict(op='jump',trigger=dict(after=0,state='accepted_shot_burst',timeout=30))]+p[i+1:]
   else:
    for v in p:
     if v.get('trigger',{}).get('state')=='chain_final':v['final_x']=c['exit_port'][0];v['height_threshold']=160
   c['control_plan']=p
  d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':main()
