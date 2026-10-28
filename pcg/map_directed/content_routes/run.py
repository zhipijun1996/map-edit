"""Bounded challenge adaptation with existing library, contracts and Harness."""
import argparse,copy,json,random,shutil,time
from pathlib import Path
from ..director import REPO
from ..run import write
from ..woven_region.run import WovenEngine,cases_for,causal_check
from ..direct_join.canonical import export_reload
from ..direct_join.assemble import assemble_modules
from ..direct_join.audit import audit
from ..ecosystem.run import catalog
from ..library import CandidateLibrary
from pcg.prototype.plains.content_routes import adapt
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest

HERE=Path(__file__).parent

class ContentEngine(WovenEngine):
    def __init__(self,out):
        super().__init__(out)
        art=REPO/'pcg/research/content-routes-hazard-art.json'
        extra=[art]
        for record in json.loads(art.read_text())['files']:
            p=REPO/'pcg/prototype/godot'/record['path']
            if file_sha(p)!=record['sha256']:raise ValueError('hazard_art_binding_drift')
            extra.append(p)
        for p in list(HERE.glob('*'))+extra+[REPO/'pcg/prototype/plains/content_routes.py',REPO/'pcg/map_directed/direct_join/canonical.py']:
            if p.is_file()and p.suffix in ['.py','.json','.gd','.tscn','.tres','.png','.import']:
                rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p)
                q=self.out/'source_snapshot'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
        self.binding.update(source_files=self.hashes,source_manifest_sha256=digest(self.hashes))
        self.sim.runner_script=str(HERE/'runner.gd');self.binding['runner']=self.sim.runner_script
        write(self.out/'source_binding.json',self.binding)


def build(out,library_root=None):
    source=REPO/'pcg/results/woven-release-v1';parent=json.loads((source/'compiled.json').read_text())
    protocol=json.loads((HERE/'protocol.json').read_text());demands=protocol['content_demands'];library=CandidateLibrary(library_root)
    modules=[];events=[];calls=0;reused=0
    # Requirements are frozen before adaptation, not inferred from a success.
    specs=[]
    for old in parent['modules']:
        spec=copy.deepcopy(old['spec'])
        if old['id']in demands:
            spec['id']='content-routes-v1/'+old['id'];spec['design_contract']['challenge']=demands[old['id']]
            spec['objective']=demands[old['id']]['decision'];spec['budget']=dict(generator_candidates=1,local_retries=0)
        specs.append(spec)
    write(out/'challenge-specifications.json',specs)
    for old,spec in zip(parent['modules'],specs):
        matches=library.find_payload(spec,isolated_experiment=True)if library_root else []
        events.append(dict(event='module_query',node=old['id'],exact_matches=len(matches)))
        if matches:
            m=matches[0]['module'];reused+=1;events.append(dict(event='module_reused',node=old['id'],record=matches[0]['record']))
        elif old['id']in demands:
            events.append(dict(event='library_gap',node=old['id'],challenge=demands[old['id']]))
            try:m=adapt(old,spec)
            except ValueError as error:
                events.append(dict(event='unsatisfied',node=old['id'],reason=str(error),retry=False,generic_fallback=False));write(out/'generation-events.json',events);raise
            m=export_reload([m],out/'generated'/m['id'],producer='pcg/prototype/plains/content_routes.py')[0];calls+=1
            events.append(dict(event='challenge_adapted',node=m['id'],status='requires_fresh_whole_map_physics'))
        else:
            m=copy.deepcopy(old);reused+=1;events.append(dict(event='verified_parent_payload_reused',node=m['id'],version=m['content_version'],evidence=str((source/'summary.json').relative_to(REPO))))
        modules.append(m);write(out/'generation-events.json',events)
    modules=catalog(modules,out/'module-library')
    from ..direct_join.director import requests
    _,_,seams=requests(source/'layout.json')
    c=assemble_modules(parent['exploration_graph'],modules,seams)
    for gate in c['gate_specs']:gate.update(zip(['x','y','w','h'],gate['bounds']))
    c['shop']=copy.deepcopy(c['case']['shop_sites'][0]);c['unresolved_rewards']=[]
    c['source'].update(content_policy='challenge-before-travel/v1',parent_compiled_sha256=file_sha(source/'compiled.json'))
    for f in ['layout.json','mission.json','exploration.json']:shutil.copy2(source/f,out/f)
    write(out/'compiled.json',c);write(out/'assembly-audit.json',audit(c))
    write(out/'generation-log.json',dict(reused=reused,generator_calls=calls,demands=len(demands),map_added_terrain=0,generic_fallbacks=0))
    write(out/'map-recipe.json',dict(schema='pcg/content-routes-recipe/v1',parent=str(source.relative_to(REPO)),parent_sha256=file_sha(source/'compiled.json'),protocol=protocol,production_admitted=False))
    return c


