"""Explicit impact-driven outer revision; old failed16cases remain immutable."""
from pathlib import Path
from pcg.prototype.creative_batches.batch30_blockn02 import rules_v2 as source
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=source.RECIPES;RUNNER_SCRIPT=source.RUNNER_SCRIPT
NATIVE_SCENE='res://prototype/creative_batches/batch30_blockn02_repair/main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(source.__file__),*source.SOURCE_DEPENDENCIES,HERE/'protocol-v1.json',HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_blockn02/probe-receipt-v1.json']

def candidate(interface=0,control=0,route='high'):
 c=source.candidate(interface,control,route);c['latches'][0]['bell']=[832,476]
 c['id']=c['id'].replace('b30-blockn02-v2','b30-blockn02-receiver-v1')
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites','block_grid','block_ports']})
 c['rule_parameters'].update(receiver_corridor=[812,360,128,144],active_static_bell=[832,476],source_cycle='N02failed2rules16cases',repair_cycle='explicitactualimpact_receivercorridor')
 c['generation_rule']=dict(id='batch30/blockN02-receiver-corridor',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'],not_new_family=True)
 c['native_scene']=NATIVE_SCENE;c['native_block_scene']=str((HERE/'main_v1.tscn').relative_to(HERE.parents[3]))
 c['map_specification']=source.old.specification(c)
 return c

purpose=source.purpose
