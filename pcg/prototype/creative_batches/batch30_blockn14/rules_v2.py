"""Second final geometry: real high-shore catch window, same action domain."""
from pathlib import Path
from . import rules_v1 as source
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=source.RECIPES;RUNNER_SCRIPT=source.RUNNER_SCRIPT;NATIVE_SCENE=source.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(source.__file__),*source.SOURCE_DEPENDENCIES,Path(__file__),HERE/'revision-v2.json']
def candidate(target='B',control=0):
 c=source.candidate(target,control);c['platforms'][2][2]=288;c['platforms'][3]=[736,352,288,96];c['id']=c['id'].replace('blockn14-v1','blockn14-v2')
 c['layout_uid']=digest({k:c.get(k)for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']});c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])));c['rule_parameters']['highshore_extend64']=True;c['map_specification']['objective']['physical_layout_sha256']=c['layout_uid'];return c
purpose=source.purpose
def margin(c,r):
 i=2 if c['rule_parameters']['target']=='B'else 3;rect=c['platforms'][i];f=next((f for f in r.get('frames',[])if f.get('grounded')and f.get('support_id')=='Platform'+str(i)),None)
 if not f:return dict(eligible=False,score=None)
 score=min(f['x']-12-rect[0],rect[0]+rect[2]-f['x']-12)
 return dict(eligible=purpose(c,r)['ok']and score>=0,score=score,first_highshore_support={k:f.get(k)for k in ['frame','x','y','support_id']})
