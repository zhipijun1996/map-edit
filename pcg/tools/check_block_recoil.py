"""Real same-world recoil omission checks; finite alternatives, not a bypass proof."""
import argparse,copy,json
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.map_directed.block_grid.engine import BlockEngine

def run(name,source):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_counterfactual_exists')
    out.mkdir();base=json.loads((REPO/source/'cases.json').read_text())['cases'][0];cases=[]
    for hold in [None,24]:
        c=copy.deepcopy(base);c['id']+='-omit-recoil'+('-long-jump'if hold else'')
        for leg in c['pilot_program']:
            for op in leg.get('control_plan',[]):
                if op['op']=='shoot':op['op']='wait';op.pop('direction',None)
                if hold and op['op']=='jump_release':op['trigger']['after']=hold
        cases.append(c)
    write(out/'protocol.json',dict(source=str(source),modified='Only omit shoot inputs; second strategy extends jump hold to24frames',geometry_changed=False,physics_changed=False,resources_reset=False,scope='Two concrete omission strategies. Does not prove impossibility of every unintended gate bypass.'))
    write(out/'cases.json',dict(cases=cases));rows=[]
    for c,r,e in BlockEngine(out/'physics').run(cases,'block-recoil-counterfactual'):
        rows.append(dict(id=c['id'],physics_pass=r['ok'],expectation_met=not r['ok'],reason=r['reason'],ticks=r.get('ticks'),shots=r.get('shots'),failure=r.get('pilot',{}).get('failure'),evidence=e));write(out/'rows.json',rows)
    write(out/'summary.json',dict(expectations_met=len(rows)==2 and all(r['expectation_met']for r in rows),rows=rows,scope='Expected failures retained; excluded from positive holdout totals',production_admitted=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--source',default='pcg/results/block-grid-evaluation-2-v1');a=p.parse_args();run(a.name,a.source)
