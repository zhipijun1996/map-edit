"""Demand binding repair: true reward region, visible relay ingress."""
from pathlib import Path
import copy
from . import rules_v1 as old
from pcg.prototype.workshop.engine import ROOT
HERE=Path(__file__).parent
RECIPES=old.RECIPES
purpose=old.purpose
alternatives=old.alternatives
runner=old.runner
exporter=old.exporter

def compiler(request):
 r=old.compiler(request)
 for s in r['specifications']:
  s['id']+='/r2'
  if request['recipe']=='attack-relay'and s['objective']['spatial_demand']['entry_x']==50:s['objective']['spatial_demand']['entry_x']=80
 for c in r['cases']:
  c['id']=c['id'].replace('p50-enemy-','p50-enemy-r2-');c['map_specification']['id']+='/r2'
  if request['recipe']=='attack-relay'and c['spawn'][0]==50:
   c['spawn'][0]=80;c['entry_port'][0]=80;c['map_specification']['objective']['spatial_demand']['entry_x']=80;c['rule_parameters']['spatial_demand']['entry_x']=80
  for site in c['reward_sites']:
   x,y=site['position'];site['region']=[x-30,y-5,60,10]
  c['generation_rule']['version']=2;c['generation_rule']['source_path']=str(Path(__file__).relative_to(ROOT.parent))
 return r

def sources():return old.sources()+[Path(__file__),HERE/'protocol-v1.json',HERE/'designs-v1.json']
