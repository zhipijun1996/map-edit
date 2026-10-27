"""Classifier-scope registration only; original N08 world/programs are frozen."""
from pathlib import Path
from . import api_v1 as source,counter_policy_v2 as policy
HERE=Path(__file__).parent
RECIPES=source.RECIPES;RUNNER_SCRIPT=source.RUNNER_SCRIPT;NATIVE_SCENE=source.NATIVE_SCENE;EXPORT_SCRIPT=source.EXPORT_SCRIPT
SOURCE_DEPENDENCIES=[Path(source.__file__),*source.SOURCE_DEPENDENCIES,Path(policy.__file__),HERE/'counter-scope-revision-v1.json']
COUNTER_CLASSIFIER=policy.classify
purpose=source.purpose


def metadata(c):
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 c['counter_scope_policy']=dict(id='N08/slower-external-air/v1',nominal_body_strict=True,outside_alternatives='NotacceptedModulepaths; onlyactualcore/goal/resourcevalid andnotcheapercost/12frameAcompletion. Spatial/MapUNKNOWN; noownedgrowth.')
 return c


def layouts(recipe,interface):return[metadata(c)for c in source.layouts(recipe,interface)]
def alternatives(c):return[metadata(v)for v in source.alternatives(c)]


def candidate_for_request(spec,interface=0):
 response=source.candidate_for_request(spec,interface)
 if response.get('cases'):response['cases']=[metadata(c)for c in response['cases']]
 return response
