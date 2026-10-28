from pathlib import Path
from . import rules_v1 as old
RECIPES=old.RECIPES
RUNNER_SCRIPT=old.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(old.__file__),*old.SOURCE_DEPENDENCIES,Path(__file__).parent/'protocol-v2.json']
purpose=old.purpose

def candidate(interface=0,direction='out',hold=20):
 c=old.candidate(interface,direction,hold)
 c['id']=c['id'].replace('-v1-','-v2-');c['generation_rule']['version']=2
 if direction=='back':c['control_plan'].insert(6,old.original.wait_x(c['moving_platforms'][0]['start'][0]+30,-1))
 return c

def layouts(recipe,interface):
 if recipe!=RECIPES[0]:raise ValueError('outside exact recipe')
 return[candidate(interface,d)for d in ['out','back']]
