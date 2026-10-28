"""Bounded offline ecosystem, reusing the existing contracts/library/Harness.

CLI produces immutable evidence. Unsupported ideas stop explicitly. Only
isolated concrete instances may consume UNKNOWN general Module interfaces.
"""
import argparse,copy,json,random,shutil,time
from pathlib import Path
from .ideas import brief,proposals,NODE_RULES,RULES,demand_key
from ..director import REPO
from ..run import write
from ..library import CandidateLibrary
from ..valley_complete.director import requests
from ..valley_complete.rock_run import cases_for,make_case
from ..valley_complete.run import CompleteEngine
from ..valley_complete.gate_audit import run as gate_audit
from ..direct_join.canonical import export_reload,reload_catalog
from ..direct_join.assemble import assemble_modules
from ..direct_join.audit import audit
from pcg.prototype.plains.rock_recoil import adapt
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.plains.synthesis import command

PROTOCOL=Path(__file__).with_name('protocol.json')

class EcosystemEngine(CompleteEngine):
    def __init__(self,out):
        super().__init__(out,formal_style=True)
        for p in list(Path(__file__).parent.glob('*.py'))+[PROTOCOL,REPO/'pcg/map_directed/library.py']:
            rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p)
            target=self.out/'source_snapshot'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
        self.binding.update(source_files=self.hashes,source_manifest_sha256=digest(self.hashes))
        write(self.out/'source_binding.json',self.binding)

def design(seed,window):
    graph,old,seams,mission=requests()
    specs=copy.deepcopy(old)
    for spec in specs:
        spec['id']='ecosystem-v1/'+spec['node_id'];spec['revision']='rock-recoil-causal-design-v1'
        spec['risk_reward']['value']={'arch':12,'bell':8,'relay':16}.get(spec['node_id'],0)
        spec['design_contract']=brief(spec,window)
        spec['budget']=dict(generator_candidates=1,director_revisions=1,unbounded_retry=False)
    graph['seed']=seed
    mission.update(scope='Isolated eight-Macro, two-loop plains pilot; no actual boss encounter',
        content_policy='Source-owned rock; actual recoil; timed sealed treasure; real reward and shop; no lift dependency')
    return graph,specs,seams,mission,old

def generate(spec,source):
    """Existing measured producer; reject unimplemented relationships honestly."""
    design=spec['design_contract'];registry={r['id']:r for r in RULES}
    unsupported=[r['id']for r in design['relationships']if not registry.get(r['id'],{}).get('implemented',False)]
    if unsupported:return dict(status='unsatisfied',conditions=[dict(condition='relationships',reason='producer_not_implemented',relationships=unsupported)])
    if [r['id']for r in design['relationships']]!=NODE_RULES.get(spec['node_id']) or spec['node_id']!=source['id']:
        return dict(status='unsatisfied',conditions=[dict(condition='relationships',reason='producer_cannot_realize_requested_relationship_in_this_shape')])
    if spec.get('region')!='plains' or spec.get('boundary_policy')!='open' or spec.get('enclosing_walls') is not False:
        return dict(status='unsatisfied',conditions=[dict(condition='region/boundary',reason='only_open_plains_landform_supported')])
    caps=spec.get('capabilities',{})
    if caps.get('status')!='defined' or caps.get('anyOfGroups'):
        return dict(status='unsatisfied',conditions=[dict(condition='capabilities',reason='unknown_or_disjunctive_state_not_supported')])
    reward=sum(site['reward']for site in source['case'].get('reward_sites',[]))
    if spec['risk_reward'].get('value')!=reward:
        return dict(status='unsatisfied',conditions=[dict(condition='risk_reward.value',reason='reward_value_requires_explicit_content_revision',supported=reward)])
    if spec['ports']!=source['spec']['ports'] or spec['space']!=source['spec']['space']:
        return dict(status='unsatisfied',conditions=[dict(condition='space/ports',reason='bootstrap_adapter_geometry_domain_exceeded',
            available=dict(space=source['spec']['space'],ports=source['spec']['ports']))])
    if not set(source['case']['capabilities'])<=set(spec['capabilities']['allOf']):
        return dict(status='unsatisfied',conditions=[dict(condition='capabilities',reason='required_real_actions_unavailable')])
    window=design.get('gate_window_seconds')
    if window is not None and window not in [1.2,1.4]:
        return dict(status='unsatisfied',conditions=[dict(condition='gate_window_seconds',reason='outside_frozen_producer_domain',supported=[1.2,1.4])])
    module=adapt(source,spec)
    if window is not None:
        dx,dy=spec['placement']
        for latch in module['case']['latches']:
            latch['open_seconds']=window
            # Original ShotLatch return-side receiver: a player who pauses
            # inside can reopen by an actual projectile, without free unlocks.
            latch['return_access']=[1698-dx,280-dy]
    if module['id']=='relay':
        for reward in module['case']['reward_sites']:reward['required_enemy']=''
    module['content_version']='sha256:'+digest({k:module[k]for k in ['case','ports','core','boundary_gates']})
    return dict(status='requires_physics',module=module,
        origin='existing measured landform adapter plus demand-driven timed gate; no inherited pass')

