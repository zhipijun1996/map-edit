"""Second revision: lower boarding dock behind a real sight-screen, side exit."""
import copy,json,math
from pathlib import Path
from pcg.prototype.creative_batches.plains50_machinery import rising_v1 as old
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.rules import cmd,wait_x,settle
from pcg.prototype.workshop.evaluate import purpose as common_purpose
from pcg.prototype.workshop.counterexamples import alternatives as common_alts
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.dynamic.generators import dynamic
HERE=Path(__file__).parent;RECIPE=old.RECIPE

def candidates(interface):
    out=[]
    for delay in [60,66,72,78]:
        c=old.candidates(interface)[0]
        front,top,width,target=[(800,160,260,920),(830,150,230,940)][interface]
        roof=[355,-80,220+interface*15,80]
        c['platforms']=[[-160,438,400,100],[front,top,width,100],[300,100,50,320],roof,[-200,700,1500,60]]
        c['moving_platforms'][0].update(start=[315,488],finish=[315,-40],travel_duration=2.2)
        c['latches'][0]['return_access']=[370,410]
        c['thorns'][0]['length']=roof[2]
        c['id']=f'plains50-machinery-rising-side-i{interface}-d{delay}-v2'
        c['control_plan'][5]['trigger']['after']=delay;c['control_plan'][-1]=settle(target,6)
        c['exit_port']=[target,top-18];c['goal']=[target-25,top-22,50,8]
        c['reward_sites'][0].update(position=c['exit_port'],region=[target-30,top-23,60,10])
        c['rule_parameters']=dict(relationship='activate a lower lift beyond occluding rock, read remaining headroom and leave toward a high side receiver',
            interface=interface,departure_after_ticks=delay,receiver=[front,top,width,100],shore_screen=[300,100,50,320],roof=roof,
            controls='original start/pause only; pause may stabilize departure but is not forced if same rising-support challenge remains',
            prior_failure='v1 all8 probes fell short of distant high bank; second source revision changes dock/receiver and lower access ray',
            recovery_and_return='UNKNOWN')
        c['generation_rule'].update(version=2,parameters=c['rule_parameters']);c['rule_source_path']=str(Path(__file__).relative_to(ROOT.parent));out.append(c)
    return out

def specification(interface):
    s=old.specification(interface);c=candidates(interface)[0];obj=copy.deepcopy(c['rule_parameters']);obj.pop('departure_after_ticks')
    s.update(id=f'plains50/machinery/rising-side/i{interface}/v2',objective=obj,rise=420-c['exit_port'][1]);return s

def compiler(request):
    specs=[specification(i)for i in [0,1]];cs=[]
    for i,s in enumerate(specs):
        for c in candidates(i):c['map_specification']=s;c['idea_ids']=['plains50-machinery/rising-side-exit'];cs.append(c)
    return dict(status='requires_physics',specifications=specs,cases=cs)

def purpose(c,r):
    p=common_purpose(c,r);fs=r.get('frames',[]);neutral=[f for f in fs if f.get('support_id')=='rising-deck'and abs(f.get('axis',0))<.01]
    rise=max((f['y']for f in neutral),default=0)-min((f['y']for f in neutral),default=0)
    toggles=[e for e in r.get('workshop',{}).get('events',[])if e['type']=='carrier_toggle']
    p['causal'].update(real_neutral_rise=rise,neutral_supported_frames=len(neutral),carrier_toggles=toggles,pause='optional same-core alternative')
    if rise<70:p['reasons'].append('rising_world_support_not_used')
    if not toggles or not toggles[0]['running']:p['reasons'].append('real_lift_not_activated')
    p['ok']=not p['reasons'];return p

def alternatives(c):
    out=common_alts(c)
    def add(label,plan):
        v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
    add('stay-aboard',copy.deepcopy(c['control_plan'][:5])+[cmd('wait',after=420),settle(c['exit_port'][0],6)])
    for receiver in ['main','access']:
        aim=dict(kind='bell',id='lift-control')
        if receiver=='access':aim['receiver']='access'
        for x in [180,220,238]:
            for delay in [20,40,60]:
                p=[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('shoot',aim_cell=aim),cmd('shoot',after=delay,aim_cell=aim),
                    cmd('axis',value=1),wait_x(400),dynamic('wait','on_platform',query=dict(id='rising-deck'),timeout=180),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.5,.8660254]),settle(c['exit_port'][0],6)]
                add(f'shore-prepark-{receiver}-{x}-{delay}',p)
    for delay in [20,40,60]:
        p=[cmd('axis',value=1),wait_x(220),cmd('axis',value=0),cmd('jump'),cmd('jump_release',after=10),cmd('shoot',after=6,aim_cell=dict(kind='bell',id='lift-control',receiver='access')),cmd('wait',after=delay),cmd('jump'),cmd('shoot',after=10,aim_cell=dict(kind='bell',id='lift-control',receiver='access')),cmd('axis',value=1),wait_x(400),cmd('jump'),cmd('shoot',after=16,direction=[-.5,.8660254]),settle(c['exit_port'][0],6)]
        add('air-shore-prepark-'+str(delay),p)
    for dy in [.15,.5,.8660254,1.]:
        p=copy.deepcopy(c['control_plan'][:4])+[cmd('axis',value=1),wait_x(450),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-math.sqrt(1-dy*dy),dy]),settle(c['exit_port'][0],6)]
        add('static-dock-direct-'+str(dy),p)
    return out

def extra_sources():return old.extra_sources()+[HERE/'rising_v1.py',HERE/'rising-protocol-v2.json']
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--probe',action='store_true');p.add_argument('--name',required=True);a=p.parse_args()
    if a.probe:
        e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__)]+extra_sources());rows=[]
        for c,r,ev in e.run([c for i in [0,1]for c in candidates(i)],'rising-side-probe'):
            q=purpose(c,r);rows.append(dict(id=c['id'],ok=q['ok'],purpose=q,evidence=ev));print(c['id'],r.get('reason'),q,flush=True)
        (e.out/'summary.json').write_text(json.dumps(rows,indent=2))
    else:run(a.name,[dict(recipe=RECIPE)],1,library_root=ROOT/'map_directed/library',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=extra_sources())
