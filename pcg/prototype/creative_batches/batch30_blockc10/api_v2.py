"""Repair counter identity binding; physical worlds and controls stay v2."""
from pathlib import Path
from . import api_v1 as prior
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'identifier-repair-v1.json']

def metadata(c):
    c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
    c['generation_rule']['registration_version']=2
    return c

def layouts(recipe,interface):return[metadata(c)for c in prior.layouts(recipe,interface)]
def purpose(c,r):return prior.purpose(c,r)
def alternatives(c):
    out=prior.alternatives(c)
    for v in out:
        v['id']=c['id']+'-counter-'+v['counterexample_kind']
        metadata(v)
    return out

def for_exact_request(spec):
    result=prior.for_exact_request(spec)
    if 'cases'in result:result['cases']=[metadata(c)for c in result['cases']]
    return result
