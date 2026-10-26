"""Four bounded enemy-world recipes adapted to explicit plains spatial demands.

Uses original native Cells, quality policy and production loop. No new physics.
"""
from pathlib import Path
import copy
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.rules import cmd
from pcg.prototype.creative_batches.enemy_world import production_v7 as attack
from pcg.prototype.creative_batches.enemy_world import production_v2 as clear
from pcg.prototype.creative_batches.enemy_world import production_v6 as displace
from pcg.prototype.creative_batches.occupancy import production_v2 as occupancy
HERE=Path(__file__).parent
OLD=HERE.parent/'enemy_world';OCC=HERE.parent/'occupancy'
RECIPES=['attack-relay','clear-sightline','live-enemy-sensor','displace-landing']
BASES={'attack-relay':attack,'clear-sightline':clear,'live-enemy-sensor':occupancy,'displace-landing':displace}
DEMANDS={
 'attack-relay':[dict(entry_x=50,exit_x=460,floor_width=850,ceiling_width=400),dict(entry_x=110,exit_x=520,floor_width=980,ceiling_width=470)],
 'clear-sightline':[dict(entry_x=90,exit_x=480,bell_x=245,gate_x=320,floor_width=850),dict(entry_x=90,exit_x=560,bell_x=265,gate_x=355,floor_width=1000)],
 'live-enemy-sensor':[dict(entry_x=60,exit_x=620,floor_width=1040),dict(entry_x=100,exit_x=720,floor_width=1200)],
 'displace-landing':[dict(entry_x=170,entry_y=190,exit_x=208,entry_bank_width=350),dict(entry_x=170,entry_y=240,exit_x=208,entry_bank_width=350)]}

def compiler(request):
 recipe=request['recipe']
 if recipe not in RECIPES:return dict(status='needs_design',gaps=['unsupported enemy causal rule'],cases=[])
 response=BASES[recipe].compiler(dict(recipe=recipe))
 specs=[];cases=[]
 for interface in request.get('interfaces',[0,1]):
  d=DEMANDS[recipe][interface];s=copy.deepcopy(response['specifications'][0]);s['id']=f'plains50/enemy/{recipe}/d{interface}'
  s['objective']['spatial_demand']=d;s['objective']['source_relationship']='existing family, demand adaptation not new family';s['objective']['campaign']='plains50-v1'
  s['space'].update(max_width=1500,max_height=1000);s['budget']['generator_candidates']=4
  s['entry_y']=d.get('entry_y',420);s['rise']=s['entry_y']-420;s['return_conditions']='UNKNOWN';specs.append(s)
  source=response['cases'][:4]
  for index,old in enumerate(source):
   c=copy.deepcopy(old);c['id']=f'p50-enemy-{recipe}-d{interface}-c{index}';c['map_specification']=copy.deepcopy(s);c['idea_ids']=[f'plains50/enemy/{recipe}'];c['production_recipe']=recipe
   c['spawn']=[d['entry_x'],d.get('entry_y',420)];c['entry_port']=c['spawn'][:]
   oldexit=c['exit_port'][0];c['exit_port']=[d['exit_x'],420];c['goal']=[d['exit_x']-8,416,16,8]
   for reward in c['reward_sites']:reward['position']=[d['exit_x'],420]
   for step in c['control_plan']:
    if step.get('op')=='settle'and step.get('target_x')==oldexit:step['target_x']=d['exit_x']
   if recipe=='attack-relay':
    c['platforms'][0][2]=d['floor_width'];c['platforms'][2][2]=d['ceiling_width']
   elif recipe=='clear-sightline':
    c['platforms'][0][2]=d['floor_width'];c['platforms'][1][2]=d['floor_width'];c['latches'][0]['bell'][0]=d['bell_x'];c['latches'][0]['gate'][0]=d['gate_x']
   elif recipe=='live-enemy-sensor':c['platforms'][0][2]=d['floor_width']
   elif recipe=='displace-landing':c['platforms'][0][1]=d['entry_y']+18
   c['rule_parameters']={'spatial_demand':d,'existing_relationship':recipe,'campaign':'plains50-v1','interface':interface,'control_choice':index}
   c['generation_rule']={'id':'plains50/enemy/'+recipe,'version':1,'source_path':str(Path(__file__).relative_to(ROOT.parent)),'parameters':c['rule_parameters']}
   c['max_frames']=max(c.get('max_frames',420),520);c['trace_all']=False;cases.append(c)
 return dict(status='requires_physics',specifications=specs,cases=cases)

def purpose(c,r):return BASES[c['production_recipe']].purpose(c,r)

def alternatives(c):
 recipe=c['production_recipe'];m=BASES[recipe]
 rows=m.counters(c)if recipe=='clear-sightline'else m.alternatives(c)
 oldtarget={'attack-relay':420,'clear-sightline':450,'live-enemy-sensor':650,'displace-landing':208}[recipe]
 for v in rows:
  for step in v['control_plan']:
   if step.get('op')=='settle'and step.get('target_x')==oldtarget:step['target_x']=c['exit_port'][0]
 return rows

def sources():
 return [Path(__file__)]+[p for folder in [OLD,OCC]for p in folder.iterdir()if p.suffix in ['.py','.gd','.mjs','.tscn']]

def runner(recipe):return OLD/'attack_runner_v1.gd'if recipe=='attack-relay'else OCC/'runner_v1.gd'if recipe=='live-enemy-sensor'else OLD/'runner_v1.gd'
def exporter(recipe):return OLD/'export_v1.mjs'if recipe=='attack-relay'else OCC/'export_v1.mjs'if recipe=='live-enemy-sensor'else None
