"""Search cheaper actual policies on identical geometry; never assert necessity."""
import copy
from .rules import launch,settle,cmd,wait_x

def alternatives(base):
    out=[]
    def add(label,plan):
        c=copy.deepcopy(base);c['id']+='-counter-'+label;c['control_plan']=plan;c['counterexample_kind']=label
        out.append(c)
    for index,step in enumerate(base['control_plan']):
        if step['op']!='shoot':continue
        plan=copy.deepcopy(base['control_plan']);plan[index]={'op':'wait','trigger':copy.deepcopy(step.get('trigger',{}))}
        add('omit-shot-'+str(index),plan)
    for hold in [0,4,8,12,20,30]:
        for takeoff in [180,220,238]:
            plan=[cmd('axis',value=1),wait_x(takeoff),cmd('jump'),cmd('jump_release',hold),settle(base['exit_port'][0],4)]
            add(f'ordinary-jump-{takeoff}-{hold}',plan)
    if base['family']in ['timed-cache','chase-landing']:
        plan=copy.deepcopy(base['control_plan']);i=next(i for i,s in enumerate(plan)if s['op']=='shoot')
        shot=plan.pop(i);shot['trigger']={'after':0}
        add('early-ground-shot',[shot]+plan)
    if base['family']=='thorn-slot':
        for takeoff in [80,180,220]:
            plan=launch(20,25,1,takeoff)+[settle(base['exit_port'][0],6)]
            add('over-top-'+str(takeoff),plan)
    if base['family']=='chase-landing':
        plan=copy.deepcopy(base['control_plan'][:4]);plan += [cmd('axis',value=0,after=10),cmd('wait',480)]
        add('passive-carrier',plan)
    if base['family']=='brake-under-ledge':
        for x in [-180,260,290,320]:
            direction=-1 if x<0 else 1
            plan=[cmd('axis',value=direction),wait_x(x,direction),settle(base['exit_port'][0])]
            add('drop-turn-no-shot-'+str(x),plan)
    if base['family']=='air-refund':
        for hold in [8,16,24]:
            for dy in [.5,.8660254037844386,1.]:
                import math
                add(f'one-shot-direct-{hold}-{dy}',launch(hold,hold+6,dy,205)+[settle(base['exit_port'][0],6)])
    return out
