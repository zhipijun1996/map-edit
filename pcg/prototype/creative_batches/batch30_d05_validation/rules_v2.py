"""Validation control repair: a true missed bell; no core geometry changes."""
from pathlib import Path
from . import rules_v1 as original
HERE=Path(__file__).parent
SOURCE_DEPENDENCIES=original.SOURCE_DEPENDENCIES+[Path(original.__file__),HERE/'protocol-v2.json']
RUNNER_SCRIPT=original.RUNNER_SCRIPT
def fixture(interface=0,control=0):
 c=original.fixture(interface,control);c['id']=c['id'].replace('recovery-v1','recovery-v2');c['control_plan'][9]['direction']=[0,1]
 c['validation_fixture']['wrong_first_shot_direction']=[0,1]
 return c
def purpose(c,r):return original.purpose(c,r)