def resolve(spec,library,source,emit):
    matches=library.find_payload(spec,isolated_experiment=True)
    emit('module_query',node=spec['node_id'],key=demand_key(spec),matches=len(matches))
    if matches:
        emit('module_reused',node=spec['node_id'],record=matches[0]['record'],generator_called=False)
        return matches[0]['module'],False
    emit('library_gap',node=spec['node_id'],relationships=[r['id']for r in spec['design_contract']['relationships']])
    response=generate(spec,source);attempts=1
    if response['status']=='unsatisfied' and spec.get('negotiation',{}).get('allow_gate_window_revision') and spec.get('budget',{}).get('director_revisions',0)>0:
        supported=[v for issue in response['conditions']if issue['condition']=='gate_window_seconds'for v in issue.get('supported',[])]
        allowed=spec['negotiation'].get('allowed_gate_windows',[])
        choices=sorted(set(supported)&set(allowed))
        if choices:
            previous=spec['design_contract']['gate_window_seconds'];spec['design_contract']['gate_window_seconds']=choices[0]
            spec['design_contract'].pop('hypothesis_sha256',None)
            spec['design_contract']['hypothesis_sha256']=digest(spec['design_contract'])
            emit('director_local_revision',condition='gate_window_seconds',before=previous,after=choices[0],maximum_revisions=1,
                topology_abilities_ports_unchanged=True)
            response=generate(spec,source);attempts+=1
    if response['status']=='unsatisfied':
        emit('unsatisfied',node=spec['node_id'],conditions=response['conditions'],retry=False)
        return None,attempts
    emit('module_generated',node=spec['node_id'],source=response['origin'],technical_status='unverified')
    return response['module'],attempts

def catalog(modules,out):
    """Compose existing canonical documents without reversioning reused content."""
    documents=out/'documents';documents.mkdir(parents=True);entries=[]
    for module in modules:
        doc=module['canonical_document'];source=REPO/doc['path']
        if file_sha(source)!=doc['sha256']:raise ValueError('canonical_payload_changed_before_assembly')
        target=documents/source.name;shutil.copy2(source,target)
        # mapnote.json -> .svg with the canonical document ID.
        svg=source.parent/(doc['id']+'.svg')
        if svg.exists():shutil.copy2(svg,documents/svg.name)
        entries.append(dict(nodeId=module['id'],id=doc['id'],contentVersion=module['content_version'],
            file=target.name,sha256=file_sha(target),physics='scoped Map evidence only',productionAdmitted=False))
    write(out/'source.json',dict(modules=modules))
    write(documents/'manifest.json',dict(schema='pcg/direct-module-catalog/v1',modules=entries,
        scope='Existing canonical documents, unchanged; per-instance physical validation remains mandatory'))
    return reload_catalog(out)

def nominal_cases(compiled):
    cases=cases_for(compiled,'full')
    delayed=make_case(compiled,['arch','lookout','west'],'timed-cache-delayed-return',('arch',))
    index=next(i for i,leg in enumerate(delayed['pilot_program'])if leg['id']=='optional/arch/3')
    target=copy.deepcopy(delayed['pilot_program'][index]['target'])
    target.update(position=[1692,340],region=[1684,336,16,8])
    target['support_indices']=[i for i,p in enumerate(compiled['case']['platforms'])if abs(p[1]-358)<.01 and p[0]<=1703 and p[0]+p[2]>=1681]
    delayed['pilot_program'].insert(index+1,dict(id='timed-cache/deep-chamber',edge_id='optional/arch',kind='walk',target=target,budget_ticks=120))
    delayed['pilot_program'].insert(index+2,dict(id='timed-cache/wait-close-and-reopen',edge_id='optional/arch',kind='module',target=target,budget_ticks=360,
        control_plan=[command('axis',value=0),command('wait',90),command('shoot',direction=[0,-1]),command('wait',12)]))
    cases.append(delayed)
    return cases

