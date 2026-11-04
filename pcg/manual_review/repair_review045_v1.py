"""First new-round repairs derived from the preserved 040 failure episodes."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .refresh_review045_v1 import rows,RETRIES
from .prepare_review045_v1 import at,end,height,axis,phase
from .repair_review040_v9 import board
from .repair_review040_v5 import safe_kill
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/imported-review040-cases.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan']
  if n=='115'and a=='entry':
   p=at(230,582)
   for _ in range(12):
    block=[dict(op='wait',enemy_position=dict(id='design-carrier-enemy',minimum_x=-100000,maximum_x=430),trigger=dict(state='enemy_x_ready',timeout=900)),dict(op='shoot',aim_cell=dict(kind='enemy',id='design-carrier-enemy',body_offset=[0,-6]),trigger=dict(state='grounded_shot_ready',migration_goal=[226,579,8,6],timeout=180))]+at(230,582)
    for v in block:v['skip_if_enemy_dead']='design-carrier-enemy'
    p+=block
   p+=[phase('ferry',[0,.02])]+board(1)+[phase('ferry',[.5,.52])]+end(*c['exit_port'])
  elif n=='220'and a=='C'and z=='A':
   b=next(v for v in cs if v['route_spec']['from_port']=='B'and v['route_spec']['to_port']=='A')['control_plan'];i=next(i for i,v in enumerate(b)if v['op']=='jump'and i>5);tail=b[i-1:]
   p=at(650,492)+at(580,562)+safe_kill('design-ground-enemy',580,562)+at(500,562)+[dict(op='wait',enemy_position=dict(id='design-air-enemy',minimum_x=450,moving_side=1),trigger=dict(state='enemy_x_ready',timeout=900))]+tail
  elif n=='225'and a=='B':
   first=next(v for v in p if v['op']=='jump_release');first['trigger']['after']=24
  for v in p:
   if v.get('trigger',{}).get('migration_goal'):v['trigger']['after']=max(1,v['trigger'].get('after',0))
  c['control_plan']=p
 doc=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 for row in rows():
  if row['reviewId']in RETRIES:apply(row)
