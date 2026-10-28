"""Compile the supported RegionPolicy subset through existing R2/CP-SAT APIs."""
import copy,json,sys
from pathlib import Path
from ..director import REPO
from ..run import write
from ..direct_join.layout import solve

POLICY=Path(__file__).with_name('plains-policy.json')

def load_policy(path=POLICY):
    p=json.loads(Path(path).read_text())
    allowed={'schema','id','source_intent','region','capabilities','topology','hard','content','scope'}
    if set(p)-allowed:raise ValueError('unsupported_region_policy_fields/'+','.join(sorted(set(p)-allowed)))
    if p['schema']!='map-notes/region-policy/v1'or p['region']!='plains':raise ValueError('unsupported_region_policy_domain')
    if set(p['topology'])!={'producer','core_count','reward_expeditions'}:raise ValueError('unsupported_topology_policy_fields')
    if set(p['capabilities'])!={'move','jump','shot_recoil'}:raise ValueError('unsupported_region_capabilities')
    if p['topology']['producer']!='region-network-v2'or p['topology']['reward_expeditions']!=2:raise ValueError('unsupported_topology_policy')
    if p['hard']!={'direct_module_join':True,'map_added_terrain':0,'moving_platforms':0,'optional_rewards_required_for_completion':False}:raise ValueError('unsupported_hard_policy')
    if p['content']!={'landform':'exposed_rock_banks','vertical_transfer':'airborne_recoil','reward':'physical_chest','main_risk':'moderate','reward_risk':'advanced'}:raise ValueError('unsupported_content_policy')
    return p


def graph_for(seed,policy):
    sys.path.insert(0,str(REPO/'experiments/l4-mapgen'))
    import region_network
    g=region_network.construct(seed,policy['region'],policy['topology']['core_count'])
    g['initial_abilities']=policy['capabilities'][:]
    g['seed']=seed
    g['region_policy']=policy['id']
    return g


def design(name,seed):
    p=load_policy();g=graph_for(seed,p)
    # Content responsibility affects the finite size domain before embedding.
    # Larger hubs and reward chambers are genuine shapes, not Map connectors.
    degrees={n['id']:sum(n['id']in[e['from'],e['to']]for e in g['edges'])for n in g['nodes']}
    cc={n['id']:dict(min_w=3 if degrees[n['id']]>=4 or n['role']=='reward'else 2,max_w=4,
        min_h=4 if n['role']=='reward'or degrees[n['id']]>=4 else 3,max_h=5,side_ports_at_base=n['role']=='reward')for n in g['nodes']}
    r=solve(name,seconds=55,seed=0,graph=g,content_constraints=cc,
        settings={'units':[512,144],'boss_at_top':False,'workers':1,'deterministic_budget':35})
    r.update(content_floor_margin=96,port_head_clearance=24,physical_port_clearance=True,region_policy=p)
    write(REPO/'pcg/results'/name/'layout.json',r)
    return r

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
    protocol=json.loads(Path(__file__).with_name('protocol.json').read_text());design(a.name,protocol['seed'])
