"""Existing R2 graph and canonical direct assembler, with landform demands."""
import argparse,copy,json,random,shutil,sys,time
from pathlib import Path
from ..director import REPO
from ..run import write
from ..direct_join.director import requests
from ..direct_join.canonical import export_reload
from ..direct_join.assemble import assemble_modules
from ..direct_join.audit import audit
from ..region_scale.materialize import case_for
from ..r2_full.orchestrate import logical_route,partitioned_cover,path_to,state_after
from ..library import CandidateLibrary
from ..ecosystem.run import catalog as reuse_catalog
from ..valley_complete.run import CompleteEngine
from pcg.prototype.plains.woven_landforms import generate,add_recoil_ravine,sculpt_banks,steer_recoil_routes
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest

class WovenEngine(CompleteEngine):
    def __init__(self,out):
        super().__init__(out,formal_style=True)
        paths=list(Path(__file__).parent.glob('*'))+[REPO/'pcg/prototype/plains/woven_landforms.py']
        for p in paths:
            if p.is_file()and p.suffix in ['.py','.gd','.json','.tscn']:
                rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p)
                target=self.out/'source_snapshot'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
        self.sim.runner_script=str(Path(__file__).with_name('runner.gd'))
        self.binding['runner']=self.sim.runner_script
        self.binding.update(source_files=self.hashes,source_manifest_sha256=digest(self.hashes))
        write(self.out/'source_binding.json',self.binding)


def make(c,steps,name,collect=(),buy=False):
    v=case_for(c,steps,name)
    v.update(id='woven-plains-'+name,title='风铃平原 · 岩谷织路 · R2拓扑实际拼装',
             extra_script=str(Path(__file__).with_name('mechanics.gd')),automatic_shop_input=buy,require_purchase=buy,woven_region=True)
    # These rewards/return flags belong to actual chest contacts, never visits.
    for n in v['r2_semantics']['nodes']:
        if n['id']in collect or c['nodes'][n['id']]['role']=='reward':n['opens']=[]
    program=[];done=set()
    for leg in v['pilot_program']:
        program.append(leg)
        node=leg.get('edge_to')if leg.get('edge_terminal')else None
        if node in collect and node not in done:
            for i,raw in enumerate(c['nodes'][node]['core_visit_program']):
                added=copy.deepcopy(raw);added.update(id='optional/'+node+'/'+str(i),edge_id='optional/'+node,budget_ticks=720 if raw['kind']=='module'else 360);program.append(added)
            done.add(node)
    v['pilot_program']=program
    v['required_optional_challenges']=[node+'/cache'for node in collect]
    v['map_budget_ticks']=min(36000,max(6000,len(program)*110))
    for leg in program:leg['budget_ticks']=1000 if leg['kind']=='module'else 360
    for leg in program:
        if leg['kind']=='module':
            x,y=leg['target']['position']
            leg['target']['allowed_transit_support_indices']=[i for i in v['one_way_platform_indices']if 0<y-(v['platforms'][i][1]-18)<260 and v['platforms'][i][0]+12<=x<=v['platforms'][i][0]+v['platforms'][i][2]-12]
    return v


