"""N12 source-preserving external-air counter scope registration."""
from pathlib import Path
from . import api_v1 as source,counter_policy_v1 as policy
HERE=Path(__file__).parent
RECIPES=source.RECIPES;RUNNER_SCRIPT=source.RUNNER_SCRIPT;NATIVE_SCENE=source.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(source.__file__),*source.SOURCE_DEPENDENCIES,Path(policy.__file__),HERE/'counter-scope-revision-v1.json']
COUNTER_CLASSIFIER=policy.classify
purpose=source.purpose

def metadata(c):
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 c['counter_scope_policy']=dict(id='N12/slower-external-air-reward-rejoin/v1',nominal_body_strict=True,outside_alternatives='NotcertifiedinternalModulepaths; onlyactualsamegoal/resource/safety/baselinevalid, realupperreward/support, notcheapercost/originalstablecompletion. Spatial/MapUNKNOWN. Norejoin/B->C/ownedgrowthqualification.')
 return c

def layouts(recipe,interface):return[metadata(c)for c in source.layouts(recipe,interface)]
def alternatives(c):return[metadata(v)for v in source.alternatives(c)]
def candidate_for_request(spec,interface=0):
 r=source.candidate_for_request(spec,interface)
 if r.get('cases'):r['cases']=[metadata(c)for c in r['cases']]
 return r
