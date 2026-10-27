from pathlib import Path
from . import rules_v1 as old
HERE=Path(__file__).parent
RECIPES=old.RECIPES
RUNNER_SCRIPT=old.RUNNER_SCRIPT
NATIVE_SCENE=old.NATIVE_SCENE
SOURCE_DEPENDENCIES=[*old.SOURCE_DEPENDENCIES,Path(__file__),HERE/'protocol-v2.json']
purpose=old.purpose

def candidate(control=0,route='loop'):
 c=old.candidate(control,route);c['id']=c['id'].replace('-v1-','-v2-');c['generation_rule']['version']=2;c['generation_rule']['source_path']=str(Path(__file__).relative_to(HERE.parents[3]))
 for s in c['control_plan']:
  if s.get('trigger',{}).get('dynamic',{}).get('kind')=='actor_x':s['trigger']['timeout']=max(s['trigger']['timeout'],475)
 c['rule_parameters']['actor_x_timeout']=475
 return c

def margin(c,r):
 fs=r.get('frames',[]);checks=[]
 for label,rect,support in [('L',c['latches'][0]['gate'],'PairGateA_fold-pair'),('island',c['platforms'][1],'Platform1'),('pillar',c['platforms'][2],'Platform2'),('R',c['latches'][0]['paired_gate'],'PairGateB_fold-pair')]:
  f=next((f for f in fs if f.get('grounded')and f.get('support_id')==support),None)
  if not f:return dict(eligible=False,score=None,missing_stage=label)
  checks.append(dict(stage=label,frame=f['frame'],x=f['x'],left=f['x']-12-rect[0],right=rect[0]+rect[2]-f['x']-12))
 score=min(min(s['left'],s['right'])for s in checks)
 return dict(eligible=purpose(c,r)['ok']and score>=0,score=score,stages=checks)
