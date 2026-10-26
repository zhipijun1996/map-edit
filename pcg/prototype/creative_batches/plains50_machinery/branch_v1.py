"""One explicit 3-port carrier/safe-outlet request using root's orchestration."""
import copy,json,sys
from pathlib import Path
from pcg.prototype.workshop.rules import chase,cmd,settle
from pcg.prototype.workshop.evaluate import purpose as original_purpose
from pcg.prototype.workshop.counterexamples import alternatives as original_alternatives
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
HERE=Path(__file__).parent
RECIPES=('carrier-safe-branch',)
PROTOCOL=dict(schema='pcg/plains50-carrier-safe-branch/v1',proposal='carrier-safe-branch',source_revision_max=2,interfaces=1,
    actual_supported_ports=3,ordered_relations=6,routes=['A→B challenge/reward','A→C intentional safe exit'],
    max_actual_physics_cases=400,minimum_counters_per_route=18,calibration_and_holdout_trials_per_level=12,
    quality='original regular unchanged',external_outcome='exact exit plus actual reward for challenge; safe low arrival without reward is not a high-route refutation',
    novelty='A2 branch-interface adaptation, not a new action family',return_conditions='UNKNOWN')

def layouts(recipe,interface):
    if recipe not in RECIPES or interface!=0:raise ValueError('outside one explicit branch demand')
    c=chase(0)
    c['platforms'][1]=[805,288,210,100]
    upper=[905,270];lower=[1030,632]
    c['reward_sites'][0].update(position=upper,region=[875,265,60,10]);c['control_plan'][-1]=settle(905,6)
    c['ports']=[dict(id='A',position=[80,420],normal=[-1,0],support_index=0),dict(id='B',position=upper,normal=[1,0],support_index=1),dict(id='C',position=lower,normal=[1,0],support_index=2)]
    keys=['capabilities','platforms','one_way_platform_indices','wall_platform_indices','hazards','thorns','saws','moving_platforms','hooks','latches','enemies','world_bounds','ports','reward_sites']
    uid=digest(dict(recipe=recipe,physical={k:c.get(k,[])for k in keys}))
    plans=[('reward','B','reward',c['control_plan'],True),('safe-lower-exit','C','main',[cmd('axis',value=1),settle(1030,6)],False)]
    out=[]
    for rid,to,role,plan,challenge in plans:
        v=copy.deepcopy(c);end=next(p for p in c['ports']if p['id']==to)
        v.update(id='plains50-machinery-carrier-safe-branch-'+rid+'-v1',layout_uid=uid,layout_title='追台取宝或下层通行 / 3口',
            spawn=[80,420],entry_port=[80,420],exit_port=end['position'],goal=[end['position'][0]-25,end['position'][1]-4,50,8],
            control_plan=copy.deepcopy(plan),max_frames=1200,trace_all=False,interface=0,challenge_route=challenge,production_recipe=recipe,
            expected_reward=8 if challenge else 0,idea_ids=['plains50-machinery/carrier-safe-branch'])
        v['route_spec']=dict(id=rid,from_port='A',to_port=to,role=role,via_ports=[],require_bell=challenge)
        v['rule_parameters']=dict(relationship='same initial carrier terrain offers high reward interception or intentional lower-risk ground outlet',port_count=3,
            original_family='chase-landing',new_action_family=False,challenge_geometry=[805,288,210,100],safe_outlet=lower,
            directed_routes=['A→B','A→C'],other_directions='UNKNOWN',no_added_seam_geometry=True)
        v['generation_rule']=dict(id='plains50-machinery/carrier-safe-branch',version=1,source_type='actual_current_codex_subagent',author_task='/root/plains50_machinery',parameters=v['rule_parameters'],protocol=PROTOCOL)
        v['rule_source_path']=str(Path(__file__).relative_to(ROOT.parent));out.append(v)
    spec=dict(schema='map-notes/challenge-specification/v1',id='plains50/machinery/carrier-safe-branch/3port/v1',source_type='parent_map_interface_work_order',
        region='plains',required_family='chase-landing',objective=dict(recipe=recipe,physical_layout_sha256=uid,branch_ports=c['ports']),
        capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=3,required_normals=[p['normal']for p in c['ports']]),
        relations=[dict(from_port='A',to_port='B',role='reward',route_id='reward'),dict(from_port='A',to_port='C',role='main',route_id='safe-lower-exit')],
        space=dict(max_width=1900,max_height=1300,max_port_span_x=1300),boundary_policy='open',enclosing_walls=False,
        difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),
        resource_state=dict(reset_between_components=False,entry='authored fresh original supported source A; actual entry snapshot bound',exit='observed stable only'),
        return_conditions='B→A/B→C/C→A/C→B UNKNOWN; no implicit all-to-all connectivity',budget=dict(generator_candidates=1,director_revisions=0))
    for v in out:v['map_specification']=spec
    return out

def purpose(c,r):
    clone=copy.deepcopy(c)
    if not c['challenge_route']:
        clone['family']='safe-branch';clone['route_spec']['id']='recovery';clone['expected_reward']=0
    p=original_purpose(clone,r)
    if r.get('returns'):p['reasons'].append('unexpected_teleport_or_reset')
    p['ok']=not p['reasons'];return p

def alternatives(c):
    out=original_alternatives(c)
    for direction in [-1,1]:
        for delay in [0,8,20]:
            v=copy.deepcopy(c);v['id']+=f'-counter-direct-walk-{direction}-{delay}';v['counterexample_kind']='direct-walk';v['control_plan']=[cmd('axis',value=direction),cmd('wait',after=delay),settle(c['exit_port'][0])];out.append(v)
    return out

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--probe',action='store_true');p.add_argument('--name',required=True);a=p.parse_args()
    if a.probe:
        e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__)]);rows=[]
        for c,r,ev in e.run(layouts(RECIPES[0],0),'branch-probe'):
            q=purpose(c,r);rows.append(dict(id=c['id'],ok=q['ok'],purpose=q,evidence=ev));print(c['id'],r.get('reason'),q,flush=True)
        (e.out/'summary.json').write_text(json.dumps(rows,indent=2))
    else:
        from pcg.prototype.creative_batches.plains50_ports import produce_v2 as orchestration
        orchestration.recipes=sys.modules[__name__] # explicit recipe injection; original machinery unchanged
        result=orchestration.run(a.name,only=list(RECIPES),interfaces=[0])
        ledger=json.loads((result/'ledger.json').read_text());assert sum(r['actual_physics_cases']for r in ledger)<=400
