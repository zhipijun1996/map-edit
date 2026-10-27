"""Entry rock pillar gives the three-way fork its own internal shot boundary."""
from pathlib import Path
from . import rules_v1 as prior
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json',HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_runtime/main_block_v1.gd',HERE.parent/'batch30_runtime/block_draw_v1.gd']

def revised(c):
 before=c['platforms'][0][:];c['platforms'][0][3]=640-c['platforms'][0][1]
 c['latches'][0]['bell']=[345,551]
 c['block_adaptation'].update(revision_kind='new_native_entry_rock_pillar_and_receiver',entry_pillar_before=before,entry_pillar_after=c['platforms'][0][:],bell_before=[278,551],bell_after=[345,551],bounded_terminal_adapter_only=False)
 c['id']=c['id'].replace('block-c06-v1','block-c06-v2')
 c['native_block_scene']=str(NATIVE_SCENE.relative_to(HERE.parents[3]))
 c['native_scene']='res://prototype/creative_batches/batch30_blockc06/main_v1.tscn'
 c['rule_parameters']['launch_x']=348
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['block_adaptation'])
 c['map_specification']['objective']['physical_layout_sha256']=c['layout_uid']
 return c

def layouts(recipe,interface):return[revised(c)for c in prior.layouts(recipe,interface)]

def purpose(c,r):
 q=prior.purpose(c,r)
 # Early airborne shots are genuine alternatives, not failed keystroke orders.
 # The independent complete-body ownership requirement remains unchanged.
 if 'single_shot_falling_choice_missing'in q['reasons']and q['causal']['air_high_openings']:
  shots=[f for f in r.get('frames',[])if not f.get('grounded')and any(e.get('type')=='shot'for e in f.get('accepted',[]))]
  if any(f.get('vy',0)<0 for f in shots):
   q['reasons'].remove('single_shot_falling_choice_missing');q['causal']['legitimate_early_air_recoil_alternative']=True
 q['ok']=not q['reasons'];return q

def alternatives(c):
 original=next(v for v in prior.layouts(RECIPES[0],0)if v['rule_parameters']['route']==c['rule_parameters']['route'])
 return[revised(v)for v in prior.alternatives(original)]
