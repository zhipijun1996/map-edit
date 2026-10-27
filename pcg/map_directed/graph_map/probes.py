"""Actual full-world reverse/one-shot bypass attempts, with expected blocking.

A failed goal alone is not success: the real actor must reach the tested
passage, push against its actual collider, remain alive, and acquire no reward
from the return side. All cases begin at the Map's original entrance.
"""
import argparse,copy,json,math
from pathlib import Path
from .engine import GraphMapEngine
from ..director import REPO
from ..run import write
from ..r2_full.orchestrate import make_case,path_to,state_after
from ..direct_join.assemble import assemble_modules
from pcg.prototype.workshop.production_loop import compile_request


def create(c,parent_modules):
    g=c['exploration_graph'];parents=[compile_request(dict(recipe='map-owned-supports/v1',module=m))['modules'][0]for m in parent_modules]
    raw=assemble_modules(g,parents,[dict(id=e['id'],kind='side')for e in g['edges']]);out=[]
    for e in g['edges']:
        if e['bidirectional']:continue
        gate=next(q for q in c['gate_specs']if q['edge_id']==e['id']);to=e['to'];fr=e['from'];route_graph=copy.deepcopy(g)
        if to in g.get('core_nodes',[]):route_graph['edges']=[q for q in g['edges']if q['from']in g['core_nodes']and q['to']in g['core_nodes']]
        state=state_after(g,(g['entry'],frozenset(g['initial_abilities']),frozenset()),g['entry']);path,_,_=path_to(route_graph,state,to);incoming=path[-1]['edge_id']if path else c['nodes'][to]['center_port'];approach=[]
        if incoming!=e['id']:approach=copy.deepcopy(raw['nodes'][to]['port_transitions'][incoming+'>'+e['id']])
        goal=copy.deepcopy(c['nodes'][fr]['ports'][e['id']]['target']);protected=[s['id']for s in c['case']['reward_sites']if s.get('allocation',{}).get('node')==fr and s.get('reward_kind')in ['major_item','hidden_collectible']]if to in g.get('core_nodes',[])else[]
        for strategy in ['ground','vertical-shot','diagonal-shot']:
            case=make_case(c,path,'reverse-'+e['id']+'-'+strategy);prefix_count=len(case['pilot_program'])
            for i,v in enumerate(approach):v.update(id='counter-approach-'+e['id']+'-'+str(i),edge_id='adversarial-approach',budget_ticks=min(900,int(v.get('budget_ticks',360))));case['pilot_program'].append(v)
            direction=-gate['direction'][0];plan=[dict(op='axis',value=direction,trigger=dict(after=0))]
            if strategy!='ground':plan += [dict(op='jump',trigger=dict(after=0)),dict(op='shoot',direction=[0,1]if strategy=='vertical-shot'else[gate['direction'][0]*.6,.8],trigger=dict(after=10)),dict(op='jump_release',trigger=dict(after=26))]
            plan.append(dict(op='settle',target_x=goal['position'][0],deadband=3,trigger=dict(after=0)))
            attack='counter-attempt-'+e['id'];case['pilot_program'].append(dict(id=attack,kind='module',edge_id='adversarial-reverse',target=goal,control_plan=plan,budget_ticks=360))
            case.update(goal=goal['region'],exit_port=goal['position'],extra_script=str(REPO/'pcg/map_directed/graph_map/extra.gd'),required_reward_ids=[],required_bosses=[],reward_flag_requirements=c['reward_flag_requirements'],map_budget_ticks=18000,automatic_shop_input=False,map_seed=g['seed'],title='实际整图 · 单向回程反向/一枪绕过探针')
            for n in case['r2_semantics']['nodes']:n['visit_targets']=[p['target']for p in c['nodes'][n['id']]['ports'].values()]
            case['gate_probe']=dict(edge=e['id'],gate=copy.deepcopy(gate),strategy=strategy,prefix_legs=prefix_count,attack_id=attack,protected_reward_ids=protected,goal=goal,actor_body=[24,36],expected='blocked; never call an unattempted failed goal a pass')
            out.append(case)
    return out


def evaluate(case,result):
    q=case['gate_probe'];frames=result.get('frames',[]);legs=result.get('pilot',{}).get('legs',[]);prefix_ids={v['id']for v in case['pilot_program'][:q['prefix_legs']]};complete={v['id']for v in legs if v.get('ok')};prefix_ok=prefix_ids<=complete
    end=max((v['end']['frame']for v in legs if v['id']in prefix_ids and v.get('ok')),default=10**9);post=[f for f in frames if f['frame']>=end];attack=[f for f in post if f.get('pilot',{}).get('input_leg_id')==q['attack_id']]
    x,y,w,h=q['gate']['bounds'];nx,ny=q['gate']['direction'];cx,cy=x+w/2,y+h/2
    sign=lambda f:(f['x']-cx)*nx+(f['y']-cy)*ny
    crossed=any(sign(f)<-12 for f in attack);contact=any(abs(sign(f)-(12+w/2))<2 and y-18<f['y']<y+h+18 and f.get('axis',0)*nx<0 and abs(f.get('real_velocity',[1,1])[0])<.2 for f in post)
    gx,gy,gw,gh=q['goal']['region'];wrong_goal=any(gx<=f['x']<=gx+gw and gy<=f['y']<=gy+gh and f['grounded']for f in post)
    actual=result.get('extra',{});earned={str(e['id'])for e in actual.get('typed_events',[])if e.get('accepted')};stolen=sorted(earned&set(q['protected_reward_ids']));safe=bool(post)and all(f.get('actor_epoch',1)==1 and not f.get('dead',False)and f.get('hp',0)>0 for f in post)
    passed=prefix_ok and safe and contact and len(attack)>=300 and not crossed and not wrong_goal and not stolen
    return dict(passed=passed,status='blocked_at_actual_shutter'if passed else'bypass_or_cheap_reward_found'if crossed or wrong_goal or stolen else'inconclusive',prefix_completed=prefix_ok,actual_gate_contact=contact,wrong_side_crossed=crossed,wrong_side_dock_reached=wrong_goal,unearned_reward_ids=stolen,alive_same_actor_epoch=safe,attack_frames=len(attack),goal_physics_passed=result.get('ok'),goal_failure=result.get('reason'),scope='Finite real Router strategies, not a universal inability proof')


def run(name,source,parent):
    out=REPO/'pcg/results'/name;out.mkdir(exist_ok=False);c=json.loads((REPO/source/'compiled.json').read_text());ms=json.loads((REPO/parent/'precanonical.json').read_text())['modules'];cases=create(c,ms);write(out/'cases.json',dict(cases=cases));write(out/'protocol.json',dict(source=source,parent=parent,strategies=['ground','vertical-shot','diagonal-shot'],world_resets_within_attempt=0,player_teleports=0,expected_result='Actual passage contact and failed reverse traversal, with no cheap reward',production_admitted=False));rows=[];engine=GraphMapEngine(out/'physics')
    for case,r,e in engine.run(cases,'actual-world-oneway-counters'):
        row=dict(id=case['id'],**evaluate(case,r),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps({k:row[k]for k in ['id','passed','status','actual_gate_contact','wrong_side_crossed','unearned_reward_ids']}),flush=True)
    write(out/'summary.json',dict(passed=sum(r['passed']for r in rows),total=len(cases),bypasses=sum(r['status']=='bypass_or_cheap_reward_found'for r in rows),inconclusive=sum(r['status']=='inconclusive'for r in rows),rows=rows,production_admitted=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--source',required=True);p.add_argument('--parent',required=True);a=p.parse_args();run(a.name,a.source,a.parent)
