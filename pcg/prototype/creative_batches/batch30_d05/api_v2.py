"""Repair first post-shot interception: fixed roof no longer receives actor."""
import copy
from pathlib import Path
from . import api_v1 as prior
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=prior.SOURCE_DEPENDENCIES+[Path(prior.__file__),HERE/'protocol-v3.json']
CONTROL={0:0,1:0}
def materialize(interface=0,control=0):
 c=prior.materialize(interface,control);c['platforms'][2][2]=35
 c['id']=c['id'].replace('api1','api2')
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','moving_platforms','latches','reward_sites']})
 c['map_specification']['objective']['physical_layout_sha256']=c['layout_uid']
 c['rule_parameters']['roof']=c['platforms'][2]
 c['generation_rule'].update(version=3,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 return c
def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in CONTROL:raise ValueError('outside registered D05 demands')
 return [materialize(interface,CONTROL[interface])]
def purpose(c,r):
 q=prior.purpose(c,r);fs=r.get('frames',[])
 shot=next((f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))),None)
 first=next((f for f in fs if shot and f['frame']>shot['frame']and f.get('grounded')),None)
 q['causal']['first_post_shot_support']={k:first.get(k)for k in ['frame','support_id','x','y','shot_charges']}if first else None
 if not first or first.get('support_id')!='catch-deck':q['reasons'].append('first_landing_is_not_moving_catch_deck')
 q['ok']=not q['reasons'];return q
def alternatives(c):return prior.alternatives(c)