def run(name,mode='routes',held=False,source=None,library_root=None):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_content_run_exists')
    out.mkdir(parents=True);start=time.perf_counter();protocol=json.loads((HERE/'protocol.json').read_text());write(out/'protocol.json',dict(protocol,mode=mode,held=held))
    # Freeze even contract/materialization failures.
    for p in list(HERE.glob('*'))+[REPO/'pcg/prototype/plains/content_routes.py',REPO/'pcg/map_directed/direct_join/assemble.py',REPO/'pcg/map_directed/direct_join/canonical.py']:
        if p.is_file():
            dest=out/'design-source'/p.relative_to(REPO);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
    try:
        if source:
            c=json.loads((Path(source)/'compiled.json').read_text());write(out/'compiled.json',c)
        else:c=build(out,library_root)
        cases=cases_for(c,'cover')[2:3]if mode=='depletion'else cases_for(c,mode)
        for case in cases:case['title']='风铃平原 · 风隙回响 · 内容驱动整图'
        if held:
            rng=random.Random(protocol['holdout_seed']);new=[]
            for original in cases[:4]:
                for i in range(protocol['holdout_trials_per_route']):
                    v=copy.deepcopy(original);v['id']+='-content-held-'+str(i)
                    v['noise']=dict(seed=rng.randrange(2**30),timing_frames=1,aim_degrees=1)
                    for e in v['enemies']:e['initial_idle_cooldown']=rng.uniform(.2,.6)
                    v['holdout']=True;new.append(v)
            cases+=new
        write(out/'cases.json',dict(cases=cases));engine=ContentEngine(out/'physics');rows=[]
        for case,result,evidence in engine.run(cases,'content-'+mode):
            causal=causal_check(case,result);f=result.get('pilot',{}).get('failure')or{}
            row=dict(id=case['id'],ok=result['ok']and causal['ok'],reason=result['reason'],ticks=result.get('ticks'),shots=result.get('shots'),failure=f,extra=result.get('extra'),evidence=evidence)
            if case.get('counterfactual'):
                omitted=next(i for i,l in enumerate(case['pilot_program'])if l['id']==case['counterfactual']['omitted_leg']);row['reached_counterfactual_leg']=result.get('pilot',{}).get('legs_completed',0)>=omitted
            rows.append(row);write(out/'rows.json',rows)
            print(json.dumps(dict(id=row['id'],ok=row['ok'],ticks=row['ticks'],shots=row['shots'],reason=row['reason'],leg=f.get('leg_id'),position=f.get('actual',{}).get('position')),ensure_ascii=False),flush=True)
        write(out/'summary.json',dict(all_passed=len(rows)==len(cases)and all(r['ok']for r in rows),rows=rows,held=held,wall_seconds=time.perf_counter()-start,
            counterfactual_expectations_met=mode=='negative'and all(not r['ok']and r.get('reached_counterfactual_leg')for r in rows),human_fun='unreviewed',production_admitted=False))
    except Exception as error:
        import traceback
        write(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc()));raise
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mode',default='routes',choices=['main','routes','all','cover','negative','depletion']);p.add_argument('--held',action='store_true');p.add_argument('--source');p.add_argument('--library');a=p.parse_args();out=run(a.name,a.mode,a.held,a.source,a.library);print(out)
    if not json.loads((out/'summary.json').read_text())['all_passed']and a.mode!='negative':raise SystemExit(2)
