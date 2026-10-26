"""Input-only finite proposals for the v2 drop/air-recoil boundary profile."""
import copy


def transfer(source,destination,plane):
    sx,sy=source['position'];dx,dy=destination['position'];px=plane[0]
    if abs(abs(dy-sy)-128)>.01 or abs(dx-sx)>256:raise ValueError('v2_vertical_staging_outside_128_domain')
    direction=1 if px>sx else-1
    if (dx-sx)*direction>0 and abs(dx-sx)>=128:
        if dy>sy:return [dict(kind='walk',target=destination,budget_ticks=360)]
        from pcg.prototype.workshop.rules import cmd,settle
        plan=[cmd('axis',value=direction),cmd('jump'),cmd('jump_release',8),cmd('shoot',2,direction=[-direction*.6,.8]),settle(dx,8)]
        return [dict(kind='module',target=destination,control_plan=plan,budget_ticks=900)]
    from pcg.prototype.workshop.rules import cmd,settle
    if dy>sy:
        plan=[cmd('axis',value=direction),dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte'if direction>0 else'lte',value=px),timeout=180)),settle(dx,0)]
        return [dict(kind='module',target=destination,control_plan=plan,budget_ticks=900)]
    launch=copy.deepcopy(source);launch['position'][0]+=direction*20;launch['region'][0]+=direction*20;launch['id']+='/vertical-launch'
    plan=[cmd('axis',value=direction),cmd('jump'),cmd('jump_release',1),cmd('axis',8,value=-direction),cmd('shoot',4,direction=[0,1]),settle(dx,2)]
    return [dict(kind='walk',target=launch,budget_ticks=360),dict(kind='module',target=destination,control_plan=plan,budget_ticks=900)]