def causal_check(case,result):
    if 'timed-cache-delayed-return'not in case['id']:return dict(ok=True,scope='no additional delayed-return condition')
    bell_id='arch/arch-bell';observed_closed=False;reopened=False
    for frame in result.get('frames',[]):
        state=next((b for b in frame.get('plains',{}).get('bells',[])if b['id']==bell_id),None)
        if not state:continue
        if state['open_count']==1 and not state['open'] and frame['x']>1667 and frame['y']<358:observed_closed=True
        if observed_closed and state['open_count']>=2:reopened=True
    return dict(ok=observed_closed and reopened,actual_closed_inside=observed_closed,actual_second_open=reopened)

def held_cases(nominal,seed,index,protocol):
    rng=random.Random(protocol['holdout_seed_base']+index)
    phases=[rng.random()for _ in range(protocol['holdout_trials_per_route'])]
    values=[]
    for original in nominal:
        for i,phase in enumerate(phases):
            case=copy.deepcopy(original);case['id']+='-held-'+str(i)
            for saw in case['saws']:saw['initial_phase']=phase
            for enemy in case['enemies']:enemy['initial_idle_cooldown']=.6*rng.random()
            case['ecosystem_trial']=dict(seed=seed,phase=phase,independent=True,selection_used=False)
            values.append(case)
    return values,phases

def run(name,seed,index=0,window=1.2,library_root=None,calibrate=False):
    start=time.perf_counter();out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_ecosystem_run_exists')
    out.mkdir(parents=True);protocol=json.loads(PROTOCOL.read_text());events=[]
    def emit(event,**fields):
        row=dict(sequence=len(events),event=event,**fields);events.append(row);write(out/'generation-log.json',events)
        print(json.dumps(row,ensure_ascii=False),flush=True)
    write(out/'protocol.json',dict(protocol,seed=seed,seed_index=index,gate_window=window,calibration_only=calibrate))
    # Freeze before query/generation too: even static failures retain their source.
    for p in list(Path(__file__).parent.glob('*'))+[REPO/'pcg/prototype/plains/rock_recoil.py',REPO/'pcg/map_directed/library.py']:
        if p.is_file():
            target=out/'design-source'/p.relative_to(REPO);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    graph,specs,seams,mission,old=design(seed,window)
    write(out/'mission.json',mission);write(out/'exploration.json',graph);write(out/'challenge-specifications.json',specs)
    ideas=proposals({})
    write(out/'idea-proposals.json',dict(proposals=ideas,distinct_relationships=len({r['novelty_family']for r in ideas}),
        note='Role variants are proposals, not validated Modules or distinct gameplay families'))
    library=CandidateLibrary(library_root)
    # Bootstrap from already versioned measured sources, not from an ad-hoc
    # second library. These source passes do not approve new adaptations.
    source=CandidateLibrary().find_direct_instance(old)
    if not source:raise ValueError('restore_verified_valley_complete_source_archive')
    sources={m['id']:m for m in source['modules']};modules=[];calls=0;reused=0
    for spec in specs:
        module,called=resolve(spec,library,sources[spec['node_id']],emit);calls+=int(called);reused+=int(not called)
        if calls>protocol['maximum_generator_calls_per_map']:raise ValueError('generator_budget_exhausted')
        if module is None:
            write(out/'summary.json',dict(status='unsatisfied',generator_calls=calls,reused=reused,production_admitted=False));return out
        if called:
            module=export_reload([module],out/'generated'/module['id'],producer='pcg/map_directed/ecosystem/run.py')[0]
        modules.append(module)
    modules=catalog(modules,out/'module-library')
    write(out/'effective-challenge-specifications.json',specs)
    compiled=assemble_modules(graph,modules,seams);compiled['case']['world_bounds']=[-80,50,3290,1400]
    compiled['shop']=copy.deepcopy(compiled['case']['shop_sites'][0]);compiled['unresolved_rewards']=[]
    write(out/'compiled.json',compiled);write(out/'assembly-audit.json',audit(compiled))
    write(out/'map-recipe.json',dict(seed=seed,specs=specs,seams=seams,mission=mission,
        topology_source='existing valley_complete Mission/Exploration; fixed physical topology, not independent random topologies',
        assembly_scope='isolated experiment; canonical general relations remain UNKNOWN',production_admitted=False))
    gates=gate_audit(out)
    if not gates['all_passed']:raise ValueError('closed_gate_geometry_bypass')
    nominal=nominal_cases(compiled)
    for case in nominal:case['ecosystem_seed']=seed
    held,phases=held_cases(nominal,seed,index,protocol)
    cases=nominal if calibrate else nominal+held
    write(out/'cases.json',dict(cases=cases));write(out/'holdout-selection.json',dict(frozen_before_physics=True,phases=phases,attempts=0 if calibrate else 1))
    engine=EcosystemEngine(out/'physics');rows=[]
    for case,result,evidence in engine.run(cases,'ecosystem'):
        causal=causal_check(case,result)
        row=dict(id=case['id'],held='ecosystem_trial'in case,ok=result['ok']and causal['ok'],physics_reason=result['reason'],reason=result['reason']if causal['ok']else'delayed_return_not_demonstrated',causal_witness=causal,
            ticks=result.get('ticks'),shots=result.get('shots'),failure=result.get('pilot',{}).get('failure',{}),
            actual_rewards=result.get('extra',{}).get('optional_challenge_events',[]),
            actual_purchases=result.get('extra',{}).get('shop_events',[]),evidence=evidence)
        rows.append(row);write(out/'rows.json',rows)
        print(json.dumps({k:row[k]for k in ['id','ok','reason','ticks','shots']},ensure_ascii=False),flush=True)
    passed=len(rows)==len(cases)and all(r['ok']for r in rows)
    summary=dict(schema='pcg/ecosystem-map-result/v1',seed=seed,status='calibration_only'if calibrate else'whole_map_candidate_passed'if passed else'whole_map_failed',
        all_passed=passed,rows=rows,generator_calls=calls,reused_modules=reused,modules=len(modules),
        nominal_cases=len(nominal),held_cases=0 if calibrate else len(held),wall_seconds=time.perf_counter()-start,
        human_fun='unreviewed',production_admitted=False,larger_region_goal_met=False,
        topology_diversity_claim=False,calibration_only=calibrate)
    write(out/'summary.json',summary)
    if passed and not calibrate:
        records=library.enroll_payloads(out)if calls else [library.find_payload(s,isolated_experiment=True)[0]['record']for s in specs]
        write(out/'candidate-enrollment.json',dict(records=records,status='scoped candidate only',production_admitted=False))
        emit('candidate_payloads_indexed',records=len(records),production_admitted=False)
    else:emit('admission_blocked',reason='calibration is not holdout evidence'if calibrate else'real whole-map failure',retry=False)
    return out

