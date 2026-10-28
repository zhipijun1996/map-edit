"""Metadata-only semantic repair; all actual controls/geometry/purpose frozen."""
from pathlib import Path
from . import api_v1 as previous
from .counter_policy_v2 import classify as COUNTER_CLASSIFIER
HERE=Path(__file__).parent
RECIPES=previous.RECIPES;RUNNER_SCRIPT=previous.RUNNER_SCRIPT;NATIVE_SCENE=previous.NATIVE_SCENE
PRELIMINARY_QUALITY=previous.PRELIMINARY_QUALITY
SOURCE_DEPENDENCIES=[Path(previous.__file__),*previous.SOURCE_DEPENDENCIES,HERE/'counter_policy_v2.py',HERE/'semantic-repair-protocol-v1.json']
alternatives=previous.alternatives
purpose=previous.purpose


def bind(c):
    c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
    c['generation_rule']['semantic_metadata_revision']='outside-owned-policy-preserving-active-P2-core remainsnotaccepted; notP2bypass'
    return c


def layouts(recipe,interface):return[bind(c)for c in previous.layouts(recipe,interface)]


def candidate_for_request(spec,interface=0):
    result=previous.candidate_for_request(spec,interface)
    if 'cases'in result:result['cases']=[bind(c)for c in result['cases']]
    return result
