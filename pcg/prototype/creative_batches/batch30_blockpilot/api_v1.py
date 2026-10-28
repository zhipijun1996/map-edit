"""Frozen Block-native production registration over original C02 semantics."""
import copy
from pathlib import Path
from . import rules_v2 as rules

HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES]

def layouts(recipe,interface):
    cs=rules.layouts(recipe,interface)
    for c in cs:c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
    return cs

def purpose(c,r):return rules.purpose(c,r)

def alternatives(c):
    out=rules.alternatives(c)
    for v in out:
        # The reward suffix belongs to the nominal identity, before -counter-.
        # Preserve one-to-one linkage for the original producer's decision map.
        v['id']=c['id']+'-counter-'+v['counterexample_kind']
        v['map_specification']=copy.deepcopy(c['map_specification'])
        for key in ['source_map_request','map_request_response']:
            if key in c:v[key]=copy.deepcopy(c[key])
    assert len({v['id']for v in out})==len(out)
    return out
