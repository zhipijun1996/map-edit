"""Additional real cheap-C policies, sharing the exact repaired world."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from . import rules_v1 as rules

SOURCE_DEPENDENCIES=[Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES


def extra(interface=0):
    c=rules.cases(interface)[0]
    c['route_spec']=dict(id='middle-park-to-C-counter',from_port='A',to_port='C',role='reward',via_ports=['B'])
    c['expected_reward']=12;c['challenge_route']=True
    end=next(p['position']for p in c['ports']if p['id']=='C')
    c['exit_port']=end;c['goal']=[end[0]-25,end[1]-4,50,8]
    c['max_frames']=1800;prefix=copy.deepcopy(c['control_plan']);dx=interface*30
    front=c['platforms'][3][0];out=[]
    def add(label,plan):
        v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
    for launch in [front-100,front-60]:
        for dy in [.7,.8660254,1.]:
            for hold in [8,20]:
                add(f'floor-climb-{launch}-{dy}-{hold}',prefix+[cmd('axis',value=1),wait_x(launch),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=1),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-math.sqrt(max(0,1-dy*dy)),dy]),settle(end[0],0)])
    for x in [840+dx,880+dx]:
        for dy in [.15,.35,.5,.7,.8660254,1.]:
            add(f'later-B-fall-{x}-{dy}',prefix+[cmd('axis',value=1),wait_x(x),cmd('shoot',direction=[-math.sqrt(max(0,1-dy*dy)),dy]),settle(end[0],0)])
    return out
