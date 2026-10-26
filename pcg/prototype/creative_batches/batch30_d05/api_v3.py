"""Frozen registration: v3 geometry, first clean valid control1 at both demands.

This file selects an already probed option; it adds no new geometry revision.
"""
from pathlib import Path
from . import api_v2 as rules
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=rules.SOURCE_DEPENDENCIES+[Path(rules.__file__)]
CONTROL={0:1,1:1}
def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in CONTROL:raise ValueError('outside frozen D05 demands')
 return [rules.materialize(interface,CONTROL[interface])]
def purpose(c,r):return rules.purpose(c,r)
def alternatives(c):return rules.alternatives(c)
