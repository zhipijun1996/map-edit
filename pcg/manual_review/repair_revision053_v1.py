"""Correct observed wall input ordering, cavity takeoff and newly lowered top dock."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,sys
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision053_v1 import rows,label
from .prepare_revision053_v1 import climb
from .prepare_review045_v1 import at,end,axis

def apply(row):
    n=label(row);f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-control-v2-cases.json',dict(cases=cs))
    for c in cs:
        p=c['control_plan']
        if n=='196':
            c['generation_rule']['registration_source']='pcg/manual_review/revision053_author_v4.py'
            for i,v in enumerate(p):
                if v['op']=='axis' and v.get('value')==-1 and i and p[i-1]['op']=='jump':v['trigger']=dict(after=1,state='wall_kick',timeout=30)
        elif n in ['51','52']:
            if c['route_spec']['from_port']=='exit':
                for i,v in enumerate(p):
                    if v.get('target_x')in [52.7,53,54]:v['target_x']=80
                    goal=v.get('trigger',{}).get('migration_goal')
                    if goal and 48<=goal[0]<=51:goal[0]=76
            elif n=='51':
                i=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('migration_goal')and abs(v['trigger']['migration_goal'][0]-106)<1 and abs(v['trigger']['migration_goal'][1]+233)<3)
                p=p[:i+1]+at(132,-230)+[axis(0),cmd('jump'),dict(op='wait',observed_y=dict(value=-290,direction='lte'),trigger=dict(after=1,state='observed_height',timeout=180)),cmd('grapple',aim_target=[330,-350]),cmd('jump_release',1),dict(op='wait',hook_count=2,trigger=dict(after=1,state='hook_done',timeout=240))]+end(*c['exit_port'])
        elif n=='three':
            if c['route_spec']['to_port']=='B':p=[v for v in p if v.get('trigger',{}).get('state')!='chain_final']
            c['generation_rule']['registration_source']='pcg/manual_review/revision053_three_author_v2.py'
        c['control_plan']=p;c['id']=c['id'].replace('r053-v1','r053-v2').replace('r053-v3','r053-v4')
    core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
    for row in rows():
        if label(row)in sys.argv[1:]:apply(row)
