"""Metadata-only registration fix: full must evaluate both A->B witnesses."""
from pathlib import Path
from . import api_v1 as prior
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES]
purpose=prior.purpose
alternatives=prior.alternatives

def layouts(recipe,interface):
 cs=prior.layouts(recipe,interface)
 for c in cs:
  c['route_spec']['role']='main'
  c['generation_rule']['registration_source']=str(Path(__file__).relative_to(Path(__file__).parents[4]))
 return cs
