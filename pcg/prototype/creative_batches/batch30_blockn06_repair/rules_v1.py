"""Explicit model geometry repair after the preserved failed N06 cycle."""
from pathlib import Path
from pcg.prototype.creative_batches.batch30_blockn06 import rules_v2 as source
from pcg.prototype.creative_batches.batch30_blockn06 import policy_v1 as policy
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=source.RECIPES;RUNNER_SCRIPT=source.RUNNER_SCRIPT
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(source.__file__),Path(policy.__file__),*policy.SOURCE_DEPENDENCIES,HERE/'protocol-v1.json',HERE/'main_v1.gd',HERE/'main_v1.tscn']

def candidate(target='B',control=0):
 c=source.candidate(target,control)
 assert c['platforms'][1]==[544,608,192,64]and c['latches'][0]['bell']==[800,672]
 c['platforms'][1]=[480,608,256,64];c['latches'][0]['bell']=[800,560]
 c['id']=c['id'].replace('blockn06-v2','blockn06-repair-v1')
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['rule_parameters']['shared_choice_M']=c['platforms'][1][:]
 c['generation_rule']=dict(id='batch30/blockN06/geometry-repair',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=dict(control=control,target=target,parent_failed_cases=52,parent_failed_rules=2,geometry_changes=dict(M=c['platforms'][1],bell=c['latches'][0]['bell']),physical_control_plan_unchanged=True,new_rule_cap=1,lineage_probe_cap=80))
 c['map_specification']['id']='batch30/blockN06/geometry-repair/fork-interface0';c['map_specification']['objective']['physical_layout_sha256']=c['layout_uid']
 c['native_scene']='res://prototype/creative_batches/batch30_blockn06_repair/main_v1.tscn';c['native_block_scene']=str(NATIVE_SCENE.relative_to(HERE.parents[3]))
 return c

purpose=policy.purpose

def support_margin(c,r):
 fs=r.get('frames',[]);m=next((f for f in fs if source.over(f,c['platforms'][1])),None)
 stage=purpose(c,r)['causal'].get('actual_corresponding_bridge_stage');bridge=c['latches'][0]['gate'if c['route_spec']['to_port']=='B'else'paired_gate']
 landed=stage.get('first_landing')if stage else None
 if not m or not landed:return dict(eligible=False,score=None,reason='actualM/correspondingbridgefirstsupportmissing')
 mr=c['platforms'][1];values=dict(M_left=m['x']-12-mr[0],M_right=mr[0]+mr[2]-m['x']-12,bridge_left=landed['x']-12-bridge[0],bridge_right=bridge[0]+bridge[2]-landed['x']-12)
 return dict(eligible=purpose(c,r)['ok'],score=min(values.values()),values=values,first_M={k:m.get(k)for k in ['frame','x','y','support_id']},first_bridge=landed,body_width=24)
