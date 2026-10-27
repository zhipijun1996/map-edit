"""A2 application: shoot a parked lift, then leave its shrinking headroom."""
import copy,json,math
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,settle,finish,reward
from pcg.prototype.workshop.counterexamples import alternatives as common_alts
from pcg.prototype.workshop.evaluate import purpose as common_purpose
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.dynamic.generators import dynamic
HERE=Path(__file__).parent;RECIPE='rising-side-exit'

def candidates(interface):
    out=[]
    for delay in [42,48,54,60]:
        c=base(f'plains50-machinery-rising-side-i{interface}-d{delay}-v1');c['family']=RECIPE;c['production_recipe']=RECIPE;c['parent_family']='chase-landing'
        front,top,width,target,roof=[(760,220,240,870,[275,20,240,90]),(790,205,230,900,[275,10,260,85])][interface]
        c['platforms']=[[-160,438,400,100],[front,top,width,100],[210,100,60,250],roof,[-200,700,1500,60]]
        c['moving_platforms']=[dict(platform_id='rising-deck',start=[315,448],finish=[315,70],size=[300,20],travel_duration=1.8,dwell_duration=.15,initial_phase=0)]
        c['latches']=[dict(id='lift-control',bell=[390,180],gate=[-100,-100,10,10],open_seconds=0,ferry_id='rising-deck',return_access=[330,160])]
        c['thorns']=[dict(surface_id='rising-roof',platform_index=3,face='bottom',start_offset=0,length=roof[2],depth=12)]
        c['rule_parameters']=dict(relationship='activate real lift, read shrinking headroom, choose an airborne pause/recoil into a side receiver',
            interface=interface,departure_after_ticks=delay,receiver=[front,top,width,100],shore_screen=[210,100,60,250],roof=roof,
            initial_motion='parked',no_new_platform_behaviour=True,return_conditions='UNKNOWN')
        p=[cmd('axis',value=1),wait_x(400),cmd('axis',value=0),dynamic('wait','on_platform',query=dict(id='rising-deck'),timeout=120),cmd('shoot',aim_cell=dict(kind='bell',id='lift-control')),
            cmd('wait',after=delay),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,aim_cell=dict(kind='bell',id='lift-control',receiver='access')),settle(target,6)]
        reward(c,target,top-18);finish(c,target,top-18,p);c['max_frames']=900;c['capabilities']=['move','jump','shot_recoil'];c['trace_all']=False
        c['generation_rule']=dict(id='plains50/machinery/'+RECIPE,version=1,source_type='actual_current_codex_subagent',author_task='/root/plains50_machinery',parameters=c['rule_parameters'])
        c['layout_title']='启动上升台后反冲进侧洞 / '+str(interface+1);c['rule_source_path']=str(Path(__file__).relative_to(ROOT.parent));out.append(c)
    return out

def specification(interface):
    c=candidates(interface)[0];objective=copy.deepcopy(c['rule_parameters']);objective.pop('departure_after_ticks')
    return dict(schema='map-notes/challenge-specification/v1',id=f'plains50/machinery/rising-side/i{interface}/v1',region='plains',required_family=RECIPE,
        objective=objective,capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),
        relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=420,rise=420-c['exit_port'][1],space=dict(max_width=1900,max_height=1500,max_port_span_x=1200),
        boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=8,mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),
        resource_state=dict(reset_between_components=False,entry='original supported resources',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))

def compiler(request):
    specs=[specification(i)for i in [0,1]];cs=[]
    for i,s in enumerate(specs):
        for c in candidates(i):c['map_specification']=s;c['idea_ids']=['plains50-machinery/rising-side-exit'];cs.append(c)
    return dict(status='requires_physics',specifications=specs,cases=cs)

def purpose(c,r):
    p=common_purpose(c,r);fs=r.get('frames',[])
    carried=[f for f in fs if f.get('support_id')=='rising-deck']
    neutral=[f for f in carried if abs(f.get('axis',0))<.01]
    gain=max((f['y']for f in neutral),default=0)-min((f['y']for f in neutral),default=0)
    toggles=[e for e in r.get('workshop',{}).get('events',[])if e['type']=='carrier_toggle']
    p['causal'].update(real_neutral_rise=gain,neutral_supported_frames=len(neutral),carrier_toggles=toggles)
    if gain<70:p['reasons'].append('rising_world_support_not_used')
    if len(toggles)<2 or not toggles[0]['running']or toggles[1]['running']or not toggles[1]['airborne']:p['reasons'].append('airborne_pause_recoil_not_demonstrated')
    p['ok']=not p['reasons'];return p

def alternatives(c):
    out=common_alts(c)
    def add(label,plan):
        v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
    add('stay-aboard',copy.deepcopy(c['control_plan'][:5])+[cmd('wait',after=420),settle(c['exit_port'][0],6)])
    for x in [180,220,238]:
        for delay in [20,40,60]:
            p=[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='lift-control')),cmd('shoot',after=delay,aim_cell=dict(kind='bell',id='lift-control',receiver='access')),
                cmd('axis',value=1),wait_x(400),cmd('axis',value=0),dynamic('wait','on_platform',query=dict(id='rising-deck'),timeout=180),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.97,.243]),settle(c['exit_port'][0],6)]
            add(f'shore-prepark-{x}-{delay}',p)
    for dy in [.15,.5,.8660254]:
        p=[cmd('axis',value=1),wait_x(220),cmd('jump'),cmd('jump_release',after=16),cmd('shoot',after=6,direction=[-math.sqrt(1-dy*dy),dy]),settle(c['exit_port'][0],6)]
        add('direct-shore-'+str(dy),p)
    return out

def extra_sources():return [HERE/'rising-protocol-v1.json',HERE/'rising-card-v1.json']
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--probe',action='store_true');p.add_argument('--name',required=True);a=p.parse_args()
    if a.probe:
        e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__)]+extra_sources());rows=[]
        for c,r,ev in e.run([c for i in [0,1]for c in candidates(i)],'rising-side-probe'):
            q=purpose(c,r);rows.append(dict(id=c['id'],ok=q['ok'],purpose=q,evidence=ev));print(c['id'],r.get('reason'),q,flush=True)
        (e.out/'summary.json').write_text(json.dumps(rows,indent=2))
    else:run(a.name,[dict(recipe=RECIPE)],1,library_root=ROOT/'module_library/store',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=extra_sources())
