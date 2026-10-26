"""Correct an over-strong body-position proxy; preserve actual sightline cause.

Early east peek remains valid without the whole body crossing the occluder.
This is not a new family or a relaxed regular/noise policy. Re-run full evidence.
"""
import argparse,copy
from pathlib import Path
from pcg.prototype.creative_batches.plains50_resources import production_v1 as prior
from pcg.prototype.workshop.evaluate import purpose as standard
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.rules import cmd,wait_x,settle
HERE=Path(__file__).parent
RECIPE='sightline-backtrack'

def compiler(request):
 response=prior.compiler(request)
 for c in response['cases']:
  c['id']=c['id'].replace('-c','-r2-c');c['rule_source_path']=str(Path(__file__).relative_to(ROOT.parent));c['generation_rule']['version']=2
  c['purpose_revision']='Require real eastward exposure, actual opening, westward return; do not require whole body beyond screen right edge.'
 return response

def purpose(c,r):
 p=standard(c,r);fs=r.get('frames',[]);ev=r.get('plains',{}).get('events',[]);opens=[x for x in ev if x['type']=='bell_open'];origins=[x for x in ev if x['type']=='shot_origin']
 hit=opens[0]['frame']if opens else None
 entry_x=c['entry_port'][0];fired_east=bool(hit is not None and any(x['frame']<=hit and x['origin'][0]>entry_x+1 for x in origins))
 returned=bool(hit is not None and any(f['frame']>hit and f['x']<c['latches'][0]['gate'][0]for f in fs))
 excursion=max((x['origin'][0]-entry_x for x in origins if hit is not None and x['frame']<=hit),default=None)
 p['causal'].update(real_open=hit,real_shot_origins=origins,east_excursion_at_shot=excursion,west_return_after_open=returned,body_beyond_entire_screen_not_required=True)
 if not(hit is not None and fired_east and returned):p['reasons'].append('east_ray_exposure_real_open_then_west_return_missing')
 p['ok']=not p['reasons'];return p

def alternatives(c):
 out=prior.alternatives(c)
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 q=dict(kind='bell',id='remote-key');target=c['exit_port'][0]
 for hold in [8,20]:
  for delay in [0,6,12,18,24]:add(f'entry-neutral-jump-{hold}-{delay}',[cmd('axis',value=0),cmd('jump'),cmd('jump_release',hold),cmd('shoot',delay,aim_cell=q),settle(target,18)])
 for x in [90,110,130]:
  for delay in [0,8,18]:add(f'shallow-east-ray-{x}-{delay}',[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('shoot',delay,aim_cell=q),settle(target,18)])
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 run(a.name,[dict(recipe=RECIPE)],1,library_root=ROOT/'map_directed/library',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=[HERE/'production_v1.py',HERE/'protocol-v1.json',prior.LEGACY/'runner-v2.gd',prior.LEGACY/'export-v4.mjs'],runner_script=prior.LEGACY/'runner-v2.gd',export_script=prior.LEGACY/'export-v4.mjs')
