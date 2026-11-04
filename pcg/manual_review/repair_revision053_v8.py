if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision053_v1 import rows,label
from .prepare_review045_v1 import at,end,axis
from .prepare_ideas_v1 import settle

def wait(name,timeout=900):return dict(op='wait',trigger=dict(after=1,state='revision_lift_'+name,timeout=timeout))
def target(name):return dict(op='settle',revision_target=name,target_x=192,deadband=.6,source_native_gain=5.5,trigger=dict(after=0))
def main():
    row=next(r for r in rows()if label(r)=='lift');f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-control-v2-cases.json',dict(cases=cs))
    for c in cs:
        c['generation_rule']['registration_source']='pcg/manual_review/revision053_lift_author_v2.py';c['id']=c['id'].replace('r053-v1','r053-v2');c['max_frames']=3600
        if c['route_spec']['to_port']!='B':continue
        c['control_plan']=at(192,846)+[wait('clear',1200),wait('choose_lower',2200),target('edge'),wait('edge',240),axis(0),cmd('jump'),cmd('jump_release',24),cmd('shoot',4,direction=[0,1]),wait('above_g1',180),target('lower'),wait('lower_support',240),wait('transfer',600),target('lower_launch'),wait('lower_launch',120),settle(192),cmd('jump'),cmd('jump_release',24),dict(op='shoot',direction=[0,1],revision_transfer_shot=True,trigger=dict(after=4)),cmd('wait',12),target('upper'),wait('upper_support',240),wait('finish',900),target('finish'),wait('finish_edge',240),settle(192),cmd('jump'),dict(op='shoot',direction=[0,1],revision_final_shot=True,trigger=dict(after=20)),cmd('jump_release',8)]+end(192,46)+[dict(op='shoot',direction=[0,-1],aim_cell=dict(kind='bell',id='top-exit-bell'),trigger=dict(after=4,state='grounded_shot_ready',timeout=300)),cmd('wait',12),cmd('jump'),cmd('jump_release',24)]+end(192,-50)
    core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':main()
