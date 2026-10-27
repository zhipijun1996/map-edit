"""Four bounded machinery adapters; original physical components and Harness."""
import copy,json,importlib.util
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.rules import chase,settle
from pcg.prototype.workshop.evaluate import purpose as common_purpose
from pcg.prototype.workshop.counterexamples import alternatives as common_alts
from pcg.prototype.creative_batches.machinery.production_v9 import purpose as evac_purpose,alternatives as evac_alts
from pcg.prototype.creative_batches.machinery.production_v14 import purpose as dual_purpose,alternatives as dual_alts

HERE=Path(__file__).parent
OLD=HERE.parent/'machinery'
ray_spec=importlib.util.spec_from_file_location('plains50_original_ray',HERE.parent/'resource_routes/moving-ray-v1.py')
ray=importlib.util.module_from_spec(ray_spec);ray_spec.loader.exec_module(ray)
RECIPES=('chase-landing','evacuate-rejoin','moving-ray-window','carrier-dual-service')

def source(recipe,interface):
    if recipe=='chase-landing':return chase(interface)
    name={'evacuate-rejoin':'M16','moving-ray-window':'M17','carrier-dual-service':'M20'}[recipe]
    return json.loads((HERE/'inputs'/f'{name}.json').read_text())

def move_receiver(c,index,x,y,w,target_x):
    c['platforms'][index][:3]=[x,y,w]
    c['exit_port']=[target_x,y-18];c['goal']=[target_x-25,y-22,50,8]
    c['control_plan'][-1]=settle(target_x,6)

def candidates(recipe,interface):
    c=source(recipe,interface)
    if recipe=='chase-landing':
        front,top,width,target=([(805,288,210,905),(850,284,240,950)][interface])
        move_receiver(c,1,front,top,width,target)
        c['reward_sites'][0].update(position=c['exit_port'],region=[target-30,top-23,60,10])
    elif recipe=='evacuate-rejoin':
        # A narrow high refuge vs a wider lower refuge changes landing support,
        # then a distinct receiver frontage changes the final interception use.
        island=[(660,245,150),(645,250,175)][interface]
        c['platforms'][1][:3]=island
        target=[1450,1465][interface];front=[1335,1350][interface]
        move_receiver(c,2,front,[438,430][interface],[235,220][interface],target)
        cache_x=[730,725][interface];c['reward_sites'][0].update(position=[cache_x,island[1]-18],region=[cache_x-30,island[1]-23,60,10])
        c['control_plan'][14]['trigger']['dynamic']['value']=cache_x
    elif recipe=='moving-ray-window':
        # Keep the original physical shutter. The requested landing frontage /
        # wall depth differs, so every timing and projectile proof is renewed.
        target=[680,645][interface]
        move_receiver(c,1,460,438,[285,255][interface],target)
        c['platforms'][3][0]=[745,715][interface]
        c['platforms'][2][2]=[525,495][interface]
        c['reward_sites'][0].update(position=c['exit_port'],region=[target-30,415,60,10])
    elif recipe=='carrier-dual-service':
        target=[1795,1745][interface]
        move_receiver(c,1,[1675,1640][interface],[438,428][interface],[260,240][interface],target)
        c['reward_sites'][0].update(position=c['exit_port'],region=[target-30,c['exit_port'][1]-5,60,10])
    c['id']=f'plains50-machinery-{recipe}-i{interface}-v1'
    c['production_recipe']=recipe;c['parent_family']=recipe
    c['capabilities']=['move','jump','shot_recoil'];c['trace_all']=False
    c['rule_parameters']=dict(relationship=recipe,interface=interface,receiver=c['platforms'][-1] if recipe=='carrier-dual-service' else c['exit_port'],
        ancestry='Old relationship adapted to explicit new receiving/refuge geometry, not a new family',
        requested_geometry=copy.deepcopy(c['platforms']),only_special_ability='shot_recoil')
    c['generation_rule']=dict(id='plains50/machinery/'+recipe,version=1,source_type='actual_current_codex_subagent',author_task='/root/plains50_machinery',parameters=c['rule_parameters'])
    c['rule_source_path']=str(Path(__file__).relative_to(ROOT.parent))
    c['layout_title']={'chase-landing':'追台后登上窄岸','evacuate-rejoin':'在避险岛换乘同台','moving-ray-window':'穿过移动挡板的射击窗口','carrier-dual-service':'先守门再运人的载台'}[recipe]+f' / 接口{interface+1}'
    return [c]

def specification(recipe,interface):
    c=candidates(recipe,interface)[0]
    return dict(schema='map-notes/challenge-specification/v1',id=f'plains50/machinery/{recipe}/i{interface}/v1',region='plains',required_family=recipe,
        objective=copy.deepcopy(c['rule_parameters']),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),
        ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='entry',to_port='exit',role='reward')],
        entry_y=c['entry_port'][1],rise=c['entry_port'][1]-c['exit_port'][1],space=dict(max_width=2400,max_height=1600,max_port_span_x=1900),
        boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=c['reward_sites'][0]['amount'],mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),
        resource_state=dict(reset_between_components=False,entry='original supported resources',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=1,director_revisions=0))

def compiler(request):
    recipe=request['recipe'];specs=[specification(recipe,i)for i in [0,1]];cs=[]
    for i,s in enumerate(specs):
        for c in candidates(recipe,i):c['map_specification']=s;c['idea_ids']=['plains50-machinery/'+recipe];cs.append(c)
    return dict(status='requires_physics',specifications=specs,cases=cs)

def purpose(c,r):
    recipe=c['production_recipe']
    return {'chase-landing':common_purpose,'evacuate-rejoin':evac_purpose,'moving-ray-window':ray.purpose,'carrier-dual-service':dual_purpose}[recipe](c,r)

def alternatives(c):
    recipe=c['production_recipe']
    fn={'chase-landing':common_alts,'evacuate-rejoin':evac_alts,'moving-ray-window':ray.alternatives,'carrier-dual-service':dual_alts}[recipe]
    out=fn(c)
    # The declared finite set remains mechanism-specific; no full search claim.
    return out

def extra_sources():
    return list((HERE/'inputs').glob('*.json'))+[HERE/'protocol-v1.json',HERE/'design-cards-v1.json']+list(OLD.glob('*.py'))+list(OLD.glob('*.gd'))+list(OLD.glob('*.mjs'))+[HERE.parent/'resource_routes/moving-ray-v1.py']

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--probe',action='store_true');p.add_argument('--name',default='workshop-plains50-machinery-probe-v1');a=p.parse_args()
    if a.probe:
        e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__)]+extra_sources(),runner_script=OLD/'dock_runner_v11.gd');rows=[]
        for c,r,ev in e.run([c for recipe in RECIPES for i in [0,1]for c in candidates(recipe,i)],'new-demand-probe'):
            q=purpose(c,r);row=dict(id=c['id'],ok=q['ok'],purpose=q,reason=r.get('reason'),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
        (e.out/'summary.json').write_text(json.dumps(rows,indent=2))
    else:
        from pcg.prototype.workshop.production_loop import run
        run(a.name,requests=[dict(recipe=r)for r in RECIPES],cycles=4,library_root=ROOT/'module_library/store',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__),extra_sources=extra_sources(),runner_script=OLD/'dock_runner_v11.gd',export_script=OLD/'dock_export_v13.mjs')