def build(layout,out,library_root=None):
    raw=json.loads(Path(layout).read_text());g,specs,seams=requests(layout)
    from .design import load_policy,graph_for
    policy=load_policy()
    seed=json.loads(Path(__file__).with_name('protocol-release.json').read_text())['seed']
    expected=graph_for(seed,policy);actual=copy.deepcopy(g)
    expected.pop('seed',None);actual.pop('seed',None)
    if expected!=actual:raise ValueError('layout_topology_does_not_match_registered_seed_and_policy')
    g['seed']=seed
    if set(g['initial_abilities'])!=set(policy['capabilities']):raise ValueError('layout_capability_snapshot_mismatch')
    # The former abstract Boss node is an actual region exit in this pilot.
    # No fake boss encounter; forecourt/access logic remains explicit.
    next(n for n in g['nodes']if n['id']==g['goal']).update(role='exit',label='平原出口')
    for i,branch in enumerate(g['branches']):
        next(n for n in g['nodes']if n['id']==branch['reward'])['reward']=[8,12][i]
    import mapgen,region_network
    errors,logical_stats=mapgen.validate_graph(g);intent_errors=region_network.validate_region_intent(g)
    write(out/'logical-validation.json',dict(errors=errors,intent_errors=intent_errors,statistics=logical_stats,
        scope='Existing monotonic capability/flag validator; physical resources and arbitrary movement are verified separately'))
    if errors or intent_errors:raise ValueError('existing_region_or_mission_validation_failed')
    for s in specs:
        s.update(id='woven-region-v1/'+s['node_id'],boundary_policy='open',enclosing_walls=False,
            risk_reward=dict(value=s['node']['reward']),include_optional_core=False,
            design_contract=dict(landform='rock-ravine',active_action='airborne recoil',moving_platforms=False))
        if s['node_id']==g['branches'][1]['reward']:s['reward_mechanic']='angled_timed_cache'
    # Freeze requests and all sources before even a generation failure.
    write(out/'layout.json',raw);write(out/'exploration.json',g);write(out/'challenge-specifications.json',specs)
    modules=[];events=[];reused=0;library=CandidateLibrary(library_root)
    for s in specs:
        matches=library.find_payload(s,isolated_experiment=True)
        events.append(dict(event='module_query',node=s['node_id'],matches=len(matches)))
        if matches:
            modules.append(matches[0]['module']);reused+=1
            events.append(dict(event='module_reused',node=s['node_id'],record=matches[0]['record'],fresh_whole_map_required=True))
        else:
            m=generate(s)
            if int(digest(s['node_id'])[:2],16)%2==0:m=add_recoil_ravine(m)
            modules.append(steer_recoil_routes(sculpt_banks(m)))
            events.append(dict(event='new_geometry_demand_materialized',node=s['node_id'],status='requires_whole_map_physics'))
        write(out/'generation-events.json',events)
    if not reused:modules=export_reload(modules,out/'module-library',producer='pcg/prototype/plains/woven_landforms.py')
    else:
        modules=[m if m.get('canonical_document')else export_reload([m],out/'generated'/m['id'],producer='pcg/prototype/plains/woven_landforms.py')[0]for m in modules]
        modules=reuse_catalog(modules,out/'module-library')
    c=assemble_modules(g,modules,seams)
    for gate in c['gate_specs']:gate.update(zip(['x','y','w','h'],gate['bounds']))
    c['source'].update(graph_source='existing region-network-v2, fixed protocol seed',region_policy='windchime-open-rock-weave/v1')
    c['unresolved_rewards']=[]
    shops=c['case']['shop_sites']
    if not shops:raise ValueError('regional_rest_merchant_missing')
    c['shop']=copy.deepcopy(shops[0])
    write(out/'compiled.json',c);write(out/'assembly-audit.json',audit(c))
    write(out/'mission.json',dict(schema='map-notes/mission-graph/v1',entry=g['entry'],goal=g['goal'],
        objectives=[dict(id='reach-region-exit',location=g['goal'],role='main')]+[dict(id='earn-'+b['reward'],location=b['reward'],role='optional',requires=['shot_recoil'],reward=[8,12][i],opens=['expedition_return_'+str(i)])for i,b in enumerate(g['branches'])]+[dict(id='trade-earned-coins',location=next(n['id']for n in g['nodes']if n['role']=='rest'),role='optional',price=8)],
        scope='One actual region exit, two physical chest duties and original merchant; no Boss encounter or campaign persistence'))
    write(out/'map-recipe.json',dict(seed=g['seed'],region_policy=policy,layout_sha256=file_sha(Path(layout)),
        topology_source='existing region-network-v2; frozen generated topology, no authored eight-slot layout',
        placement_replay='frozen contact artifact; CP-SAT wall-clock optimal-layout reproducibility is not claimed',
        assembly_scope='isolated concrete instance; generic relations UNKNOWN',production_admitted=False))
    write(out/'generation-log.json',dict(topology='existing R2 construct; no fixed physical slots',nodes=len(g['nodes']),edges=len(g['edges']),
        module_demands=len(specs),new_geometry_instances=len(modules)-reused,unchanged_library_reuse=reused,
        reused_producer='existing room_modules and measured recoil/bell relationship',
        adaptation_scope='isolated new shapes; old generic Module relations remain UNKNOWN',map_added_terrain=0))
    return c


