"""Cast from the correct side of each native bounce anchor; phase-align side ingress."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import sys
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision053_v1 import rows,label
from .prepare_review045_v1 import at,end,axis

def hook_done(count):return dict(op='wait',hook_count=count,trigger=dict(after=1,state='hook_done',timeout=240))
def apply(row):
    n=label(row);f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-control-v3-cases.json',dict(cases=cs))
    for c in cs:
        p=c['control_plan'];a=c['route_spec']['from_port']
        if n=='196':
            if a=='exit':p=[axis(0),dict(op='wait',trigger=dict(after=1,state='saw_exit_ready',timeout=240))]+p
            c['generation_rule']['registration_source']='pcg/manual_review/revision053_author_v5.py'
        elif n=='51' and a=='entry':
            i=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('migration_goal')and abs(v['trigger']['migration_goal'][0]-106)<1 and abs(v['trigger']['migration_goal'][1]+233)<3)
            p=p[:i+1]+at(132,-230)+[dict(op='settle',target_x=375,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',24),cmd('shoot',4,direction=[-.8,.6]),dict(op='wait',height_threshold=-390,trigger=dict(after=1,state='falling_height',timeout=240)),cmd('grapple',aim_target=[330,-350]),hook_done(2)]+end(*c['exit_port'])
        elif n in ['51','52'] and a=='exit':
            i=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('migration_goal')and abs(v['trigger']['migration_goal'][0]-106)<1 and abs(v['trigger']['migration_goal'][1]+233)<3)
            p=p[:i+1]+at(80,-230)+[dict(op='settle',target_x=-70,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',18),dict(op='wait',height_threshold=-355,trigger=dict(after=1,state='falling_height',timeout=240)),cmd('grapple',aim_target=[-35,-350]),hook_done(2),cmd('shoot',4,direction=[.85,.5267826876])]+end(*c['exit_port'])
        c['control_plan']=p;c['id']=c['id'].replace('r053-v2','r053-v3').replace('r053-v4','r053-v5')
    core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
    for row in rows():
        if label(row)in sys.argv[1:]:apply(row)
