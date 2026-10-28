import copy,json
from pathlib import Path
from . import api_v1 as rules
from pcg.prototype.workshop.rules import cmd,ground
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.map_directed.block_grid.contracts import raster
HERE=Path(__file__).parent
def main():
 cases=[]
 for c in rules.layouts(rules.RECIPES[0],0)[:2]:
  nominal=copy.deepcopy(c['control_plan']);c['control_plan']=copy.deepcopy(nominal[:7])+[cmd('shoot',direction=[1,0]),ground(),cmd('wait',8)]+nominal
  c['id']+='-missed-shot-retry';c['max_frames']=2400;c['validation_fixture']=dict(kind='wrong_shot_real_floor_renewal_same_world_retry',module_enrollment=False,source_layout_uid=c['layout_uid']);cases.append(c)
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn04-missed-recovery-v1',extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'recovery-protocol-v1.json'],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cases,'same-world-missed-shot-retry'):
  fs=r.get('frames',[]);first=next((f for f in fs if any(x.get('type')=='shot'for x in f.get('accepted',[]))),None);floor=next((f for f in fs if first and f['frame']>first['frame']and f.get('grounded')and f.get('support_id')=='Platform6'),None)
  tail=copy.deepcopy(r);tail['frames']=[f for f in fs if floor and f['frame']>=floor['frame']];q=rules.purpose(c,tail)
  if not floor:q['reasons'].append('missing_actual_failure_floor')
  if floor and floor.get('shot_charges',0)<1:q['reasons'].append('missing_actual_floor_renewal')
  if any(v.get('type')=='bell_open'and floor and v['frame']<=floor['frame']for v in r.get('plains',{}).get('events',[])):q['reasons'].append('intended_wrong_shot_opened_gate')
  owned=set(map(tuple,c['block_grid']['cells']));outside=[f['frame']for f in fs if not raster([f['x']-12,f['y']-18,24,36])<=owned]
  if outside:q['reasons'].append('actual_body_left_frozen_block_reservation')
  q['ok']=not q['reasons'];q['causal'].update(failure_floor_frame=floor['frame']if floor else None,whole_fixture_outside_frames=outside[:12])
  row=dict(id=c['id'],purpose=q,evidence=ev,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']});rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(r['purpose']['ok']for r in rows),rows=rows,scope='Two exact clean failed-shot retries; noisy/general recovery UNKNOWN',new_modules=0))
if __name__=='__main__':main()
