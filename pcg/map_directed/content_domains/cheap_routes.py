"""Limited low-cost whole-Map alternatives; reaching the exit is the objective."""
import argparse,copy,json
from .engine import ContentEngine
from ..director import REPO
from ..run import write
from pcg.prototype.workshop.rules import cmd,settle


def run(name,source):
    out=REPO/'pcg/results'/name;parent=REPO/source
    if out.exists():raise ValueError('immutable_cheap_route_probe')
    out.mkdir();c=json.loads((parent/'compiled.json').read_text());base=json.loads((parent/'cases.json').read_text())['cases'][0];goal=c['nodes'][c['exploration_graph']['goal']]['center'];direction=1 if goal['position'][0]>base['spawn'][0]else-1;cs=[]
    for label,jumping in [('walk-and-gravity',False),('jump-without-shooting',True)]:
        v=copy.deepcopy(base);plan=[cmd('axis',value=direction)]
        if jumping:
            for i in range(24):plan +=[cmd('jump'),cmd('jump_release',8),cmd('wait',30)]
        plan.append(settle(goal['position'][0],1));v.update(id='cheap-exit/'+label,pilot_program=[dict(id='blind-exit-policy',edge_id='counterexample',kind='module',target=goal,control_plan=plan,budget_ticks=3600)],map_budget_ticks=3600,noise={},required_reward_ids=[],reward_claim_limit=3,maximum_coins=54)
        v['r2_semantics']['required_nodes']=[c['exploration_graph']['goal']];v['r2_semantics']['required_rewards']=[];v['r2_semantics']['logical_route']=[];cs.append(v)
    write(out/'cases.json',dict(cases=cs));write(out/'protocol.json',dict(parent=source,goal='same regional exit; no mandatory route words or rewards',scope='Two bounded alternatives only, not a proof of all door/ability-lock necessity'));rows=[];engine=ContentEngine(out/'physics');engine.batch_size=2
    for case,result,evidence in engine.run(cs,'limited-cheap-exit-policies'):
        row=dict(id=case['id'],found_shortcut=result['ok'],reason=result['reason'],ticks=result.get('ticks'),goal_reached=result.get('goal_reached'),failure=result.get('pilot',{}).get('failure'),evidence=evidence);rows.append(row);write(out/'rows.json',rows);print(json.dumps(row),flush=True)
    write(out/'summary.json',dict(shortcuts_found=sum(r['found_shortcut']for r in rows),attempts=len(rows),rows=rows,scope='Limited finite counterexamples; no universal no-path guarantee'))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--source',required=True);a=p.parse_args();run(a.name,a.source)
