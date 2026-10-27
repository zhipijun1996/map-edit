"""Challenge Specification -> bounded local Macro recipe; explicit failures."""
import argparse,copy,json
from pathlib import Path
from .macro import FAMILY,recipe,macro_cases,components
from .experiments import write

def specifications():
    out=[]
    for variant in range(2):
        routes,_=macro_cases(variant);c=routes[0]
        out.append(dict(schema='map-notes/challenge-specification/v1',id=f'workshop/macro/{FAMILY}/{variant}',
            source_type='content_workshop_interface_fixture',region='plains',content_kind='macro',required_family=FAMILY,
            objective=dict(outbound='air shot opens gate; claim visible cache; fall outside lip and brake into second cache',
                return_path='descend to lower bank, jump two authored shelves, recoil up to original shore',
                ordered_rewards=[12,10],interface=variant),
            capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),
            ports=dict(count=3,positions=[p['position']for p in c['ports']],required_normals=[p['normal']for p in c['ports']]),
            relations=[dict(from_port='A',to_port='B',role='reward'),dict(from_port='A',to_port='C',role='reward'),dict(from_port='C',to_port='B',role='reward'),dict(from_port='B',to_port='A',role='return')],
            entry_y=420,rise=420-c['exit_port'][1],space=dict(max_width=1200,max_height=880+20*variant,max_port_span_x=515+40*variant),
            boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=22,mandatory_damage=False),
            resource_state=dict(reset_between_components=False,entry='original supported resources; exact pre-input capture',exit='observed stable only; universal transfer UNKNOWN'),
            difficulty=dict(intent='regular',human_score=None),return_conditions='continuous A-C-B-A specimen required; universal-state return UNKNOWN',
            budget=dict(generator_candidates=4,director_revisions=0)))
    return out

def generate(spec):
    supported=specifications();keys=['region','content_kind','required_family','objective','capabilities','ports','relations','entry_y','rise','boundary_policy','enclosing_walls','risk_reward','resource_state','difficulty','return_conditions']
    for variant,known in enumerate(supported):
        if not all(spec.get(k)==known[k]for k in keys):continue
        space=spec.get('space',{})
        if set(space)!=set(known['space'])or any(type(space.get(k))not in (int,float)or space[k]<v for k,v in known['space'].items()):continue
        routes,loop=macro_cases(variant)
        return dict(status='requires_physics',matched_specification=known['id'],variant=variant,cases=routes,components=components(variant),continuous_fixture=loop,
            search=dict(registered_recipe=FAMILY,interfaces_considered=2,selected_geometry=1),production_admitted=False)
    conflicts=[dict(field=k,reason='outside_registered_macro_domain',requested=spec.get(k),supported=[s[k]for s in supported])for k in keys if not any(spec.get(k)==s[k]for s in supported)]
    if not conflicts:conflicts=[dict(field='space_or_coupled_constraints',reason='no registered interface satisfies this combination',requested=spec.get('space'),supported=[s['space']for s in supported])]
    return dict(status='unsatisfied',conflicts=conflicts,searched=dict(recipe=FAMILY,interfaces=2,unbounded_search=False),negotiable=['registered positions/roles and sufficient space', 'new authored Cell/rule plus new validation for other demands'],production_admitted=False)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--spec',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    value=generate(json.loads(Path(a.spec).read_text()));write(Path(a.out),value)
    print(json.dumps(dict(status=value['status'],conflicts=value.get('conflicts',[])),ensure_ascii=False))
