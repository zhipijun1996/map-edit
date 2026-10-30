"""Keep initial ground recoil grounded under aim noise; clear floor before side motion."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import sys
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision053_v1 import rows,label
from .prepare_review045_v1 import at,end,axis
from .repair_revision053_v2 import hook_done

def apply(row):
    n=label(row);f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-control-v4-cases.json',dict(cases=cs))
    for c in cs:
        p=c['control_plan']
        if c['route_spec']['from_port']=='entry':
            first=next(v for v in p if v['op']=='shoot');first['direction']=[-.98,-.1989974874]
        else:
            first=next(v for v in p if v['op']=='shoot');first['direction']=[.8,.6]
            i=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('migration_goal')and abs(v['trigger']['migration_goal'][0]-106)<1 and abs(v['trigger']['migration_goal'][1]+233)<3)
            p=p[:i+1]+at(54,-230)+[axis(0),cmd('jump'),dict(op='wait',observed_y=dict(value=-260,direction='lte'),trigger=dict(after=1,state='observed_height',timeout=120)),dict(op='settle',target_x=-50,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',trigger=dict(state='airborne',dynamic=dict(kind='actor_x',direction='lte',value=-49),timeout=180)),cmd('grapple',aim_target=[-35,-350]),cmd('jump_release',1),hook_done(2),cmd('shoot',4,direction=[.98,.1989974874])]+end(*c['exit_port'])
        c['control_plan']=p;c['id']=c['id'].replace('r053-v3','r053-v4')
    core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
    for r in rows():
        if label(r)in sys.argv[1:]:apply(r)
