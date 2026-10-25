"""Use the existing Map Director's real ascent demand as an adaptation fixture.

No topology/layout implementation. An explicit local family revision asks for
an active carrier, preserving Map's 100 rise, 900x800 space, capabilities, ports,
zero reward and budgets. This fixture is not task B's whole-map approval.
"""
import argparse,copy,json
from .rules import chase,settle
from .engine import ROOT,WorkshopEngine
from .evaluate import evaluate
from .experiments import write,counter_run,produce
from pcg.map_directed.director import design,challenge_specs
from ..factory.core.quality import digest

def request():
    original=next(s for s in challenge_specs(design('task-a-map-demand-01'))if s['id']=='bell-terrace-ascent')
    spec=copy.deepcopy(original)
    # Record the negotiation explicitly: never silently substitute a family.
    spec.update(id='task-a-active-carrier-ascent',required_family='chase-landing',boundary_policy='open',enclosing_walls=False,
        content_family_revision=dict(from_family=original['required_family'],to_family='chase-landing',reason='Task A active landing prototype requested at the same Map ascent role',director_revisions_used=1),
        return_conditions='UNKNOWN; concrete continuous carrier return fixtures separate',
        relations=[dict(from_port='entry',to_port='exit',role='main')])
    return original,spec

def adapt(spec):
    conflicts=[]
    for key,value in [('required_family','chase-landing'),('region','plains'),('entry_y',420),('rise',100)]:
        if spec.get(key)!=value:conflicts.append(dict(field=key,requested=spec.get(key),supported=value))
    if spec['ports']['count']!=2 or spec['ports']['required_normals']!=[[-1,0],[1,0]]:conflicts.append(dict(field='ports',reason='unsupported directed interface'))
    if spec['capabilities']['allOf']!=['move','jump','shot_recoil']or spec['capabilities']['anyOfGroups']:conflicts.append(dict(field='capabilities',reason='exact real base capability configuration required'))
    if spec['space']['max_width']<900 or spec['space']['max_height']<800:conflicts.append(dict(field='space',supported_minimum=[900,800]))
    if spec['risk_reward']['amount']!=0:conflicts.append(dict(field='reward',reason='this Map demands an unrewarded travel ascent'))
    if conflicts:return dict(status='unsatisfied',conflicts=conflicts,searched=dict(rule='chase-landing',candidates=1),negotiable=['explicit ports/space/rise revision; no replacement family'])
    c=chase(0);c['id']='map-demand-active-ascent';c['platforms'][0]=[-60,438,300,100];c['platforms'][1]=[660,338,180,100];c['platforms'][2]=[-60,650,900,60]
    # Disabled original motion-mode gate still has an authored extent. Keep it
    # in the actual requested footprint, rather than ignoring it during lookup.
    c['latches'][0]['gate']=[-30,100,10,10]
    c['exit_port']=[760,320];c['goal']=[735,316,50,8];c['control_plan'][-1]=settle(760,6)
    c['reward_sites']=[];c['expected_reward']=0;c['map_specification']=copy.deepcopy(spec);c['idea_ids']=['human-A2-chase-landing']
    c['rule_parameters']=dict(map_director_demand_id=spec['id'],rise=100,space=[900,800],landing=[760,320],reward=0,adaptations=['receiver height and width','shorter unused rear bank','safe ground footprint','exit target outside original moving envelope','horizontal commitment prevents ordinary carrier dismount bypass','no chest for unrewarded travel role'])
    c['generation_rule']=dict(id='workshop/chase-landing-map-adapter',version=1,parameters=c['rule_parameters'])
    from pcg.map_directed.library import fits
    if not fits(c,spec):return dict(status='unsatisfied',conflicts=[dict(field='space/ports/capabilities',reason='materialized content exceeds the actual Map hard demand')],searched=dict(candidates=1),negotiable=['explicit footprint revision; no silent widening'])
    return dict(status='requires_physics',cases=[c],source='actual pcg.map_directed.director.challenge_specs ascent request with recorded family revision')

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
    write(root/'summary.json',dict(source='existing Map Director demand',family_revision_explicit=True,topology_modified=False,
        generation_calls=1,calibration_selected_only=True,output=str(final.relative_to(ROOT)),whole_map_validation='task B responsibility',production_admitted=False))
    return root
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();print(run(a.name))
