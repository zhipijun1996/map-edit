"""D04 new bounded geometry: eastward reward bank, original Cell mechanics."""
import copy
from pathlib import Path
from pcg.prototype.creative_batches.batch30_d04 import api_v3 as old
from pcg.prototype.creative_batches.batch30_d04 import adaptive_counters_v1 as adaptive
from pcg.prototype.workshop.rules import cmd, ground, settle
from pcg.prototype.factory.core.quality import digest

HERE=Path(__file__).parent
SOURCE_DEPENDENCIES=[Path(old.__file__),Path(adaptive.__file__),HERE/'protocol-v1.json',HERE.parents[2]/'creative-production/batch30/protocol-v7.json']+old.SOURCE_DEPENDENCIES
RECIPES=('park-for-return-repaired',)


def transform(case, extension=160, top=None, tail=True):
    c=copy.deepcopy(case)
    dx=c['interface']*30
    c['platforms'][3][0]+=extension
    if top is not None:c['platforms'][3][1]=top
    for port in c['ports']:
        if port['id']=='C':port['position']=[port['position'][0]+extension,c['platforms'][3][1]-18]
    site=c['reward_sites'][0]
    site['position']=[site['position'][0]+extension,c['platforms'][3][1]-18]
    site['region']=[site['region'][0]+extension,c['platforms'][3][1]-23,site['region'][2],site['region'][3]]
    for q in c['control_plan']:
        dyn=q.get('trigger',{}).get('dynamic',{})
        if dyn.get('kind')=='actor_x' and dyn.get('value') in [1110+dx-4,1060+dx]:dyn['value']+=extension
        if q.get('op')=='settle' and q.get('target_x')==1110+dx:q['target_x']+=extension
    if c['route_spec']['to_port']=='C':
        endpoint=next(p['position']for p in c['ports']if p['id']=='C')
        c['exit_port']=endpoint
        c['goal']=[endpoint[0]-25,endpoint[1]-4,50,8]
    if tail and c['rule_parameters']['route']=='reward-return' and len(c['control_plan'])==64:
        p=c['control_plan']
        p[52:57]=[settle(300,0),cmd('wait',30),cmd('axis',value=0),ground(),cmd('wait',8)]
    c['id']=c['id'].replace('b30-d04-api3','b30-d04r2-v1')
    c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites']})
    c['rule_parameters']['geometry_repair']=dict(extension=extension,reward_top=c['platforms'][3][1],tail_feedback=tail)
    c['production_recipe']=RECIPES[0]
    c['generation_rule']=dict(id='batch30/D04r2',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
    return c


def cases(interface=0):
    return [transform(c)for c in old.layouts(old.RECIPES[0],interface)+old.fixtures(interface)]


def counters(interface=0):
    return [transform(c)for c in adaptive.cases(interface)]


purpose=old.purpose
task_outcome=old.fixture_task_outcome
