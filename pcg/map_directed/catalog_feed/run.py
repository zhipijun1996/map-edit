import argparse,copy,json,shutil,time,traceback,random
from pathlib import Path
from ..director import REPO
from ..run import write
from ..shape_search.run import ShapeEngine
from .catalog import load
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest

HERE=Path(__file__).parent
class FeedEngine(ShapeEngine):
    def __init__(self,out,source=False):
        super().__init__(out);self.batch_size=8 if source else 1
        files=list(HERE.glob('*'))
        for folder in ['prototype/workshop','prototype/creative_batches']:
            files+=list((REPO/'pcg'/folder).rglob('*'))
        for p in files:
            if not p.is_file()or p.suffix not in ['.gd','.py','.json','.tres','.tscn','.mjs']:continue
            rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p);q=self.out/'source_snapshot'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
        self.sim.runner_script=str(HERE/('source_runner.gd'if source else'runner.gd'))
        self.binding.update(runner=self.sim.runner_script,source_files=self.hashes,source_manifest_sha256=digest(self.hashes));write(self.out/'source_binding.json',self.binding)

def probe(name):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_run_exists')
    out.mkdir();items=load();write(out/'inventory.json',[dict(version=x['record']['contentVersion'],title=x['title'],family=x['row']['family'],selected=x['row']['selected_for_plains_candidates'],reason=x['row']['selection_reason'],withdrawn=x['withdrawn'],routes=len(x['cases']),original_evidence_missing=x['original_evidence_missing'])for x in items])
    refs=[(x,c)for x in items if not x['withdrawn']for c in x['cases']];cases=[copy.deepcopy(c)for _,c in refs];write(out/'cases.json',dict(cases=cases));engine=FeedEngine(out/'physics',True);rows=[]
    for i,(c,r,e)in enumerate(engine.run(cases,'source-library-clean')):
        x=refs[i][0];row=dict(version=x['record']['contentVersion'],title=x['title'],id=c['id'],family=c['family'],ok=r.get('ok',False),reason=r['reason'],ticks=r.get('ticks'),shots=r.get('shots'),capabilities=c['capabilities'],evidence=e)
        rows.append(row);write(out/'rows.json',rows);print(json.dumps(row,ensure_ascii=False),flush=True)
    write(out/'summary.json',dict(rows=rows,passed=sum(r['ok']for r in rows),total=len(rows),versions=len(items),scope='Fresh clean finite source-route checks under current formal avatar; not independent quality admission or whole-map proof',production_admitted=False));return out

def map_run(name,seed,source=None,held=False):
    from .build import generate,cases_for
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_run_exists')
    out.mkdir();protocol=json.loads((HERE/'protocol.json').read_text());write(out/'protocol.json',dict(protocol,seed=seed,held=held,source=source));start=time.perf_counter()
    for p in list(HERE.glob('*'))+list((HERE.parent/'shape_search').glob('*.py'))+list((HERE.parent/'direct_join').glob('*.py'))+list((HERE.parent/'direct_join').glob('*.mjs')):
        if p.is_file():q=out/'design-source'/p.relative_to(HERE.parent);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    try:
        if source:
            src=REPO/source
            if (src/'compiled.json').exists():
                c=json.loads((src/'compiled.json').read_text());selection=json.loads((src/'selection.json').read_text());branches=selection['branches']
            else:
                from ..direct_join.canonical import export_reload
                from ..direct_join.assemble import assemble_modules
                from ..direct_join.audit import audit
                saved=json.loads((src/'precanonical.json').read_text());g=saved['graph']
                for m in saved['modules']:
                    b=m['spec']['space']['core_bounds']
                    for saw in m['case']['saws']:
                        b[2]=max(b[2],saw['origin'][0]+abs(saw['travel'][0])+saw['radius']);b[3]=max(b[3],saw['origin'][1]+abs(saw['travel'][1])+saw['radius'])
                ms=export_reload(saved['modules'],out/'module-library',producer='pcg/map_directed/catalog_feed/adapt.py')
                c=assemble_modules(g,ms,[dict(id=e['id'],kind=next(m for m in ms if m['id']==e['from'])['ports'][e['id']]['kind'])for e in g['edges']]);write(out/'assembly-audit.json',audit(c))
                branches={f'{s}/{side}':[f'F{s}']+[f'{side}{s}-{i}'for i in range(3)]+[f'J{s}']for s in range(2)for side in ['hi','lo']}
                selection=dict(branches=branches,source_library_versions=44,plains_selected=32,latest_selected_versions=sorted({m['source_version']for m in ms}),assignments={m['id']:m['source_version']for m in ms},legacy_structural_junctions=0,added_map_geometry=0,resumed_geometry=str(src.relative_to(REPO)))
            for n in c['exploration_graph']['nodes']:
                n.setdefault('grants',[]);n.setdefault('opens',[]);n.setdefault('reward',0)
            c.setdefault('shop',{});c.setdefault('unresolved_rewards',[])
            write(out/'compiled.json',c);write(out/'selection.json',selection)
        else:c,branches=generate(out,seed)
        cs=cases_for(c,branches)
        if held:
            rng=random.Random(str(protocol['holdout_seed'])+seed)
            for original in cs[:]:
                for i in range(protocol['holdout_per_route']):
                    v=copy.deepcopy(original);v['id']+='-held-'+str(i);v['noise']=dict(seed=rng.randrange(2**30),timing_frames=1,aim_degrees=1);cs.append(v)
        write(out/'cases.json',dict(cases=cs));engine=FeedEngine(out/'physics');rows=[]
        for case,r,ev in engine.run(cs,'catalog-map'):
            row=dict(id=case['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),shots=r.get('shots'),pilot=r.get('pilot'),extra=r.get('extra'),evidence=ev);rows.append(row);write(out/'rows.json',rows)
            print(json.dumps(dict(id=row['id'],ok=row['ok'],reason=row['reason'],ticks=row['ticks'],leg=(r.get('pilot',{}).get('failure')or{}).get('leg_id')),ensure_ascii=False),flush=True)
        write(out/'summary.json',dict(all_passed=all(r['ok']for r in rows),passed=sum(r['ok']for r in rows),total=len(rows),rows=rows,seconds=time.perf_counter()-start,human_fun='unreviewed',production_admitted=False))
    except Exception as error:write(out/'failure.json',dict(error=str(error),traceback=traceback.format_exc()));raise
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--map',action='store_true');p.add_argument('--seed',default='catalog-cal-0');p.add_argument('--source');p.add_argument('--held',action='store_true');a=p.parse_args();print(map_run(a.name,a.seed,a.source,a.held)if a.map else probe(a.name))
