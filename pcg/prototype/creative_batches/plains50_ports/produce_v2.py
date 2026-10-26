"""Multi-route orchestration through ORIGINAL evaluator/producer/store only."""
import argparse,copy,json,time
from pathlib import Path
from . import recipes_v2 as recipes
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write,produce,REPO
from pcg.prototype.workshop.production_loop import static_preflight
from pcg.prototype.workshop.evaluate import instantiate,evaluate
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest

HERE=Path(__file__).parent
def external_outcome(c,r):
    required=[]
    if c['challenge_route']:
        required=['left-cache' if c['production_recipe']=='refund-fork' and c['route_spec']['to_port']=='D' else 'visible-cache']
    claimed={e['id'] for e in r.get('workshop',{}).get('events',[]) if e.get('type')=='chest_claim' and e.get('accepted')}
    return dict(ok=bool(r.get('ok')) and set(required)<=claimed,required_reward_ids=required,claimed_reward_ids=sorted(claimed),coins=r.get('workshop',{}).get('coins',0))

def counter_cases(c):
    if c['challenge_route']:return recipes.alternatives(c)
    clone=copy.deepcopy(c);clone['family']='safe-branch'
    rows=recipes.alternatives(clone)
    for row in rows:row['family']=c['family']
    return rows

def run(name,only=None,interfaces=None,*,recipe_module=None,export_script=None,protocol_config=None,extra_sources=None,outcome_checker=None):
    """Reuse this orchestration for registered local recipes; original defaults stay frozen."""
    rules=recipe_module or recipes
    exporter=Path(export_script or HERE/'export_v1.mjs')
    config=dict(calibration_seed=261026502,holdout_seed=261026503,maximum_cases_per_proposal=900,maximum_source_revisions=2)
    config.update(protocol_config or {})
    calibration_seed=config['calibration_seed'];holdout_seed=config['holdout_seed'];maximum_cases=config['maximum_cases_per_proposal']
    if calibration_seed==holdout_seed or maximum_cases<1:raise ValueError('invalid fixed protocol')
    alt_fn=rules.alternatives if recipe_module else counter_cases
    outcome_fn=outcome_checker or external_outcome
    root=ROOT/'results'/name
    if root.exists():raise ValueError('immutable multiport production batch')
    root.mkdir(parents=True);ledger=[]
    requested=list(only or rules.RECIPES);wanted_interfaces=list(interfaces if interfaces is not None else [0,1])
    write(root/'protocol.json',dict(schema='pcg/plains50-multiport-protocol/v1',recipes=requested,calibration_seed=calibration_seed,holdout_seed=holdout_seed,seed_stride=1009,maximum_source_revisions=config['maximum_source_revisions'],maximum_cases_per_proposal=maximum_cases,screen_mild=6,screen_minimum_valid=5,regular_policy='original unchanged',minimum_counters_per_route=18,canonical_witness='clean exact input fixed before holdout',selection='all declared outlets must qualify; optional via routes are still individually qualified',human_approval='UNKNOWN'))
    for recipe in requested:
        index=rules.RECIPES.index(recipe)
        started=time.perf_counter();engine=WorkshopEngine(root/recipe,extra_sources=[Path(__file__),Path(rules.__file__),exporter]+list(extra_sources or []))
        sources=[c for i in wanted_interfaces for c in rules.layouts(recipe,i)];specs=[next(c['map_specification']for c in sources if c['interface']==i)for i in wanted_interfaces]
        write(engine.out/'protocol.json',dict(schema='pcg/content-workshop-protocol/v1',calibration_seed=calibration_seed+index*1009,holdout_seed=holdout_seed+index*1009,maximum_actual_cases=maximum_cases,selection='single authored geometry/program per interface/route; clean/mild+counter gate; original regular calibration then independent holdout'))
        write(engine.out/'source-candidates.json',dict(cases=sources));static_preflight(engine,sources)
        clean={};screen=[]
        for c,r,e in engine.run(sources,'clean-screen'):
            p=rules.purpose(c,r);screen.append(dict(id=c['id'],level='clean',ok=p['ok'],purpose=p,evidence=e))
            if p['ok']:clean[c['id']]=dict(case=c,result=r,evidence=e)
        mild=[instantiate(c,calibration_seed+index*1009,'mild',i)for c in sources if c['id']in clean for i in range(6)]
        for c,r,e in engine.run(mild,'mild-screen'):
            owner=c['id'].rsplit('-mild-',1)[0];p=rules.purpose(c,r);screen.append(dict(id=owner,level='mild',ok=p['ok'],purpose=p,evidence=e))
        write(engine.out/'screen.json',screen)
        chosen=[c for c in sources if c['id']in clean and sum(v['ok']for v in screen if v['id']==c['id']and v['level']=='mild')>=5]
        # A candidate needs ALL listed route programs and all declared branches.
        for interface in range(2):
            wanted={c['id']for c in sources if c['interface']==interface};got={c['id']for c in chosen if c['interface']==interface}
            if wanted!=got:chosen=[c for c in chosen if c['interface']!=interface]
        decisions={};counter_rows=[]
        for c,r,e in engine.run([v for c in chosen for v in alt_fn(c)],'counterexample'):
            cp=rules.purpose(c,r);outcome=outcome_fn(c,r);invalid=outcome['ok']and not cp['ok'];decisions[c['id']]=dict(safe_stable=bool(r['ok']),same_external_outcome=outcome,invalidates_design=invalid,design_check=cp,evidence=e)
            counter_rows.append(dict(id=c['id'],base_id=c['id'].split('-counter-')[0],kind=c['counterexample_kind'],safe_stable=bool(r['ok']),invalidates_design=invalid,evidence=e))
        write(engine.out/'counterexamples.json',counter_rows)
        bad={r['base_id']for r in counter_rows if r['invalidates_design']}
        invalid_interfaces={c['interface']for c in chosen if c['id']in bad};chosen=[c for c in chosen if c['interface']not in invalid_interfaces]
        entries=evaluate(engine,chosen,calibration_seed+index*1009,12,'calibration',purpose_fn=rules.purpose)if chosen else[]
        write(engine.out/'calibration-evaluations.json',entries)
        selected=[e['case']for e in entries if e['quality_gate']['status']=='awaiting_human_review']
        for interface in range(2):
            wanted={c['id']for c in chosen if c['interface']==interface};got={c['id']for c in selected if c['interface']==interface}
            if wanted!=got:selected=[c for c in selected if c['interface']!=interface]
        write(engine.out/'selection-before-holdout.json',dict(case_ids=[c['id']for c in selected],calibration_sha256=file_sha(engine.out/'calibration-evaluations.json'),counterexamples_sha256=file_sha(engine.out/'counterexamples.json'),holdout_seed=holdout_seed+index*1009))
        versions=[]
        if selected:
            rel=str(engine.out.relative_to(ROOT/'results'));selected_specs=[s for s in specs if any(c['map_specification']['id']==s['id']for c in selected)]
            produce(rel,[selected[0]['family']],rel,requested=(selected_specs,selected),protocol_override=str(engine.out/'protocol.json'),engine=engine,purpose_fn=rules.purpose,library_root=ROOT/'map_directed/library',canonical_witnesses=clean,counter_decisions=decisions,export_script=exporter)
            reviews=json.loads((engine.out/'review_cases.json').read_text())['cases'];held=json.loads((engine.out/'evaluations.json').read_text())
            manifest=json.loads((engine.out/'modules/manifest.json').read_text())if (engine.out/'modules/manifest.json').exists()else dict(modules=[])
            lib=WorkshopLibrary(ROOT/'map_directed/library')
            for item in manifest['modules']:
                cs=[c for c in reviews if c['layout_uid']==item['id'].removeprefix('generated-')]
                original=[c for c in selected if c['layout_uid']==item['id'].removeprefix('generated-')]
                if len(cs)!=len(original):continue
                qualities=[e['quality_gate']for e in held if any(c['factory_id']==digest(e['case'])for c in cs)]
                artifacts=[dict(path=str(p.relative_to(REPO)),sha256=file_sha(p))for p in [engine.out/'evaluations.json',engine.out/'calibration-evaluations.json',engine.out/'protocol.json',engine.out/'bound-counterexamples.json',engine.out/'counter-decisions.json',engine.out/'selection-before-holdout.json']]
                record=lib.enroll_multi(cs,engine.out/'modules'/item['file'],cs[0]['map_specification'],qualities,artifacts)
                found=WorkshopLibrary(ROOT/'map_directed/library').find_multi(cs[0]['map_specification']);assert any(m['record']['contentVersion']==record['contentVersion']for m in found)
                versions.append(record['contentVersion'])
        row=dict(recipe=recipe,versions=versions,new_modules=len(versions),actual_physics_cases=engine.sim.cases,wall_seconds=time.perf_counter()-started,calibration_routes=len(entries),known_counter_refutations=[r['id']for r in counter_rows if r['invalidates_design']],failed_screen_routes=[c['id']for c in sources if c['id']not in clean or sum(v['ok']for v in screen if v['id']==c['id']and v['level']=='mild')<5],human_quality='unreviewed',production_admitted=False)
        assert row['actual_physics_cases']<=maximum_cases,'predeclared case budget exceeded'
        ledger.append(row);write(root/'ledger.json',ledger);print(json.dumps(row),flush=True)
        if len(versions)<len(wanted_interfaces):write(ROOT/'feedback/workshop'/f'plains50-ports-{recipe}-objective-fix-v1.json',dict(schema='pcg/production-rule-feedback/v1',production_recipe=recipe,rule_source_sha256=file_sha(Path(rules.__file__)),type='technical_experiment',stage='needs_design',flag='unexpected_shortcut'if row['known_counter_refutations']else'controls_issue',source_run=str(engine.out.relative_to(REPO)),actual_result=row,next_revision='new predeclared proposal/geometry required; retain all known counterexamples and original regular gate'))
    write(root/'summary.json',dict(schema='pcg/plains50-multiport-batch/v1',new_modules=sum(r['new_modules']for r in ledger),physics_cases=sum(r['actual_physics_cases']for r in ledger),ledger=ledger,production_admitted=False))
    return root
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--recipes',nargs='+',choices=recipes.RECIPES);p.add_argument('--interfaces',nargs='+',type=int,choices=[0,1]);a=p.parse_args();run(a.name,a.recipes,a.interfaces)
