"""115's seventh and final registered program: clear the actual left-lip enemy.

Random ferry phase can leave the native carried enemy at the left lip rather
than its nominal center; shoot from the bank before boarding, using live x.
"""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .prepare_review040_v3 import rows,at,end,phase
from .repair_review040_v9 import board
from .finalize_review040_v1 import folder_for
def apply(row):
 f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v10-cases.json',dict(cases=cs))
 final=folder_for(row)
 if final.exists():
  assert not(final/'qualification.json').exists()
  final.rename(final.with_name(final.name+'-pre-final-control-v1'))
 for c in cs:
  if c['route_spec']['from_port']=='entry':
   p=at(240,582)
   for _ in range(4):
    block=[dict(op='wait',enemy_position=dict(id='design-carrier-enemy',minimum_x=-100000,maximum_x=430),trigger=dict(state='enemy_x_ready',timeout=900)),dict(op='shoot',aim_cell=dict(kind='enemy',id='design-carrier-enemy'),trigger=dict(state='grounded_shot_ready',timeout=180))]+at(240,582)
    for v in block:v['skip_if_enemy_dead']='design-carrier-enemy'
    p+=block
   c['control_plan']=p+[phase('ferry',[0,.02])]+board(1)+[phase('ferry',[.5,.52])]+end(*c['exit_port'])
  c['generation_rule']['registration_source']='pcg/manual_review/review040_author_v6.py';c['id']=c['id'].replace('review040-v9','review040-v10')
 d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':apply(next(r for r in rows()if r['reviewId']=='115'))
