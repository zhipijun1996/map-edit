"""Finite persistent production loop on existing Engine/evaluator/export/library.

Codex authors new recipe code between runs. Programs search its declared finite
domain. Exhausted/unsupported ideas become needs_design, never renamed variants.
"""
import argparse,copy,json,shutil,subprocess,time
from pathlib import Path
from .engine import ROOT,HERE,WorkshopEngine
from .experiments import write,produce,REPO
from .production_recipes import RECIPES,candidates,specification,purpose,alternatives
from .evaluate import instantiate,evaluate
from .library import WorkshopLibrary
from ..factory.core.quality import digest,module_hash
from ..factory.core.engine import file_sha
from pcg.contract.export import collect

def compile_request(request):
    if request.get('recipe')=='ordered-interface/v1':
        from pcg.map_directed.graph_map.verify_pairs import proposals
        return dict(status='requires_macro_physics',modules=proposals([request['module']]),gaps=[],production_admitted=False)
    if request.get('recipe')=='rigid-mirror/v1':
        from pcg.map_directed.content_domains.mirror import mirror
        return dict(status='requires_macro_physics',modules=[mirror(request['module'])],gaps=[],production_admitted=False)
    if request.get('recipe')=='map-budget-binding/v1':
        from .map_budget import configure
        return configure(request)
    if request.get('recipe')=='bellstrider-court/v1':
        from pcg.map_directed.graph_map.boss_content import bellstrider
        if request.get('ports',{}).get('count')!=1:return dict(status='needs_design',gaps=['original Boss court exposes one exterior Port'])
        return dict(status='requires_macro_physics',modules=[bellstrider()],gaps=[],production_admitted=False)
    recipe=request.get('recipe')
    if recipe=='branch-terraces/v1':
        from pcg.prototype.plains.branch_terraces import request as local_macro
        return local_macro(request)
    if recipe not in RECIPES:return dict(status='needs_design',gaps=['missing executable recipe: '+str(recipe)],searched=list(RECIPES),cases=[])
    interfaces=request.get('interfaces',[0,1])
    if not isinstance(interfaces,list)or not interfaces or len(interfaces)>2 or any(type(i)is not int or i not in (0,1)for i in interfaces)or len(set(interfaces))!=len(interfaces):return dict(status='unsatisfied',gaps=['outside registered interface domain [0,1]'],cases=[])
    specs=[specification(recipe,i)for i in interfaces]
    if request.get('specifications')is not None and request['specifications']!=specs:return dict(status='unsatisfied',gaps=['mechanical Challenge Specification mismatch; no substitutions'],supported=specs,cases=[])
    cs=[]
    for i,s in zip(interfaces,specs):
        choices=candidates(recipe,i)
        if len(choices)>4:return dict(status='unsatisfied',gaps=['recipe exceeds fixed four-control-candidates budget'],cases=[])
        for c in choices:
            c['map_specification']=s;c['idea_ids']=['production-proposal/'+recipe];cs.append(c)
    return dict(status='requires_physics',specifications=specs,cases=cs)

def static_preflight(engine,cases):
    """Original schema/contract and obvious source invariants, not a simulator."""
    clones=[]
    for c in cases:
        if len({r['id']for r in c['reward_sites']})!=len(c['reward_sites']):raise ValueError('duplicate_reward_transaction_id')
        for p in [c['entry_port'],c['exit_port']]:
            if not any(p[0]-12>=x and p[0]+12<=x+w and abs(p[1]+18-y)<.1 for x,y,w,h in c['platforms']):raise ValueError('port_body_not_supported')
        v=copy.deepcopy(c);v['factory_id']=digest(c);clones.append(v)
    write(engine.out/'preflight-cases.json',dict(cases=clones))
    write(engine.out/'preflight-bundle.json',dict(rows=collect(engine.out/'preflight-cases.json'),sourceCommit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip()))
    subprocess.run(['node',str(HERE/'export.mjs'),str(engine.out/'preflight-bundle.json'),str(engine.out/'preflight-documents')],check=True,cwd=REPO,capture_output=True)

