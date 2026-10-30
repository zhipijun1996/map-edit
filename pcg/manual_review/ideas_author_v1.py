"""Observed outcomes and actual legal TOP Port mouth; no physics/resource writes."""
from pathlib import Path
from .first40_author_v2 import purpose as base
RUNNER_SCRIPT=Path(__file__).parent/'runtime/ideas_runner_v1.gd'
SOURCE_DEPENDENCIES=[Path(__file__).with_name('first40_author_v2.py'),Path(__file__).with_name('ideas_content_v1.py'),Path(__file__).parents[1]/'prototype/creative_batches/batch30_blockn25/install_v1.gd',Path(__file__).parents[1]/'prototype/creative_batches/batch30_blockn25/loop_definition_v1.gd']
def purpose(case,raw):
 q=base(case,raw);b=case['approved_implementation']['rectangle'];outside=[]
 for f in raw.get('frames',[]):
  inside=b['x']-.05<=f['x']-12 and f['x']+12<=b['x']+b['w']+.05 and b['y']-.05<=f['y']-18 and f['y']+18<=b['y']+b['h']+.05
  mouth=any(p['id']in [case['route_spec']['from_port'],case['route_spec']['to_port']]and p['face']=='TOP'and p['surface']=='ONE_WAY_PLATFORM'and abs(f['x']-p['position'][0])+12<=32.05 and b['y']-128<=f['y']-18 and f['y']+18<=b['y']+b['h']for p in case.get('legal_port_mouths',[]))
  if not inside and not mouth:outside.append(f['frame'])
 if not outside:q['reasons']=[r for r in q['reasons']if r!='actual_body_outside_approved_rectangle']
 q['causal']['outsideFrames']=outside
 q['causal']['airborneEnemyHits']=[e for e in raw.get('plains',{}).get('events',[])if e.get('type')=='enemy_hit'and e.get('fired_airborne')and e.get('player_airborne')]
 # Planned hit sequence is a demonstration, not an exclusion of real alternatives.
 q['causal']['nominalDistinctHitIds']=sorted({e['id']for e in q['causal']['airborneEnemyHits']})
 q['ok']=not q['reasons'];return q
