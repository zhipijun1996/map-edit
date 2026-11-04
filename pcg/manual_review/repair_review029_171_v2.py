if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from pcg.manual_review.prepare_review029_v1 import AUTH,at,end
from pcg.prototype.workshop.rules import cmd

def main():
 r=next(r for r in core.read(AUTH/'handoff.json')['rows']if r['reviewId']=='171');f=core.REPO/r['outputDirectory'];d=core.read(f/'module.mapnote.json');cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v2-cases.json',dict(cases=cs));core.write(f/'history/pre-repair-v2-module.json',d)
 for o in d['objects']:
  if o['type']=='enemy':o['mechanics']['initialIdleCooldown']=2.;o['mechanics'].setdefault('runtimeParameters',{})['initial_idle_cooldown']=2.
 for c in cs:
  for e in c['enemies']:e['initial_idle_cooldown']=2.
  right=c['route_spec']['from_port']=='entry';pos=476 if right else 548;first='design-ambush-left'if right else'design-ambush-right';second='design-ambush-right'if right else'design-ambush-left'
  p=at(pos,420)+[cmd('wait',3)]
  for _ in range(3):
   for ident in [first,second]:p+=[dict(op='wait',trigger=dict(state='grounded_shot_ready',timeout=120)),cmd('shoot',aim_cell=dict(kind='enemy',id=ident)),cmd('wait',17)]
  p+=end(616 if right else 408,420);c['control_plan']=p;c['generation_rule']['registration_source']='pcg/manual_review/review029_author_v4.py'
 d=godot_package.bind_case_behavior(d,cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':main()
