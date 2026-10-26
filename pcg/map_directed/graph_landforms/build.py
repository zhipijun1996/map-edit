"""The SAME graph drives candidate matching, joint Block CSP, export and world."""
import copy,json,gzip,hashlib
from pathlib import Path
from .graph import create
from .quality import screen
from .probe import cases as independent_cases
from ..director import REPO,regional
from ..run import write
from ..block_grid.contracts import declare,raster,regions,validate
from ..block_grid.build import traces
from ..catalog_feed.build import rename
from ..shape_search.search import search
from ..direct_join.canonical import export_reload
from ..direct_join.assemble import assemble_modules
from ..direct_join.audit import audit
from pcg.prototype.factory.core.quality import digest

def load(source):
    root=Path(source);modules=json.loads((root/'modules.json').read_text());cs={c['id']:c for c in json.loads((root/'cases.json').read_text())['cases']};_,results=traces(root/'physics');out=[]
    for m in modules:
        required=independent_cases(m)
        if any(c!=cs[c['id']]for c in required):raise ValueError('source_input_drift/'+m['variant_id'])
        proofs=[results[c['id']]for c in required]
        if not all(r['ok']for r in proofs):continue
        frames=[f for r in proofs for f in r['frames']]
        m['action_clearance']=[list(v)for v in dict.fromkeys((f['x']-12,f['y']-18,24,36)for f in frames[::2])]
        cells=set().union(*(raster(r)for r in regions(m)));m=declare(m,cells)
        if validate(m):raise ValueError((m['variant_id'],validate(m)))
        m['source_shape_sha256']=digest(m['case']['platforms']);m['independent_evidence']=dict(run=str(root.relative_to(REPO)),source_binding_sha256=digest(json.loads((root/'physics/source_binding.json').read_text())),scope='Finite independent directional policies, no generic admission',general_admission=False)
        out.append(m)
    return out

def build(out,seed,source):
    g=create(seed);errors,logical=regional.base.validate_graph(g)
    if errors:raise ValueError(errors)
    write(out/'exploration.json',g);write(out/'mission.json',g['mission_policy']);write(out/'logic-validation.json',logical)
    pool=load(source);domains={};demands=[]
    for node in g['nodes']:
        key=node['id'];es=[e for e in g['edges']if key in[e['from'],e['to']]]
        request=dict(id='same-graph-demand/'+key,node_id=key,node=copy.deepcopy(node),objective=node['intent'],block_size=128,required_ports={e['id']:e['port_roles'][key]for e in es},ports_and_heights='candidate variables; no old physical layout',preserve_edges=[e['id']for e in es],map_added_terrain=0)
        values=[]
        for raw in pool:
            if not raw['variant_id'].startswith(node['macro_family']):continue
            if set(request['required_ports'].values())!=set(raw['ports']):continue
            m=copy.deepcopy(raw);m['id']=key;m['spec'].update(id=request['id'],node_id=key,node=copy.deepcopy(node),design_contract=copy.deepcopy(request));mapping={v:k for k,v in request['required_ports'].items()}
            m=rename(m,mapping);m['block_grid']['port_bindings']=[dict(port_id=k,**p['grid'])for k,p in m['ports'].items()];m['variant_id']=key+'/'+raw['variant_id'];values.append(m)
        domains[key]=values;demands.append(request)
    write(out/'challenge-specifications.json',demands);write(out/'catalog-domain-counts.json',{k:len(v)for k,v in domains.items()})
    attempts=[];accepted=[]
    if all(domains.values()):
        for i in range(12):
            r=search(g,domains,seed+'/joint-'+str(i),budget=12000,require_blocks=True);ms=r.pop('modules',[]);q=screen(g,ms)if ms else dict(ok=False,errors=[r['status']]);attempts.append(dict(search=r,design=q))
            if q['ok']:accepted.append((q['score'],i,ms,q))
    write(out/'search-attempts.json',attempts)
    if not accepted:
        write(out/'generator-feedback.json',dict(status='needs_design',empty_domains=[k for k,v in domains.items()if not v],required_edges=[e['id']for e in g['edges']],may_remove_edges=False,reason='No complete physically sourced layout passed joint geometry and design screens within12 attempts'));return None
    _,attempt,ms,q=min(accepted,key=lambda v:(v[0],v[1]));write(out/'selected-design.json',dict(attempt=attempt,**q));write(out/'precanonical.json',dict(graph=g,modules=ms))
    ms=export_reload(ms,out/'module-library',producer='pcg/map_directed/graph_landforms/build.py')
    c=assemble_modules(g,ms,[dict(id=e['id'],kind='side')for e in g['edges']]);c.update(shop={},unresolved_rewards=[])
    if c['exploration_graph']!=g or set(c['nodes'])!={n['id']for n in g['nodes']}or set(c['edges'])!={e['id']for e in g['edges']}:raise ValueError('blueprint_world_graph_mismatch')
    write(out/'compiled.json',c);write(out/'assembly-audit.json',audit(c));write(out/'map-recipe.json',dict(seed=seed,blueprint_sha256=digest(g),source=str(source),modules=[m['canonical_document']for m in ms],map_added_terrain=0))
    write(out/'blueprint-world-correspondence.json',dict(ok=True,blueprint_sha256=digest(g),nodes=[dict(node=m['id'],version=m['content_version'],placement=m['spec']['placement'],family=m['selection_family'])for m in ms],edges=c['seams'],substituted_nodes=0,deleted_edges=0))
    return c
