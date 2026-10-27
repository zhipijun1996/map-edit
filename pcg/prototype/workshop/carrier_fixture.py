"""Independent carrier challenge using a fixed historical offline fixture.

Its old dimensions are local test parameters, not new Module design rules.
"""
import argparse,copy,json
from .rules import chase,settle
from .engine import ROOT,WorkshopEngine
from .evaluate import evaluate
from .experiments import write,counter_run,produce
from ..factory.core.quality import digest

def request():
    """Return a fixed offline fixture, never execute an exploration generator."""
    data=json.loads((__import__('pathlib').Path(__file__).with_name('carrier-fixture-v1.json')).read_text())
    return copy.deepcopy(data['original']),copy.deepcopy(data['effective'])


def adapt(spec):
    conflicts=[]
    for key,value in [('required_family','chase-landing'),('region','plains'),('entry_y',420),('rise',100)]:
        if spec.get(key)!=value:conflicts.append(dict(field=key,requested=spec.get(key),supported=value))
    if spec['ports']['count']!=2 or spec['ports']['required_normals']!=[[-1,0],[1,0]]:conflicts.append(dict(field='ports',reason='unsupported directed interface'))
    if spec['capabilities'].get('status')!='defined'or spec['capabilities'].get('version')!=1 or spec['capabilities']['allOf']!=['move','jump','shot_recoil']or spec['capabilities']['anyOfGroups']:conflicts.append(dict(field='capabilities',reason='exact real base capability configuration required'))
    original,supported=request()
    for field in ['resource_state','return_conditions','boundary_policy','enclosing_walls']:
        if spec.get(field)!=supported.get(field):conflicts.append(dict(field=field,reason='unsupported entry/return/boundary condition; no implicit resource reset or shell',supported=supported.get(field)))
    if spec['space']['max_width']<900 or spec['space']['max_height']<800:conflicts.append(dict(field='space',supported_minimum=[900,800]))
    if spec['risk_reward']['amount']!=0:conflicts.append(dict(field='reward',reason='this Map demands an unrewarded travel ascent'))
    if conflicts:return dict(status='unsatisfied',conflicts=conflicts,searched=dict(rule='chase-landing',candidates=1),negotiable=['explicit ports/space/rise revision; no replacement family'])
    c=chase(0);c['id']='map-demand-active-ascent';c['platforms'][0]=[0,438,240,100];c['platforms'][1]=[850,338,50,100];c['platforms'][2]=[0,650,900,60]
    # Disabled original motion-mode gate still has an authored extent. Keep it
    # in the actual requested footprint, rather than ignoring it during lookup.
    c['latches'][0]['gate']=[10,100,10,10]
    c['exit_port']=[875,320];c['goal']=[858,316,34,8];c['control_plan'][-1]=settle(875,6)
    c['reward_sites']=[];c['expected_reward']=0;c['map_specification']=copy.deepcopy(spec);c['idea_ids']=['human-A2-chase-landing']
    c['rule_parameters']=dict(map_director_demand_id=spec['id'],rise=100,space=[900,800],landing=[875,320],reward=0,adaptations=['receiver height and width','shorter unused rear bank','safe ground footprint','exit target outside original moving envelope','static-dock and far-endpoint ordinary-jump gaps','no chest for unrewarded travel role'])
    c['generation_rule']=dict(id='workshop/chase-landing-map-adapter',version=1,parameters=c['rule_parameters'])
    from pcg.module_library.matching import fits
    if not fits(c,spec):return dict(status='unsatisfied',conflicts=[dict(field='space/ports/capabilities',reason='materialized content exceeds the actual Map hard demand')],searched=dict(candidates=1),negotiable=['explicit footprint revision; no silent widening'])
    return dict(status='requires_physics',cases=[c],source='fixed offline carrier fixture; historical provenance in carrier-fixture-v1.json')

def run(name):
    root=ROOT/'results'/name
    if root.exists():raise ValueError('immutable_map_demand_experiment')
    root.mkdir(parents=True);original,spec=request();response=adapt(spec)
    write(root/'original-map-demand.json',original);write(root/'effective-map-demand.json',spec);write(root/'generation-response.json',response)
    if response['status']!='requires_physics':return root
    bases=response['cases'];engine=WorkshopEngine(root/'calibration')
    entries=evaluate(engine,bases,26102501,12,'map-demand-calibration')
    if not all(e['quality_gate']['status']=='awaiting_human_review'for e in entries):raise ValueError('map_demand_calibration_not_passed')
    requested=([spec],bases);counter_run(name+'/counters',['chase-landing'],requested)
    counter_summary=json.loads((root/'counters/summary.json').read_text())
    if counter_summary['cheap_successes']:
        write(root/'summary.json',dict(status='unsatisfied',conflicts=[dict(condition='causal_relationship',reason='key action can be omitted',counterexamples=counter_summary['cheap_successes'])],searched=dict(candidates=1),negotiable=['new receiver geometry within the unchanged Map space/rise/port budget'],production_admitted=False))
        return root
    final=produce(name+'/holdout',['chase-landing'],name+'/counters',requested)
    write(root/'summary.json',dict(source='fixed offline carrier fixture',family_revision_explicit=True,topology_modified=False,
        generation_calls=1,calibration_selected_only=True,output=str(final.relative_to(ROOT)),whole_map_validation='task B responsibility',production_admitted=False))
    return root
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();print(run(a.name))