def cases_for(c,mode):
    if mode=='all':return cases_for(c,'routes')+cases_for(c,'cover')
    g=c['exploration_graph'];entry=g['entry'];rewards=[b['reward']for b in g['branches']]
    main=make(c,logical_route(c,[g['goal']]),'main')
    cases=[main]
    for i,branch in enumerate(g['branches']):
        # Force the intended expedition chain, then its different rejoin, then
        # return to the actual entry. No world reset or state injection.
        initial=state_after(g,(entry,frozenset(g['initial_abilities']),frozenset()),entry)
        first_edge=next(e for e in g['edges']if e['from']==branch['entry']and e['to']==branch['nodes'][0])
        steps,state,_=path_to(g,initial,branch['entry'],require_edge=first_edge);at=branch['entry']
        for to in branch['nodes']+[branch['rejoin']]:
            e=next(e for e in g['edges']if {e['from'],e['to']}=={at,to})
            if not set(e['requires'])<=state[1]or(e['switch']and e['switch']not in state[2]):raise ValueError('forced_expedition_precondition_unsatisfied/'+e['id'])
            steps.append(dict(edge_id=e['id'],**{'from':at,'to':to}));at=to
            state=state_after(g,state,at)
        if i==0:
            shop=next(n['id']for n in g['nodes']if n['role']=='rest')
            tail,state,_=path_to(g,state,shop);steps+=tail
        tail,_,_=path_to(g,state,entry);steps+=tail
        # Definition rejects equal entry/exit; end at a real neighbor after
        # the return was physically witnessed, never alter the actor position.
        neighbor=next(e['to']if e['from']==entry else e['from']for e in g['edges']if entry in [e['from'],e['to']])
        tail,_,_=path_to(g,(entry,state[1],state[2]),neighbor);steps+=tail
        cases.append(make(c,steps,'reward-expedition-'+str(i),[branch['reward']],buy=i==0))
    alternate=copy.deepcopy(g);alternate['edges']=[e for e in g['edges']if e['id']!=main['r2_semantics']['logical_route'][0]['edge_id']]
    initial=state_after(g,(entry,frozenset(g['initial_abilities']),frozenset()),entry)
    alternative,_,_=path_to(alternate,initial,g['goal'])
    cases.append(make(c,alternative,'alternative-main'))
    delayed=copy.deepcopy(cases[2]);delayed['id']='woven-plains-timed-closed-return'
    node=g['branches'][1]['reward'];gate=node+'/cache-bell';found=False
    for index,leg in enumerate(delayed['pilot_program']):
        if leg['id'].startswith('optional/'+node)and any(op.get('direction')==[0,-1]for op in leg.get('control_plan',[])):
            # The original gate refuses to close near an actor. Wait deeper
            # inside the actual chamber, then walk back under its receiver.
            deep=copy.deepcopy(leg['target']);deep['position'][0]+=31;deep['region'][0]+=31
            prefix=[dict(id='timed-return/deep',edge_id='optional/'+node,kind='walk',target=deep,budget_ticks=360),
                dict(id='timed-return/actual-close',edge_id='optional/'+node,kind='module',target=deep,budget_ticks=1000,
                    control_plan=[dict(op='axis',value=0,trigger={'after':0}),dict(op='wait',trigger={'after':90})]),
                dict(id='timed-return/receiver',edge_id='optional/'+node,kind='walk',target=copy.deepcopy(leg['target']),budget_ticks=360)]
            delayed['pilot_program'][index:index]=prefix;found=True;break
    if not found:raise ValueError('timed_chamber_internal_return_policy_missing')
    delayed['require_delayed_reopen']=gate;cases.append(delayed)
    if mode=='diagnostic':return cases[-1:]
    if mode=='mild':
        trials=[]
        for ordinal,original in enumerate(cases[:3]):
            for i in range(2):
                v=copy.deepcopy(original);v['id']+='-calibration-noise-'+str(i)
                v['noise']=dict(seed=102331+ordinal*104729+i,timing_frames=1,aim_degrees=1)
                v['calibration_only']=True;trials.append(v)
        return trials
    if mode=='main':return cases[:1]
    if mode=='reward':return cases[1:]
    if mode=='negative':
        negatives=[]
        for i,original in enumerate(cases[1:3]):
            for long_hold in [False,True]:
                v=copy.deepcopy(original);node=g['branches'][i]['reward'];v['id']='woven-negative-cache-'+str(i)+('-held-jump'if long_hold else'')
                leg=next(l for l in v['pilot_program']if l['id'].startswith('optional/'+node)and any(op['op']=='shoot'and op.get('direction')!=[0,-1]for op in l.get('control_plan',[])))
                for op in leg['control_plan']:
                    if op['op']=='shoot':op['op']='wait';op.pop('direction',None)
                    if long_hold and op['op']=='jump_release':op['trigger']['after']=24
                v['counterfactual']=dict(omitted_leg=leg['id'],expect_physics_failure=True,scope='Omit optional chamber shot only; travel actions unchanged')
                negatives.append(v)
        return negatives
    if mode=='cover':
        cases=[]
        for i,v in enumerate(partitioned_cover(c,8)):
            # Coverage policies must actually claim each encountered reward
            # before any graph-planned earned return flag can become usable.
            reached={s['to']for s in v['r2_semantics']['logical_route']}
            cases.append(make(c,v['r2_semantics']['logical_route'],'coverage-'+str(i),[n for n in rewards if n in reached]))
        return cases
    return cases


def causal_check(case,result):
    gate_id=case.get('require_delayed_reopen')
    if not gate_id:return dict(ok=True,scope='no delayed-door assertion')
    gate=next(l['gate']for l in case['latches']if l['id']==gate_id);closed=False;reopened=False
    for f in result.get('frames',[]):
        bell=next((b for b in f.get('plains',{}).get('bells',[])if b['id']==gate_id),None)
        if not bell:continue
        if bell['open_count']==1 and not bell['open']and f['x']>gate[0]+gate[2]+12 and f['y']<gate[1]+gate[3]:closed=True
        if closed and bell['open_count']>=2:reopened=True
    return dict(ok=closed and reopened,actual_closed_inside=closed,actual_reopened_from_inside=reopened)


