import json
from pathlib import Path
from . import active_world_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.rules import cmd
HERE=Path(__file__).parent
def main():
 c=rules.materialize(1,0);c['id']+='-counter-reopen-primary-after-new-jump';c['counterexample_kind']='reopen-primary-after-new-jump'
 c['control_plan'] += [cmd('jump'),cmd('jump_release',12),cmd('shoot',aim_cell=dict(kind='bell',id='relay')),cmd('wait',180)]
 e=WorkshopEngine(ROOT/'results/workshop-batch30-c04-newside-air-v1',extra_sources=[Path(__file__),Path(rules.__file__),HERE/'newside-air-counter-protocol-v1.json']+rules.SOURCE_DEPENDENCIES,runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run([c],'newside-air'):
  row=dict(id=c['id'],purpose=rules.purpose(c,r),ok=r.get('ok'),hp=r.get('hp'),reason=r.get('reason'),coins=r.get('workshop',{}).get('coins'),actual_pair=r.get('workshop',{}).get('paired_gates'),actual_cover=r.get('workshop',{}).get('cover'),player_damage=r.get('plains',{}).get('player_damage'),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'counter-result.json',dict(actual_cases=e.sim.cases,rows=rows))
if __name__=='__main__':main()
