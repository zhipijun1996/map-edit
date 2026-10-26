"""C01 control repair: keep approaching the newly created landing support."""
from pathlib import Path
from . import rules_v1 as old
from pcg.prototype.workshop.rules import cmd,wait_x
HERE=Path(__file__).parent
RECIPES=old.RECIPES
RUNNER_SCRIPT=old.RUNNER_SCRIPT
NATIVE_SCENE=old.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(old.__file__),*old.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json']
purpose=old.purpose
def candidate(interface=0,control=0):
 c=old.candidate(interface,control)
 c['id']=c['id'].replace('v1','v2')
 c['control_plan'][5:7]=[wait_x(970),cmd('axis',value=0)]
 c['generation_rule']['version']=2;c['generation_rule']['source_path']=str(Path(__file__).relative_to(HERE.parents[3]))
 return c
