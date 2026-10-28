"""Small regional mission projected from the existing R2 exploration algorithm."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'experiments/l4-mapgen'))
import region_network as regional


def design(seed='map-growth-01'):
    rng, points, edges = regional.core_network(seed, 'plains')
    adj = regional.neighbors(range(len(points)), edges)
    cycles = set()
    for a in sorted(adj):
        for b in sorted(adj[a]):
            for c in sorted(adj[b] - {a}):
                for d in sorted((adj[c] & adj[a]) - {a,b,c}):
                    cycle = (a,b,c,d)
                    rotations = [cycle[i:]+cycle[:i] for i in range(4)]
                    reverse = tuple(reversed(cycle))
                    rotations += [reverse[i:]+reverse[:i] for i in range(4)]
                    cycles.add(min(rotations))
    if not cycles:
        raise ValueError('no_four_place_cycle_within_small_map_budget')
    selected = rng.choice(sorted(cycles))
    roles = ['entry', 'observation', 'rejoin', 'reward']
    g = {'entry':'entry','goal':'exit','initial_abilities':['move','jump','shot_recoil'],
         'nodes':[], 'edges':[], 'branches':[]}
    for role, source in zip(roles, selected):
        g['nodes'].append(dict(id=role,role='start' if role=='entry' else role,
            label={'entry':'溪谷入口','observation':'下层观察岸','rejoin':'汇合休整岸','reward':'高台可选奖励'}[role],
            grants=[],opens=[],reward=12 if role=='reward' else 0,risk=2 if role=='reward' else 1,
            ideal=list(points[source]), source_region_node=f'r{source}'))
    g['nodes'].append(dict(id='exit',role='goal',label='钟台出口',grants=[],opens=[],reward=0,risk=1,ideal=[0,0]))
    for a,b,cost,purpose in [('entry','observation',1,'main'),('observation','rejoin',1,'main'),
          ('entry','reward',2,'reward'),('reward','rejoin',1.5,'reward_rejoin'),('rejoin','exit',1.5,'main_ascent')]:
        regional.base.add_edge(g,a,b,cost=cost,purpose=purpose,requires=['shot_recoil'] if b in ['reward','exit'] else [],bidirectional=False)
    regional.base.add_edge(g,'reward','entry',cost=1.5,purpose='reward_return',bidirectional=False)
    errors,proof=regional.base.validate_graph(g)
    if errors:raise ValueError(errors)
    mission={'entry':'entry','goal':'exit','objectives':[dict(id=n['id'],role=n['role'],label=n['label']) for n in g['nodes']],
        'dependency_edges':[{'from':'rejoin','to':'exit','type':'main_progression'}],
        'intent':{'main':'short lower observation route then a single ascent',
          'optional':'recoil bell ascent to a rewarded upper ledge, then rejoin or return to entrance',
          'rhythm':['observe','choose low route or recoil reward','grounded recovery','single ascent','completion'],
          'space_theme':'windchime plains creek bank, high ledge and bell terrace'}}
    return dict(schema='mapgen-experiment/v1',version='map-directed-loop/v1',seed=seed,
        source_algorithm=regional.VERSION,source_cycle=list(selected),mission_graph=mission,
        exploration_graph=g,logic_validation=dict(ok=True,**proof),physics={'status':'unverified'})


def challenge_specs(plan):
    common=dict(schema='map-notes/challenge-specification/v1',map_seed=plan['seed'],region='plains',
        capabilities={'version':1,'status':'defined','allOf':['move','jump','shot_recoil'],'anyOfGroups':[],'note':'No advanced movement ability'},
        resource_state={'entry':'grounded at a supported safe port; exact snapshot must be captured before input',
            'exit':'stable landing; observed resources do not imply arbitrary-state guarantees',
            'reset_between_components':False},
        adaptation={'allowed':['translation','explicit separately versioned connector Cell'],
            'forbidden':['scaling','rotation','implicit mirrored traversal','invented ports','removing required exploration routes']},
        validation={'engine':'Godot 4.7.2','method':'existing PlainsEngine and exact-instance continuous map runner',
            'requires_whole_map_validation':True},budget={'director_revisions':1,'generator_calls':2,'unbounded_search':False})
    fork=copy.deepcopy(common)
    fork.update(id='creek-fork',objective='Offer a low observation route and optional higher recoil/bell reward; both rejoin.',
        ports={'count':3,'required_normals':[[-1,0],[1,0],[1,0]]},
        relations=[{'from':'A','to':'B','role':'main'},{'from':'A','to':'C','role':'reward'},
            {'from':'C','to':'B','role':'recovery'},{'from':'C','to':'A','role':'return'}],
        difficulty={'intent':'low main / moderate optional / safe recovery','human_score':None,'evidence':'UNKNOWN'},
        risk_reward={'optional':True,'amount':12,'claim':'actual supported contact at high port','mandatory_damage':False},
        space={'max_width':2000,'max_height':800,'max_port_span_x':1000},
        required_family='plains_three_port_fork')
    ascent=copy.deepcopy(common)
    ascent.update(id='bell-terrace-ascent',objective='After rejoining, ascend 100 world units to the bell terrace with one jump/recoil relation.',
        ports={'count':2,'required_normals':[[-1,0],[1,0]]},
        relations=[{'from':'entry','to':'exit','role':'main'}],
        difficulty={'intent':'one short action after supported recovery','human_score':None,'evidence':'UNKNOWN'},
        risk_reward={'optional':False,'amount':0,'mandatory_damage':False},
        space={'max_width':900,'max_height':800,'max_port_span_x':900},
        entry_y=420,rise=100,require_bell=True,required_family='bell_lift')
    return [fork,ascent]


def inspect_library(spec):
    """Use canonical JS contract validation; never reinterpret UNKNOWN as PASS."""
    cmd=['node',str(REPO/'pcg/map_directed/library_bridge.mjs')]
    p=subprocess.run(cmd,input=json.dumps(spec),text=True,capture_output=True,check=True,cwd=REPO)
    return json.loads(p.stdout)