def batch(name):
    protocol=json.loads(PROTOCOL.read_text());root=REPO/'pcg/results'/name
    if root.exists():raise ValueError('immutable_ecosystem_batch_exists')
    root.mkdir(parents=True);library=root/'library';runs=[]
    for i,(seed,window)in enumerate(zip(protocol['seeds'],protocol['gate_windows_seconds'])):
        try:path=run(name+'/maps/'+str(i),seed,i,window,library)
        except Exception as error:
            write(root/'summary.json',dict(runs=runs,all_passed=False,completed=len(runs),failed_seed=seed,
                failure_class='infrastructure_or_contract_error',error=type(error).__name__+': '+str(error),retry=False))
            raise
        summary=json.loads((path/'summary.json').read_text());runs.append(dict(path=str(path.relative_to(REPO)),summary=summary))
        write(root/'summary.json',dict(runs=runs,all_passed=False,completed=len(runs)))
        if not summary.get('all_passed'):return root
    passed=all(r['summary']['all_passed']for r in runs)
    reuse=[r['summary']['generator_calls']for r in runs]
    write(root/'summary.json',dict(schema='pcg/ecosystem-stability-result/v1',runs=runs,all_passed=passed,
        generator_calls=reuse,expected_generator_calls=[8,0,1],reuse_policy_passed=reuse==[8,0,1],
        physical_topologies=1,scope=protocol['scope'],human_fun='unreviewed',production_admitted=False))
    return root

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--name',required=True)
    parser.add_argument('--batch',action='store_true');parser.add_argument('--seed',default='ecology-calibration')
    parser.add_argument('--window',type=float,default=1.2);parser.add_argument('--calibrate',action='store_true')
    args=parser.parse_args();result=batch(args.name)if args.batch else run(args.name,args.seed,window=args.window,calibrate=args.calibrate)
    print(result)
    if not json.loads((result/'summary.json').read_text()).get('all_passed'):raise SystemExit(2)
