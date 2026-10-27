"""Bounded original-input counterexamples for the real raised-enemy perch.

Exactly28 programs/exact route:10 broad direct,3 omitted shots,15 perch/resource
scenarios. No actor/resources/death writes. Ground kills and perch landings are
actual original mechanisms; a paid safe alternative is not automatically a refutation.
"""
import copy
from . import rules_v2 as rules
cmd,wait_x,ground,settle=rules.cmd,rules.wait_x,rules.ground,rules.settle

def approach(x,origin=80):
 sign=1 if x>=origin else-1
 return [cmd('axis',value=sign),wait_x(x,sign),*rules.stop_ground()]

def ground_hits(count,safe=0):
 out=approach(safe)
 toward=1 if safe<125 else-1
 for _ in range(count):
  out += [cmd('shoot',aim_cell=dict(kind='enemy',id='shared-sentry')),cmd('axis',value=toward),cmd('wait',10),wait_x(safe,toward),*rules.stop_ground()]
 return out+approach(80,safe)

def staged_tail(c):
 name='east-staged'if c['route_spec']['to_port']=='B'else'west-staged'if c['route_spec']['to_port']=='C'else'main'
 return copy.deepcopy(next(v for v in rules.layouts(rules.RECIPES[0],c['interface'],c['rule_parameters']['control'])if v['route_spec']['id']==name)['control_plan'])

def perch(c,launch=50,first_shot=True,last_shot=True):
 sign=1 if launch<125 else-1
 direction=1 if c['exit_port'][0]>125 else-1
 out=approach(launch)+[cmd('axis',value=sign),cmd('jump'),cmd('jump_release',12)]
 out += [cmd('shoot',6,direction=[0,1])]if first_shot else[cmd('wait',6)]
 out += [wait_x(125,sign),*rules.stop_ground(),cmd('axis',value=direction),cmd('jump'),cmd('jump_release',16)]
 out += [cmd('shoot',6,direction=[-direction*.6,.8])]if last_shot else[cmd('wait',6)]
 return out+[settle(c['exit_port'][0],6)]

def alternatives(c):
 out=[]
 def add(label,plan,scenario):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['counter_scenario']=scenario;v['control_plan']=copy.deepcopy(plan);out.append(v)
 original=rules.alternatives(c)
 for sign in(-1,1):
  for hold,delay in[(0,0),(8,0),(8,24),(24,0),(24,24)]:
   name=f'direct-{sign}-{hold}-{delay}';v=next(v for v in original if v['counterexample_kind']==name);out.append(v)
 shots=[i for i,op in enumerate(c['control_plan'])if op['op']=='shoot']
 # Main has no shots: retain independent ordinaryjump16 direct alternatives.
 for n in range(3):
  if n<len(shots):
   index=shots[n];plan=copy.deepcopy(c['control_plan']);plan[index]=dict(op='wait',trigger=copy.deepcopy(plan[index]['trigger']));add('omit-key-shot-'+str(n),plan,'actual omission with timing preserved')
  else:
   name=f'direct-{(-1 if n==0 else 1)}-16-{n*12}';out.append(next(v for v in original if v['counterexample_kind']==name))
 for launch in(50,170):
  for fire in(False,True):add(f'live-perch-{launch}-shot{int(fire)}',perch(c,launch,fire), 'living shared enemy occupies full real28px perch top')
 for safe in(0,220):add(f'ground-clear3-then-staged-{safe}',ground_hits(3,safe)+staged_tail(c),'actual3HP ground elimination then original grounded route; paid alternative allowed')
 for launch in(50,170):add(f'ground-clear3-perch-{launch}',ground_hits(3)+perch(c,launch), 'actual dead enemy, real perch support/refill, then try onejump reward shortcut')
 for launch in(50,170):add(f'one-ground-hit-perch-{launch}',ground_hits(1)+perch(c,launch),'one actual ground hit then live-perch landing/shortcut')
 for count in(1,2):add(f'ground-hit{count}-then-canonical',ground_hits(count)+c['control_plan'],'depleted real HP then original air/world program, no replacement actor')
 add('clear3-perch-unarmed',ground_hits(3)+perch(c,50,False,False),'actual dead enemy and new support; no generic recoil in either jump')
 firstair=next(v for v in rules.layouts(rules.RECIPES[0],c['interface'],c['rule_parameters']['control'])if v['route_spec']['id']=='west-air')
 index=next(i for i,op in enumerate(firstair['control_plan'])if op['op']=='shoot')
 prefix=firstair['control_plan'][:index+1]+[cmd('axis',value=1),wait_x(80),*rules.stop_ground()]
 add('one-air-hit-then-ground-staged',prefix+staged_tail(c),'one real airborne damage receipt followed by actual ground recovery and staged alternative')
 add('one-ground-hit-then-staged',ground_hits(1)+staged_tail(c),'one actual ground hit before otherwise HP-preserving staged route')
 assert len(out)==28,len(out)
 assert len({v['id']for v in out})==28
 return out


def depleted_comparisons(recipe,interface,control=0):
 """Same-world residual1HP, with actual return to the canonical80 launch x.

The old helper stopped at groundclear x0; this comparison explicitly walks back
under the actual perch to x80 before either branch, without state/resource reset.
 """
 cases=rules.layouts(recipe,interface,control)
 canonical=next(v for v in cases if v['route_spec']['id']=='east-then-dead-west')
 plan=canonical['control_plan']
 kill=next(i for i,op in enumerate(plan)if op['op']=='shoot'and op.get('aim_cell')and i>15)
 prefix=plan[:kill]+approach(80,0)
 out=[]
 for style in('air','staged'):
  tail=next(v for v in cases if v['route_spec']['id']=='west-'+style)
  v=copy.deepcopy(canonical);v['id']+='-remaining-one-'+style;v['control_plan']=copy.deepcopy(prefix+tail['control_plan']);v['purpose_kind']='remaining_one_'+style;v['comparison_only']=True;v['comparison_branch_plan_index']=len(prefix);out.append(v)
 return out