def run(name,layout=None,source=None,mode='main',held=False,library_root=None):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_woven_run_exists')
    out.mkdir(parents=True);start=time.perf_counter()
    design_files=list(Path(__file__).parent.glob('*'))+[REPO/p for p in ['pcg/prototype/plains/woven_landforms.py','pcg/prototype/plains/room_modules.py','pcg/map_directed/direct_join/director.py','pcg/map_directed/direct_join/layout.py','pcg/map_directed/library.py','experiments/l4-mapgen/region_network.py','experiments/l4-mapgen/mapgen.py','module-contract.js','model.js','tools/export-module-contracts.mjs']]
    design_hashes={}
    for p in design_files:
        if p.is_file():
            t=out/'design-source'/p.relative_to(REPO);t.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,t)
            design_hashes[str(p.relative_to(REPO))]=file_sha(p)
    write(out/'design-binding.json',dict(files=design_hashes,sha256=digest(design_hashes)))
    protocol=json.loads(Path(__file__).with_name('protocol-release.json').read_text());write(out/'protocol.json',dict(protocol,mode=mode,held=held))
    try:
        if source:
            c=json.loads((Path(source)/'compiled.json').read_text());write(out/'compiled.json',c);write(out/'assembly-audit.json',audit(c))
        else:c=build(layout,out,library_root)
        if any(file_sha(REPO/p)!=h for p,h in design_hashes.items()):raise ValueError('design_source_changed_during_generation')
        cases=cases_for(c,mode)
        if held:
            rng=random.Random(protocol['holdout_seed']);new=[]
            for original in cases:
                if original['id']not in protocol['holdout_routes']:continue
                for i in range(protocol['holdout_phases_per_route']):
                    v=copy.deepcopy(original);phase=rng.random();v['id']+='-held-'+str(i)
                    for saw in v['saws']:saw['initial_phase']=phase
                    for enemy in v['enemies']:enemy['initial_idle_cooldown']=.6*rng.random()
                    v['noise']=dict(seed=rng.randrange(2**30),timing_frames=1,aim_degrees=1)
                    v['holdout']={'phase':phase,'selection_used':False,'input_perturbation':'±1 tick, ±1 degree; no dynamic phase claim for absent gears'};new.append(v)
            cases=cases+new
        write(out/'cases.json',dict(cases=cases));print('WOVEN',len(c['modules']),len(c['edges']),[(v['id'],len(v['pilot_program']))for v in cases],flush=True)
        engine=WovenEngine(out/'physics');rows=[]
        for v,r,ev in engine.run(cases,'woven-'+mode):
            causal=causal_check(v,r)
            row=dict(id=v['id'],ok=r['ok']and causal['ok'],reason=r['reason']if causal['ok']else'closed_return_not_demonstrated',causal=causal,ticks=r.get('ticks'),shots=r.get('shots'),failure=r.get('pilot',{}).get('failure'),extra=r.get('extra'),evidence=ev)
            if v.get('counterfactual'):
                omitted=next(i for i,l in enumerate(v['pilot_program'])if l['id']==v['counterfactual']['omitted_leg'])
                row['reached_counterfactual_leg']=r.get('pilot',{}).get('legs_completed',0)>=omitted
            rows.append(row);write(out/'rows.json',rows)
            f=row['failure']or{};print(json.dumps(dict(id=v['id'],ok=row['ok'],ticks=r.get('ticks'),shots=r.get('shots'),reason=row['reason'],leg=f.get('leg_id'),position=f.get('actual',{}).get('position')),ensure_ascii=False),flush=True)
        write(out/'summary.json',dict(all_passed=len(rows)==len(cases)and all(r['ok']for r in rows),rows=rows,held=held,wall_seconds=time.perf_counter()-start,
            counterfactual_expectations_met=mode=='negative'and len(rows)==len(cases)and all(not r['ok']and r.get('reached_counterfactual_leg')for r in rows),
            human_fun='unreviewed',production_admitted=False,larger_region_goal_met=False))
    except Exception as error:
        import traceback
        write(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc()));raise
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--layout');p.add_argument('--source');p.add_argument('--library');p.add_argument('--mode',choices=['main','reward','routes','cover','all','negative','diagnostic','mild'],default='main');p.add_argument('--held',action='store_true');a=p.parse_args();out=run(a.name,a.layout,a.source,a.mode,a.held,a.library)
    summary=json.loads((out/'summary.json').read_text())
    if not(summary['all_passed']or summary.get('counterfactual_expectations_met')):raise SystemExit(2)
