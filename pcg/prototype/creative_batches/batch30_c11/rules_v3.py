from pathlib import Path
from . import rules_v2 as prior
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'protocol-v3.json']
def candidate(interface=0,control=0):
 c=prior.candidate(interface,control)
 if interface==0:return c
 c['id']=f'b30-c11-v3-i1-c{control}';c['latches'][0]['bell']=[480,260]
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites','thorns']})
 c['generation_rule']=dict(id='batch30/C11',version=3,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 return c
purpose=prior.purpose
