"""Explicit original route metadata, no geometry/control/resource changes."""
from pathlib import Path
from . import api_v1 as previous
RECIPES=previous.RECIPES
RUNNER_SCRIPT=previous.RUNNER_SCRIPT
NATIVE_SCENE=previous.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(previous.__file__),*previous.SOURCE_DEPENDENCIES,Path(__file__).with_name('metadata-repair-protocol-v1.json')]


def metadata(case):
    route=case['route_spec']
    route['require_bell']=route['from_port']=='A'
    route['via_ports']=[]
    case['generation_rule']['registration_source']=str(Path(__file__).relative_to(previous.HERE.parents[3]))
    return case


def layouts(recipe,interface):return[metadata(c)for c in previous.layouts(recipe,interface)]
def alternatives(case):return[metadata(c)for c in previous.alternatives(case)]
purpose=previous.purpose


def for_exact_request(spec,interface=0):
    response=previous.for_exact_request(spec,interface)
    if 'cases'in response:response['cases']=[metadata(c)for c in response['cases']]
    return response