def run(name,requests=None,cycles=4,library_root=None,compiler=None,checker=None,counter_builder=None,source_file=None,extra_sources=None,runner_script=None,export_script=None):
    root=ROOT/'results'/name
    if root.exists():raise ValueError('immutable_production_run_exists')
    root.mkdir(parents=True);protocol=json.loads((HERE/'production-protocol-v2.json').read_text())
    compile_fn=compiler or compile_request;check_fn=checker or purpose;alt_fn=counter_builder or alternatives;rule_source=Path(source_file or HERE/'production_recipes.py')
    if not 1<=cycles<=protocol['maximum_rounds']:raise ValueError('round_budget_outside_protocol')
    requests=requests if requests is not None else [dict(recipe='refund-turnback'),dict(recipe='bell-floor-drop'),dict(recipe='refund-turnback',purpose='persistent reuse probe'),dict(recipe='unregistered-new-idea',implemented=True)]
    requests=requests[:cycles];write(root/'protocol.json',dict(protocol,requests=requests));ledger=[];blocked=set();batch_start=time.perf_counter();parent_families=set()
    library_root=Path(library_root or ROOT/'map_directed/library');library=WorkshopLibrary(library_root)
    for index,request in enumerate(requests):
        started=time.perf_counter();response=compile_fn(request);row=dict(round=index,recipe=request.get('recipe'),source_status=response['status'],new_candidates=0,reused=0,physics_cases=0,stage='request',failures=[])
        def done(stage):
            if stage in ('rejected_before_full_validation','needs_revision','holdout_failed'):
                notice=ROOT/'feedback/workshop'/('production-'+failure_key+'.json')
                if not notice.exists():write(notice,dict(schema='pcg/production-rule-feedback/v1',type='technical_experiment',production_recipe=request['recipe'],rule_source_sha256=file_sha(rule_source),failure_key=failure_key,flag='unneeded_mechanic'if stage=='rejected_before_full_validation'else'controls_issue',source_run=str(engine.out.relative_to(REPO)),failures=row['failures'],stage=stage,next_revision='new executable recipe/source revision required; a title or seed change does not clear feedback'))
            row['stage']=stage;row['wall_seconds']=time.perf_counter()-started;ledger.append(copy.deepcopy(row));write(root/'ledger.json',ledger);print(json.dumps(row),flush=True)
        if response['status']!='requires_physics':row['failures']=response['gaps'];done(response['status']);continue
        parent_families.update(c.get('parent_family',c['family'])for c in response['cases'])
        specs=response['specifications'];failure_key=digest(dict(rule_source=file_sha(rule_source),specifications=specs))
        notice=ROOT/'feedback/workshop'/('production-'+failure_key+'.json')
        if notice.exists():row['failures']=[dict(reason='persisted same-source failure; revise rule before spending new budget',feedback=str(notice.relative_to(REPO)))];done('blocked_by_feedback');continue
        hits=[library.find_single_exact(s)for s in specs]
        if all(hits):
            row['reused']=len(hits);row['versions']=[h[0]['record']['contentVersion']for h in hits];done('reused_from_disk');continue
        if request['recipe']in blocked:row['failures']=['same recipe/source rejected earlier; new rule revision required'];done('blocked_by_feedback');continue
        engine=WorkshopEngine(root/f'round-{index:02d}',extra_sources=[rule_source]+list(extra_sources or []),runner_script=runner_script);cal_seed=protocol['calibration_seed']+index*protocol['round_seed_stride'];held_seed=protocol['holdout_seed']+index*protocol['round_seed_stride']
        write(engine.out/'protocol.json',dict(protocol,calibration_seed=cal_seed,holdout_seed=held_seed,request=request))
        source=response['cases'];write(engine.out/'source-candidates.json',dict(cases=source));static_preflight(engine,source)
        # No source edits from this point until the complete round has stopped.
        clean=[];clean_witnesses={};screen_rows=[];owner={};expanded=[]
        for c,r,e in engine.run(source,'clean-screen'):
            p=check_fn(c,r);screen_rows.append(dict(id=c['id'],stage='clean',ok=p['ok'],purpose=p,evidence=e))
            if p['ok']:clean.append(c);clean_witnesses[c['id']]=dict(case=c,result=r,evidence=e)
        for c in clean:
            for i in range(protocol['screen_mild_trials']):
                v=instantiate(c,cal_seed,'mild',i);expanded.append(v);owner[v['id']]=c['id']
        for c,r,e in engine.run(expanded,'mild-screen'):
            p=check_fn(c,r);screen_rows.append(dict(id=owner[c['id']],stage='mild',ok=p['ok'],purpose=p,evidence=e))
        write(engine.out/'screen.json',screen_rows);chosen=[]
        for s in specs:
            cs=[c for c in clean if c['map_specification']['id']==s['id']]
            scored=[(sum(r['ok']for r in screen_rows if r['id']==c['id']and r['stage']=='mild'),-i,c)for i,c in enumerate(cs)]
            scored.sort(key=lambda x:(-x[0],-x[1]))
            if scored and scored[0][0]>=protocol['screen_minimum_valid']:chosen.append(scored[0][2])
        if not chosen:
            blocked.add(request['recipe']);row['physics_cases']=engine.sim.cases;row['failures'].append('no candidate passed equal-budget clean/mild screening');done('needs_revision');continue
        counter_cs=[v for c in chosen for v in alt_fn(c)];counter_rows=[];counter_decisions={}
        for c,r,e in engine.run(counter_cs,'counterexample'):
            cp=check_fn(c,r);invalidates=bool(r['ok'])and not cp['ok']
            counter_decisions[c['id']]=dict(safe_stable=bool(r['ok']),invalidates_design=invalidates,design_check=cp,evidence=e)
            counter_rows.append(dict(id=c['id'],base_id=c['id'].split('-counter-')[0],kind=c['counterexample_kind'],safe_stable=bool(r['ok']),invalidates_design=invalidates,coins=r.get('workshop',{}).get('coins'),shots=r.get('shots'),evidence=e))
        write(engine.out/'counterexamples.json',counter_rows)
        bad={r['base_id']for r in counter_rows if r['invalidates_design']};safe=[c for c in chosen if c['id']not in bad]
        row['failures']+=[dict(stage='cheap_counterexample',case=c['id'],witnesses=[r['id']for r in counter_rows if r['invalidates_design']and r['base_id']==c['id']])for c in chosen if c['id']in bad]
        if not safe:
            blocked.add(request['recipe']);row['physics_cases']=engine.sim.cases;done('rejected_before_full_validation');continue
        cal=evaluate(engine,safe,cal_seed,12,'calibration',purpose_fn=check_fn)
        shutil.copy2(engine.out/'evaluations.json',engine.out/'calibration-evaluations.json')
        selected=[e['case']for e in cal if e['quality_gate']['status']=='awaiting_human_review']
        write(engine.out/'selection-before-holdout.json',dict(cases=[c['id']for c in selected],calibration_sha256=file_sha(engine.out/'calibration-evaluations.json'),counterexamples_sha256=file_sha(engine.out/'counterexamples.json'),holdout_seed=held_seed))
        if not selected or time.perf_counter()-started>protocol['maximum_round_wall_seconds']:
            blocked.add(request['recipe']);row['physics_cases']=engine.sim.cases;row['failures'].append('calibration gate or round time budget');done('needs_revision');continue
        selected_specs=[s for s in specs if any(c['map_specification']['id']==s['id']for c in selected)]
        rel=str(engine.out.relative_to(ROOT/'results'))
        produce(rel,list({c['family']for c in selected}),rel,requested=(selected_specs,selected),protocol_override=str(engine.out/'protocol.json'),engine=engine,purpose_fn=check_fn,library_root=library_root,canonical_witnesses=clean_witnesses,counter_decisions=counter_decisions,export_script=export_script)
        matches=[WorkshopLibrary(library_root).find_single_exact(s)for s in selected_specs]
        row['new_candidates']=sum(bool(m)for m in matches);row['versions']=[m[0]['record']['contentVersion']for m in matches if m];row['physics_cases']=engine.sim.cases
        if row['new_candidates']<len(specs):blocked.add(request['recipe'])
        done('candidate_ready'if row['new_candidates']else'holdout_failed')
    summary=dict(schema='pcg/workshop-production-batch/v2',rounds=len(ledger),library_root=str(library_root.relative_to(REPO)),new_candidates=sum(r['new_candidates']for r in ledger),reused=sum(r['reused']for r in ledger),unique_reused_versions=sorted({v for r in ledger if r['reused']for v in r.get('versions',[])}),physics_cases=sum(r['physics_cases']for r in ledger),wall_seconds=time.perf_counter()-batch_start,
        parent_families=sorted(parent_families),confirmed_new_action_families=0,proposed_relationships=sorted({r.get('recipe','UNKNOWN')for r in requests}),production_admitted=False,online_model_service=False,stop_reason='request budget exhausted; unsupported or failed recipes require Codex/human design and executable revision',ledger=ledger)
    write(root/'summary.json',summary);print(json.dumps(summary),flush=True);return root

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--cycles',type=int,default=4);p.add_argument('--requests');p.add_argument('--library-root');a=p.parse_args();run(a.name,json.loads(Path(a.requests).read_text())if a.requests else None,a.cycles,a.library_root)
