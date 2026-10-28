"""Original engine probes of explicit no-currency Map demand adaptation."""
import argparse,json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.factory.core.engine import file_sha

def run(name,interfaces,levels,trials):
    out=ROOT/'results'/name
    if out.exists():raise ValueError('immutable_block_pilot_run')
    e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT)
    bases=[rules.layouts(rules.RECIPES[0],i)[0]for i in interfaces]
    cs=[v for c in bases for level in levels for v in ([c]if level=='clean'else[instantiate(c,261040101,level,j)for j in range(trials)])]
    write(out/'protocol.json',json.loads((Path(__file__).parent/'protocol-v2.json').read_text()))
    write(out/'source-cases.json',dict(cases=cs));rows=[]
    for c,r,v in e.run(cs,'block-no-reward-'+','.join(levels)):
        q=rules.purpose(c,r);rows.append(dict(id=c['id'],purpose=q,evidence=v,result_summary={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},workshop=r.get('workshop')))
        write(out/'rows.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons']),ensure_ascii=False),flush=True)
    write(out/'summary.json',dict(actual_physics_cases=e.sim.cases,passed=sum(x['purpose']['ok']for x in rows),total=len(rows),source_binding_sha256=file_sha(out/'source_binding.json'),full_calibration='NOT_RUN',holdout='NOT_RUN',new_modules=0,production_admitted=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--interfaces',nargs='+',type=int,default=[0,1],choices=[0,1]);p.add_argument('--levels',nargs='+',default=['clean'],choices=['clean','mild','moderate']);p.add_argument('--trials',type=int,default=6);a=p.parse_args();run(a.name,a.interfaces,a.levels,a.trials)
