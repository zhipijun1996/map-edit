"""Frozen registration of exact east160 D04 geometry, not a new mechanism."""
import copy
from pathlib import Path
from pcg.prototype.creative_batches.batch30_d04 import api_v3 as old
from . import rules_v1 as rules
from . import counter_rules_v1 as strong

HERE=Path(__file__).parent
RECIPES=rules.RECIPES
CALIBRATION_SEED=261030001
HOLDOUT_SEED=261030002
SOURCE_DEPENDENCIES=[Path(rules.__file__),Path(strong.__file__),HERE/'protocol-v1.json',HERE/'protocol-v2.json',HERE/'protocol-v3.json']+rules.SOURCE_DEPENDENCIES


def specification(interface,cases):
    s=old.specification(interface,cases)
    s['id']=f'batch30/D04r2/{interface}'
    s['required_family']=RECIPES[0]
    s['objective']['recipe']=RECIPES[0]
    s['objective']['core']='outgoing recoil leaves carrier at middle for direct return or east for wider-gap reward transfer; exact bank shifted160 east after dominating old shortcut'
    s['objective']['prior_design_refutation']='old D04 middle park gave faster C chest without any actual carrier support; old versions held, not counted as repaired'
    s['objective']['supported_geometry_parameters']=dict(reward_bank_east_shift=160,reward_bank_top=650)
    s['objective']['continuity_fixture_scope']='Two exact continuous A-return fixture programs, no Module self-loops. Root fullcal+newheld must qualify them independently.'
    s['return_conditions']='Declared forward routes do not automatically validate return. Same-world fixtures exported separately and do not create extra ports.'
    return s


def layouts(recipe,interface):
    if recipe not in RECIPES or interface not in [0,1]:raise ValueError('Unsupported repaired D04 recipe/interface')
    cs=rules.cases(interface)[:2]
    for c in cs:c['family']=RECIPES[0]
    s=specification(interface,cs)
    for c in cs:c['map_specification']=copy.deepcopy(s)
    return cs


def fixtures(interface):
    cs=rules.cases(interface)[2:]
    for c in cs:c['family']=RECIPES[0]
    return cs


def purpose(c,r):return old.purpose(c,r)


def alternatives(c):
    out=old.alternatives(c)
    if c['route_spec']['to_port']=='C':
        for v in strong.extra(c['interface']):
            # A deliberate different park is a candidate policy in the SAME
            # initial world. Compare its actual task result, not nominal park.
            # Keep its own required middle park, so the root comparator can
            # observe that state rather than silently rejecting it for not
            # leaving the author's east park. Missing carrier use is checked
            # only after actual C reward/safety/capability success.
            v['id']=c['id']+'-counter-'+v['counterexample_kind']
            v['family']=c['family']
            v['map_specification']=copy.deepcopy(c['map_specification'])
            out.append(v)
    return out


def adaptive_counters(interface):
    return rules.counters(interface)


def fixture_task_outcome(c,r):return old.fixture_task_outcome(c,r)
