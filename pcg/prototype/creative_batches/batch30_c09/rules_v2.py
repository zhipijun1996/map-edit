from pathlib import Path
from . import rules_v1 as prior
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json']
def candidate(interface=0,control=0,route='loop'):
 c=prior.candidate(interface,control,route);c['id']=c['id'].replace('-v1-','-v2-');c['latches'][0]['bell']=[270,1080]
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites']})
 c['generation_rule']=dict(id='batch30/C09',version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 return c
purpose=prior.purpose
