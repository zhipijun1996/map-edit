"""Original lower access receiver added for a real bounded recovery witness."""
from pathlib import Path
from . import rules_v1 as prior
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=prior.SOURCE_DEPENDENCIES+[Path(prior.__file__),HERE/'protocol-v2.json']
CONTROL={(0,'high'):1,(1,'high'):0,(0,'low'):0,(1,'low'):0}
def materialize(interface=0,route='high',control=0):
 c=prior.materialize(interface,route,control)
 if interface==0:c['latches'][0]['return_access']=[230,920]
 c['id']=c['id'].replace('v1','v2')
 c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','reward_sites']})
 c['map_specification']['objective']['physical_layout_sha256']=c['layout_uid']
 c['map_specification']['return_conditions']='Broad exact late-high-miss recovery is a separate continuous fixture. Slender floor primary aiming/recovery and all other port directions remainUNKNOWN; no no_path proof.'
 return c
def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in [0,1]:raise ValueError('outside C06 exact two spaces')
 return[materialize(interface,r,CONTROL[(interface,r)])for r in ['high','low']]
def purpose(c,r):return prior.purpose(c,r)
def alternatives(c):return prior.alternatives(c)
