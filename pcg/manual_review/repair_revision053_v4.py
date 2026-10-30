"""Keep the last recoil outside the high rock shore, then cross above its top."""
import copy
from pcg.migration import core,godot_package
from .continue_revision053_v1 import rows,label
from .prepare_review045_v1 import at,end,axis
from .prepare_ideas_v1 import settle
from .repair_review040_v5 import safe_kill

def main():
    row=next(r for r in rows()if label(r)=='220');f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-control-v3-cases.json',dict(cases=cs))
    originalC=next(c for c in cs if c['route_spec']['from_port']=='C'and c['route_spec']['to_port']=='A');p=originalC['control_plan'];start=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='enemy_attack_ready')-1;last=max(i for i,v in enumerate(p)if v['op']=='shoot'and v.get('aim_cell',{}).get('id')=='design-air-enemy');ladder=copy.deepcopy(p[start:last+1]);seen=0
    for v in ladder:
        if v.get('follow_enemy'):v['follow_enemy']['distance']=16
        if v['op']=='shoot':
            seen+=1
            if seen>1:
                v['align_enemy']=dict(id='design-air-enemy',distance=16,height=380 if seen==2 else 360);v['aim_cell']['body_offset']=[0,8];v['trigger'].update(state='aligned_refund',after=4)
    for c in cs:
        if c['route_spec']['to_port']!='A':continue
        if c['route_spec']['from_port']=='C':prefix=copy.deepcopy(c['control_plan'][:start])
        else:
            old=c['control_plan'];index=next(i for i,v in enumerate(old)if v.get('trigger',{}).get('state')=='enemy_attack_ready')-1
            prefix=copy.deepcopy(old[:index])+safe_kill('design-ground-enemy',480,562)+at(580,562)+[dict(op='wait',enemy_position=dict(id='design-air-enemy',minimum_x=450,moving_side=1),trigger=dict(state='enemy_x_ready',timeout=900))]+at(441,562)
        c['control_plan']=prefix+copy.deepcopy(ladder)+[settle(380),dict(op='shoot',direction=[.55,.8351646544],trigger=dict(after=4,state='ledge_recoil',timeout=240)),dict(op='wait',trigger=dict(after=1,state='ledge_clear',timeout=90))]+end(24,190)
        c['generation_rule']['registration_source']='pcg/manual_review/revision053_author_v6.py';c['id']=c['id'].replace('r053-v2','r053-v3')
    core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':main()
