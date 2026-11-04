if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core
from .continue_revision060_v1 import rows,label
from .revise_revision060_v2 import save
from .prepare_revision060_v1 import wait
from .prepare_review045_v1 import at,axis
from .prepare_ideas_v1 import settle
from pcg.prototype.workshop.rules import cmd

def main():
 for r in rows():
  n=label(r)
  if n not in ['hq01','hq03','hq07','s12']:continue
  cs=core.read(core.REPO/r['outputDirectory']/'cases.json')['cases']
  for c in cs:
   c['generation_rule']['registration_source']='pcg/manual_review/revision060_author_v6.py';a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan']
   if n=='hq01':
    if z=='R':
     k=next(i for i,v in enumerate(p)if v.get('target_x')==580);p[k+2].update(adaptive_q_hold=True,ordinary_hold=12);p[k+3].update(adaptive_right_shot=True);p[k+3]['trigger'].update(state='r060_right_live_aim',timeout=180)
    elif z=='T':
     k=next(i for i,v in enumerate(p)if v.get('target_x')==192 and v['op']=='settle');p[k+2].update(adaptive_q_hold=True,ordinary_hold=24)
    else:
     for v in p:
      if v.get('route_mode')=='far'and v.get('op')=='jump_release':v.update(adaptive_q_hold=True,ordinary_hold=24)
   if n=='s12':
    for v in p:
     if v.get('adaptive_right_shot',False):v['trigger'].update(state='r060_right_live_aim',timeout=180)
   if n=='hq03'and a=='T':
    k=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='r060_fight');p=[axis(0),cmd('drop_through',1),wait('observed_height',observed_y=dict(direction='gte',value=80),timeout=120),settle(272)]+p[k:]
   if n=='hq07'and a=='R':
    for v in p:
     if v.get('target_x')==790:v['target_x']=798
     if v.get('guard_x')==790:v.update(guard_x=798,safety_first_arc=True)
     if v.get('trigger',{}).get('migration_goal')==[786,331,8,6]:v['trigger']['migration_goal']=[794,331,8,6]
   c['control_plan']=p
  save(r,cs,'v6')
if __name__=='__main__':main()
