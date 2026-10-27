"""Same frozen v2 physical world; explicit external-counter scope policy."""
from pathlib import Path
from . import api_v1 as prior
from .counter_policy_v1 import classify
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
COUNTER_CLASSIFIER=classify
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'counter_policy_v1.py']

def scope_metadata(c):
 c['counter_scope_policy']=dict(version=1,nominal_body_ownership_required=True,external_paid_alternatives='causally accepted only by exact checked criteria; spatial certification UNKNOWN; not internal Module paths')
 c['generation_rule'].update(registration_source=str(Path(__file__).relative_to(HERE.parents[3])),registration_version=2)
 return c

def layouts(recipe,interface):return[scope_metadata(c)for c in prior.layouts(recipe,interface)]
def purpose(c,r):return prior.purpose(c,r)
def alternatives(c):return[scope_metadata(v)for v in prior.alternatives(c)]
