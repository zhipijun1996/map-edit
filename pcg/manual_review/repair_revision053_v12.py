"""Use two additional real ring contacts to gain shore clearance, without grants."""
import copy
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision053_v1 import rows,label
from .prepare_review045_v1 import end
from .repair_revision053_v2 import hook_done

def main():
 r=next(r for r in rows()if label(r)=='50');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-control-v6-cases.json',dict(cases=cs))
 ci=next(c for c in cs if c['route_spec']['from_port']=='C'and c['route_spec']['to_port']=='entry');p=ci['control_plan'];i=next(i for i,v in enumerate(p)if v.get('hook_count')==3);prefix=p[:i+1]+[cmd('grapple',4,aim_target=[200,-40]),hook_done(4),cmd('grapple',4,aim_target=[200,-40]),hook_done(5)]
 ci['control_plan']=prefix+end(*ci['exit_port']);ci['expected_hook_sequence']=['lower_window_ring']+['upper_window_ring']*4
 co=next(c for c in cs if c['route_spec']['from_port']=='C'and c['route_spec']['to_port']=='exit');out=next(c for c in cs if c['route_spec']['from_port']=='entry'and c['route_spec']['to_port']=='exit');tail=copy.deepcopy(out['control_plan'])
 for v in tail:
  if 'hook_count'in v:v['hook_count']+=5
 co['control_plan']=copy.deepcopy(ci['control_plan'])+tail;co['expected_hook_sequence']=ci['expected_hook_sequence']+out['expected_hook_sequence']
 for c in [ci,co]:c['id']+='-repeatclearance'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':main()
