import copy,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.rules import cmd,wait_x,settle
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.counterexamples import alternatives as original_alternatives
from pcg.prototype.creative_batches.occupancy.probe_v1 import candidates as probes
HERE=Path(__file__).parent

def compiler(request):
    if request.get('recipe')!='live-enemy-sensor':return dict(status='needs_design',gaps=['unknown recipe'],cases=[])
    cases=[c for c in probes()if c['id'].startswith('enemy-sensor-240')]
    spec=dict(schema='map-notes/challenge-specification/v1',id='creative/live-enemy-sensor/0',region='plains',required_family='enemy-sensor-hold',objective=dict(role='shoot enemy into live occupancy zone, maintain actual door energization until crossing; killing is not an artificial checker ban'),
        capabilities=dict(version=1,status='defined',allOf=['move','jump','shot_recoil'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=420,rise=0,space=dict(max_width=1200,max_height=900,max_port_span_x=900),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=12,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='original supported resources',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=2,director_revisions=0))
    for c in cases:
        c['platforms'].append([270,400,24,38])
        c['map_specification']=copy.deepcopy(spec);c['idea_ids']=['llm-root-live-enemy-sensor-v1'];c['generation_rule']=dict(id='creative/live-enemy-sensor',version=2,source_path=str(Path(__file__).relative_to(ROOT.parent)))
    return dict(status='requires_physics',specifications=[spec],cases=cases)

def purpose(c,r):
    reasons=[];events=r.get('plains',{}).get('events',[]);frames=r.get('frames',[])
    if not r.get('ok'):reasons.append(r.get('reason','unstable'))
    if r.get('hp')!=5 or r.get('returns'):reasons.append('player_harm_or_return')
    if r.get('workshop',{}).get('coins')!=12:reasons.append('reward_not_claimed')
    occupied=[e['frame']for e in events if e['type']=='occupancy_changed'and e.get('occupied')]
    hits=[e['frame']for e in events if e['type']=='enemy_hit']
    crossing=next((f['frame']for f in frames if f['x']-12>520),None)
    if not occupied or not hits or crossing is None or min(occupied)<min(hits)or crossing<min(occupied):reasons.append('actual_hit_occupancy_gate_crossing_missing')
    return dict(ok=not reasons,reasons=reasons,causal=dict(first_hit=min(hits)if hits else None,first_actual_live_occupancy=min(occupied)if occupied else None,body_cleared_gate=crossing,late_killing_not_forbidden=True))

def alternatives(c):
    out=original_alternatives(c)
    def add(label,plan):
        v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
    for hold in [8,16,24]:
        add('overtop-'+str(hold),[cmd('axis',value=1),wait_x(240),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[-.2,.98]),settle(650,6)])
    for x in [200,240,300]:
        add('kill-first-'+str(x),[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='enemy',id='keeper')),cmd('shoot',24,aim_cell=dict(kind='enemy',id='keeper')),cmd('shoot',24,aim_cell=dict(kind='enemy',id='keeper')),cmd('axis',value=1),cmd('jump'),cmd('jump_release',12),settle(650,6)])
    add('self-weight',[cmd('axis',value=1),wait_x(240),cmd('jump'),cmd('jump_release',12),settle(650,6)])
    return out

if __name__=='__main__':
    sources=[p for p in HERE.iterdir()if p.suffix in ['.py','.gd','.mjs','.tscn']]
    run('workshop-creative-occupancy-production-v2',requests=[dict(recipe='live-enemy-sensor')],cycles=1,library_root=ROOT/'results/workshop-creative-occupancy-library-v1',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=sources,runner_script=HERE/'runner_v1.gd',export_script=HERE/'export_v1.mjs')
