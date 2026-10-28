"""Delay recoil until closer to the new high bank; truly return to A dock."""
from pathlib import Path
from . import rules_v1 as prior
from pcg.prototype.workshop.rules import wait_x
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json']
DELAYS=[24,28]

def revised(c,delay):
 c['id']=c['id'].replace('block-c10-v1','block-c10-v2')+'-d'+str(delay)
 c['rule_parameters']['block_main_release_delay']=delay
 kind=c.get('counterexample_kind')
 if not kind or kind in ['omit-correction','omit-restoration','omit-retry-recoil']:
  q=c['control_plan'][-5];assert q['op']=='jump_release';q['trigger']['after']=delay
 out=[]
 for q in c['control_plan']:
  out.append(q)
  if q.get('op')=='settle'and q.get('target_x')==-104:out.append(wait_x(-97,-1))
 c['control_plan']=out
 c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])),control_revision=dict(main_release_delay=delay,actual_A_wait_x=-97))
 return c

def candidates(delay=24):
 if delay not in DELAYS:raise ValueError('outside preregistered release domain')
 return[revised(c,delay)for c in prior.layouts(RECIPES[0],0)]

def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('only one Block C10 interface')
 return candidates(24)

def purpose(c,r):return prior.purpose(c,r)

def alternatives(c):return[revised(v,c['rule_parameters']['block_main_release_delay'])for v in prior.alternatives(c)]
