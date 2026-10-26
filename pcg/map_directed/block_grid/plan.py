"""Policy compiler over R2, with explicit unsupported-content requests."""
import argparse,copy,json,random
from pathlib import Path
from .policy import load,review,demands
from ..director import REPO,regional
from ..run import write
from pcg.prototype.workshop.production_loop import compile_request

def allocate(g,seed):
    rng=random.Random(seed);branches=g['branches'];sites=[]
    def add(node,kind,**kw):sites.append(dict(id='allocation-'+str(len(sites)),node=node,kind=kind,value=None,materialized=False,**kw))
    ordered=sorted(branches,key=lambda b:(len(b['nodes']),g['nodes'].index(next(n for n in g['nodes']if n['id']==b['reward']))))
    high={b['reward']for b in ordered[-2:]}
    for b in branches:add(b['reward'],'major_item',high_value=b['reward']in high,branch=b['id'],extra_cost_proxy=len(b['nodes']),value_basis='risk/depth proxy; actual module time and balance UNKNOWN')
    order=list(dict.fromkeys([g['entry']]+[n for p in regional.approach_routes(g)for n in p['nodes']]+[n['id']for n in g['nodes']if n['role']=='challenge']))
    for node in order[:12]:add(node,'currency',high_value=False)
    for node in g['landmarks'][:3]:add(node,'recovery')
    add(g['landmarks'][1],'shop')
    for b in ordered[-2:]:add(b['reward'],'hidden_collectible')
    # Legacy scalar is a graph weight, never another physical reward source.
    for n in g['nodes']:n['reward']=0
    g['reward_allocations']=sites

def run(name,seed,policy_path=None):
    p=load(policy_path)if policy_path else load();out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_block_plan_exists')
    out.mkdir(parents=True);attempts=[];selected=None
    for i in range(8):
        try:
            g=regional.construct(seed+'/design-'+str(i),p['region'],20,reward_expeditions=6,
                reward_return_modes=['foldback','loop_back','merge']*2,core_edge_factor=1.05,approach_steps=(7,14),reuse_perimeter_anchors=True)
            g.update(seed=seed,region=p['region']);allocate(g,seed);audit=review(g,p)
            attempts.append(dict(attempt=i,errors=audit['errors'],module_count=len(g['nodes']),unknown=audit['unknown']))
            if audit['ok']:selected=(g,audit);break
        except ValueError as e:attempts.append(dict(attempt=i,error=str(e)))
    write(out/'design-attempts.json',attempts);write(out/'policy.json',p)
    if not selected:
        write(out/'summary.json',dict(status='unsatisfied_within_design_budget',physics='NOT_RUN',may_delete_required_routes=False,production_admitted=False));return out
    g,audit=selected;requests=demands(g,p);write(out/'exploration.json',g);write(out/'challenge-specifications.json',requests);write(out/'policy-review.json',audit)
    # Original Workshop entry handles unregistered capabilities/mechanics by
    # needs_design, rather than inventing equivalent-looking content.
    gaps=[]
    for s in requests:
        recipe='block-native-'+s['objective']['roles'][0]
        response=compile_request(dict(recipe=recipe,specifications=[s]))
        gaps.append(dict(request=s['id'],recipe=recipe,status=response['status'],gaps=response.get('gaps',[]),required_ports=s['ports']['count']))
    write(out/'generator-feedback.json',gaps)
    write(out/'summary.json',dict(status='logical_targets_satisfied_content_pending',modules=len(g['nodes']),branches=len(g['branches']),
        return_kinds=sorted({b['kind']for b in g['branches']}),principal_routes=len(audit['routes']),physics='NOT_RUN',
        production_admitted=False,scope='Actual R2 logical design only; no abstract layout or Module success claimed'))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--seed',required=True);a=p.parse_args();print(run(a.name,a.seed))
