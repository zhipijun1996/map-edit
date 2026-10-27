"""Same reward/B visit/full return goals; preserve legitimate old-route choices."""
import copy,math
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,ground

def normal_timeout(plan):
 for p in plan:
  if p.get('trigger',{}).get('dynamic',{}).get('kind')=='actor_x':p['trigger']['timeout']=max(p['trigger'].get('timeout',0),475)
 return plan

def old_upper_return(dy=.8660254037844386,shot=True):
 p=[rules.old.seek(1304),rules.old.reach(1304,-1),ground(),rules.old.seek(24),cmd('jump'),cmd('jump_release',20)]
 if shot:p+=[cmd('shoot',direction=[math.sqrt(1-dy*dy),dy])]
 p +=[rules.old.reach(24,-1),ground(),cmd('wait',20)]
 return normal_timeout(p)

def loop_alternatives(c):
 control=c['rule_parameters']['control'];out=[];prefix=normal_timeout(rules.old.outbound(control));ret=normal_timeout(rules.old.lower_return())
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=normal_timeout(plan);out.append(v)
 add('old-upper-return-recoil-0866',copy.deepcopy(prefix)+old_upper_return())
 add('old-upper-return-recoil-0800',copy.deepcopy(prefix)+old_upper_return(.8))
 add('old-upper-return-ordinary-no-shot',copy.deepcopy(prefix)+old_upper_return(shot=False))
 add('direct-walk-off-B-no-switch',copy.deepcopy(prefix)+[rules.old.seek(24),rules.old.reach(24,-1),ground(),cmd('wait',20)])
 # Supported lower-bank cut is a legal slower alternative, not an air-order failure.
 drop=[rules.old.seek(1216),rules.old.reach(1216,-1),ground()]
 for hold,dy in [(20,.15),(30,.35),(20,.6),(30,.85)]:
  add(f'lower-bank-direct-recoil-skip-R-{hold}-{dy}',copy.deepcopy(prefix)+copy.deepcopy(drop)+[rules.old.seek(1208),rules.old.reach(1208,-1),ground(),rules.old.seek(24),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[math.sqrt(1-dy*dy),dy]),rules.old.reach(24,-1),ground(),cmd('wait',20)])
 add('late-ground-primary-cut-then-R',copy.deepcopy(prefix)+copy.deepcopy(drop)+[cmd('shoot',aim_cell=dict(kind='bell',id='fold-pair')),cmd('wait',60),rules.old.seek(24),cmd('jump'),cmd('jump_release',20),rules.old.reach(24,-1),ground(),cmd('wait',20)])
 # Same full task for all deletion tests, never an unrewarded low walk.
 for j,s in enumerate(prefix):
  if s['op']=='shoot':
   p=copy.deepcopy(prefix);p[j]=dict(op='wait',trigger=copy.deepcopy(s['trigger']));add('omit-upper-shot-'+str(j),p+copy.deepcopy(ret))
 for hold in [8,20,30]:
  p=copy.deepcopy(prefix);j=next(i for i,s in enumerate(p)if s['op']=='shoot');p[j]=dict(op='wait',trigger=copy.deepcopy(p[j]['trigger']));p[j-1]['trigger']['after']=hold;add('ordinary-first-upper-stage-'+str(hold),p+copy.deepcopy(ret))
 p=copy.deepcopy(ret);j=next(i for i,s in enumerate(p)if s['op']=='shoot');p[j]=cmd('shoot',direction=[0,-1]);add('miss-B-access-no-retry',copy.deepcopy(prefix)+p)
 assert len(out)==16,len(out)
 return out


def task_outcome(c,r):
 fs=r.get('frames',[]);isback=c['route_spec']['from_port']=='B';coins=r.get('workshop',{}).get('coins',0);claims=[e for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')and e.get('id')=='upper-cache'];loop=c.get('fixture_kind')=='same-world-A-B-A';b=rules.old.visits(fs,1512,334);end=rules.old.visits(fs,24,718,b[0]['frame']if loop and b else-1)
 q=rules.purpose(c,r);safety=not set(q['reasons'])&{'player_harm','forbidden_ability','world_reset','actual_body_left_frozen_ownership'}
 good=bool(r.get('ok')and safety and(len(b)>=12 if loop else True)and len(end)>=12 and(coins==0 and not claims if isback else coins==16 and len(claims)==1))
 return dict(ok=good,coins=coins,accepted_reward_claims=len(claims),actual_B_first=b[0]['frame']if b else None,actual_A_first=end[0]['frame']if end else None,return_frames=(end[0]['frame']-b[0]['frame'])if loop and b and end else None,shots=r.get('shots'),jumps=r.get('jumps'),whole_task_includes_real_reward=not isback)


def classify(c,r,check,outcome,baseline=None):
 from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import counter_classification
 initial=counter_classification(c,r,check,outcome,baseline)
 # For an earned outbound quest, keep the actually demonstrated upper bridge;
 # return route may legally use old upper space or the floor. Compare costs.
 only_return_reasons={'actual_lower_bridge_support_refill_missing','actual_lower_exchange_after_B_missing'}
 reasons=set(check['reasons'])
 if outcome['ok']and reasons<=only_return_reasons:
  initial.update(invalidates_design=False,reason='Allowed actual same-task return alternative: old upper/floor path need not reproduce lower-switch words. Shortcut/easier claims require measured costs; not assumed.',return_alternative=True,shortcut_claim_supported=False)
 return initial
