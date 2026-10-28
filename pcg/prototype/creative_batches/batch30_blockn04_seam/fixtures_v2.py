"""Input-only repair: wait for the real left dock before retargeting feedback."""
from pathlib import Path
from . import fixtures_v1 as prior
from pcg.prototype.workshop.rules import wait_x
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json']
purpose=prior.purpose
def fixture():
 c=prior.fixture(1);plan=[];inserted=0
 for q in c['control_plan']:
  plan.append(q)
  if q.get('op')=='settle'and q.get('target_x')==1256:plan.append(wait_x(1249));inserted+=1
 assert inserted==1
 c['control_plan']=plan;c['id']='b30-N04-exact-seam-v2-c2';c['seam_specimen']['control']=2
 c['seam_specimen']['fixture_version']='sha256:'+digest(dict(source=c['seam_specimen']['source_contentVersion'],translation=c['seam_specimen']['translation_right'],platforms=c['platforms'],latches=c['latches'],rewards=c['reward_sites'],owned=c['block_grid'],control=plan))
 return c
