"""Approach the original sentry from its safe rear shore using a real jump."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision053_v1 import rows,label
from .prepare_review045_v1 import at
from .prepare_ideas_v1 import settle

def main():
 r=next(r for r in rows()if label(r)=='220');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v10-cases.json',dict(cases=cs))
 source=next(c for c in cs if c['route_spec']['from_port']=='C'and c['route_spec']['to_port']=='A');i=next(i for i,v in enumerate(source['control_plan'])if v.get('skip_if_enemy_dead')=='design-ground-enemy')
 target=next(c for c in cs if c['route_spec']['from_port']=='B'and c['route_spec']['to_port']=='A');p=target['control_plan'];k=next(k for k,v in enumerate(p)if v.get('skip_if_enemy_dead')=='design-ground-enemy');target['control_plan']=p[:k]+[settle(580),cmd('jump'),cmd('jump_release',24)]+at(580,562)+copy.deepcopy(source['control_plan'][i:]);target['id']+='-rear'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':main()
