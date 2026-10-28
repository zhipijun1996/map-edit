"""Unchanged N16 world, final reachable preparation threshold."""
from pathlib import Path
from . import rules_v1 as source
HERE=Path(__file__).parent
RECIPES=source.RECIPES;RUNNER_SCRIPT=source.RUNNER_SCRIPT;NATIVE_SCENE=source.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(source.__file__),*source.SOURCE_DEPENDENCIES,Path(__file__),HERE/'revision-v2.json']
def metadata(c):
 c['id']=c['id'].replace('blockn16-v1','blockn16-v2')
 if c['rule_parameters']['launch']==596:c['control_plan'][1]['trigger']['dynamic']['value']=592
 c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 c['rule_parameters']['preparation_trigger']=592 if c['rule_parameters']['launch']==596 else c['rule_parameters']['launch']
 c['rule_parameters']['new_family']=False
 c['map_specification']['objective']['new_family']=False
 c['map_specification']['objective']['family_interpretation']='Existingdirectionalrecoiladaptation, wallprojectionoptionalrealobservation. Detached1gun/1jumpallowed.'
 return c
def candidate(launch=596,hold=20):return metadata(source.candidate(launch,hold))
purpose=source.purpose
observations=source.observations
