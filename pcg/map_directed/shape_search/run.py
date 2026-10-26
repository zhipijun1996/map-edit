"""Existing canonical/assembler/Harness consumers for searched real Macro poses."""
import argparse,copy,json,random,shutil,time
from pathlib import Path
from .catalog import load
from .search import search,translated
from ..director import REPO
from ..run import write
from ..direct_join.canonical import export_reload
from ..direct_join.assemble import assemble_modules
from ..direct_join.audit import audit
from ..valley_complete.run import CompleteEngine
from ..valley_complete.rock_run import cases_for
from ..ecosystem.run import causal_check
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest

HERE=Path(__file__).parent
class ShapeEngine(CompleteEngine):
    def __init__(self,out):
        super().__init__(out,formal_style=True)
        art=REPO/'pcg/research/shape-search-art-closure.json';paths=list(HERE.glob('*'))+[art]
        for item in json.loads(art.read_text())['files']:
            p=REPO/'pcg/prototype/godot'/item['path']
            if file_sha(p)!=item['sha256']:raise ValueError('formal_art_closure_drift/'+item['path'])
            paths.append(p)
        for name in ['underworld_scenery.gd','underworld_local_composition.gd','grounded_contact.gd','underworld_presentation.gd','underworld_foreground.gd','underworld_windmill.gd']:
            paths.append(REPO/'pcg/prototype/godot/scripts/underworld_plains'/name)
        for p in paths:
            if p.is_file()and p.suffix in ['.py','.json','.gd','.tscn','.png','.import','.mp3']:
                rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p);q=self.out/'source_snapshot'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
        self.binding.update(source_files=self.hashes,source_manifest_sha256=digest(self.hashes));write(self.out/'source_binding.json',self.binding)

def build(out,seed,mode='shape_action'):
    g,domains,binding=load();protocol=json.loads((HERE/'protocol.json').read_text())
    write(out/'catalog-binding.json',binding)
    write(out/'candidate-catalog.json',dict(graph=g,domains=domains,source_positions_removed=True))
    result=search(g,domains,seed,mode,protocol['maximum_search_expansions'],protocol['capabilities'])
    modules=result.pop('modules',[]);write(out/'search.json',result)
    if not modules:return None
    # Pure rigid placement; every source template is canonical before assembly.
    for m in modules:
        m['spec']['design_contract']=dict(role=m['spec']['node']['role'],relationships=m['spec'].get('design_contract',{}).get('relationships',[]),shape_variant=m['variant_id'],motion_contract=m['motion_contract'])
        m['spec']['id']='shape-search/'+m['id']
    modules=export_reload(modules,out/'module-library',producer='pcg/map_directed/shape_search/catalog.py')
    seams=[dict(id=e['id'],kind=next(m for m in modules if m['id']==e['from'])['ports'][e['id']]['kind'])for e in g['edges']]
    c=assemble_modules(g,modules,seams);c['shop']=copy.deepcopy(c['case']['shop_sites'][0]);c['unresolved_rewards']=[]
    c['exploration_graph']['seed']=seed
    write(out/'compiled.json',c);write(out/'assembly-audit.json',audit(c))
    write(out/'map-recipe.json',dict(seed=seed,mode=mode,source=binding,search={k:v for k,v in result.items()if k not in ['trace','rejections']},production_admitted=False))
    write(out/'generation-log.json',dict(source_template_roles=8,finite_template_variants=sum(map(len,domains.values())),selected=len(modules),map_added_terrain=0,
        shape_search=True,original_placements_consumed=False,template_creation_before_search=True,source_challenge_cores_scaled=False))
    return c

def prepare_cases(c,mode='full'):
    cases=cases_for(c,'full')
    if mode=='main':cases=cases[:1]
    if mode=='lower':cases=cases[-2:]
    if mode=='reward':cases=cases[2:3]
    identities={'west':'windmill_plateau','ridge':'windmill_plateau','lookout':'repair_gallery','arch':'clock_court','east':'windmill_plateau','hollow':'creek_well','bell':'creek_well','relay':'clock_court'}
    for v in cases:
        v.update(title='风铃平原 · 岩谷空间搜索 · 实际完整地图',extra_script=str(HERE/'mechanics.gd'),map_seed=c['exploration_graph']['seed'])
        v['presentation_areas']=[dict(id=k,identity=identities[k],position=n['center']['position'])for k,n in c['nodes'].items()]
        v['presentation_keep_clear']=[translated(r,m['spec']['placement'])for m in c['modules']for r in m['action_clearance']]
        # Protect actual standing/interacting silhouettes too, as main does.
        v['presentation_keep_clear'] += [[n['center']['position'][0]-42,n['center']['position'][1]-65,84,90]for n in c['nodes'].values()]
        for leg in v['pilot_program']:
            if leg['kind']=='module':leg['entry']=dict(grounded=True,required_air_shots=1,maximum_shot_cooldown=0)
    return cases

def run(name,seed,mode='full',held=False,source=None):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_shape_run_exists')
    out.mkdir(parents=True);start=time.perf_counter();protocol=json.loads((HERE/'protocol.json').read_text());write(out/'protocol.json',dict(protocol,seed=seed,held=held,mode=mode))
    for p in HERE.glob('*'):
        if p.is_file():q=out/'design-source'/p.name;q.parent.mkdir(exist_ok=True);shutil.copy2(p,q)
    try:
        c=json.loads((Path(source)/'compiled.json').read_text())if source else build(out,seed)
        if c is None:write(out/'summary.json',dict(all_passed=False,status='search_unsatisfied'));return out
        if source:write(out/'compiled.json',c)
        cases=prepare_cases(c,mode)
        if held:
            rng=random.Random(str(protocol['holdout_input_seed'])+seed);extra=[]
            for case in cases[:3]:
                for i in range(protocol['holdout_trials_per_route']):
                    v=copy.deepcopy(case);v['id']+='-held-'+str(i);v['noise']=dict(seed=rng.randrange(2**30),timing_frames=1,aim_degrees=1)
                    for saw in v['saws']:saw['initial_phase']=rng.random()
                    for enemy in v['enemies']:enemy['initial_idle_cooldown']=.2+.4*rng.random()
                    v['holdout']=True;extra.append(v)
            cases+=extra
        write(out/'cases.json',dict(cases=cases));engine=ShapeEngine(out/'physics');rows=[]
        for case,r,ev in engine.run(cases,'shape-'+mode):
            row=dict(id=case['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),shots=r.get('shots'),failure=r.get('pilot',{}).get('failure'),extra=r.get('extra'),evidence=ev)
            rows.append(row);write(out/'rows.json',rows);f=row['failure']or{}
            print(json.dumps(dict(id=row['id'],ok=row['ok'],ticks=row['ticks'],shots=row['shots'],reason=row['reason'],leg=f.get('leg_id'),position=f.get('actual',{}).get('position')),ensure_ascii=False),flush=True)
        write(out/'summary.json',dict(all_passed=len(rows)==len(cases)and all(r['ok']for r in rows),rows=rows,held=held,wall_seconds=time.perf_counter()-start,human_fun='unreviewed',production_admitted=False))
    except Exception as error:
        import traceback
        write(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc()));raise
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--seed',required=True);p.add_argument('--mode',default='full',choices=['main','full','lower','reward']);p.add_argument('--held',action='store_true');p.add_argument('--source');a=p.parse_args();out=run(a.name,a.seed,a.mode,a.held,a.source);print(out)
    if not json.loads((out/'summary.json').read_text())['all_passed']:raise SystemExit(2)
