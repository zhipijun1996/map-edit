"""Bring lower-to-upper hook casts into a short real ray and regain the upper dock."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision053_v1 import rows,label
from .prepare_review045_v1 import at,end,axis
from .repair_revision053_v2 import hook_done

def main():
    row=next(r for r in rows()if label(r)=='50');f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-control-v2-cases.json',dict(cases=cs))
    reverse=copy.deepcopy(next(c['control_plan']for c in cs if c['route_spec']['from_port']=='exit'and c['route_spec']['to_port']=='entry'))
    for c in cs:
        if c['route_spec']['from_port']!='C':continue
        prefix=c['control_plan'][:7]+at(276,332)
        p=prefix+[dict(op='settle',target_x=198,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('grapple',18,aim_target=[120,155]),cmd('jump_release',1),hook_done(1),axis(0),dict(op='shoot',direction=[-.25,.9682458366],trigger=dict(after=4,state='shot_ready',timeout=120)),cmd('wait',12),cmd('grapple',aim_target=[200,-40]),hook_done(2),cmd('grapple',4,aim_target=[200,-40]),hook_done(3)]+end(488,-42)
        c['expected_hook_sequence']=['lower_window_ring','upper_window_ring','upper_window_ring']
        if c['route_spec']['to_port']=='entry':
            for v in reverse:
                if v.get('trigger',{}).get('state')=='hook_done':v['hook_count']=4
            p+=reverse;c['expected_hook_sequence'].append('upper_window_ring');c['route_spec']['via_ports']=['exit']
        c['control_plan']=p;c['id']=c['id'].replace('r053-v1','r053-v2')
    core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':main()
