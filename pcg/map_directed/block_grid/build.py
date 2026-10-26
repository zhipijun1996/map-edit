"""Joint Block/shape search on preserved Exploration graphs and real Modules."""
import copy,gzip,hashlib,json
from pathlib import Path
from .contracts import validate
from ..director import REPO
from ..run import write
from ..catalog_feed.build import rename
from ..catalog_feed.adapt import apply_reward_request
from ..catalog_feed.reentrant_fixture import mirrored
from ..catalog_feed.design_review import reward_requests
from ..shape_search.search import search
from ..direct_join.canonical import export_reload
from ..direct_join.assemble import assemble_modules
from ..direct_join.audit import audit
from ..library import CandidateLibrary
from pcg.prototype.plains.block_modules import hub,cases_for
from pcg.prototype.factory.core.quality import digest

def traces(run):
    root=Path(run);frames=[];results={}
    for b in json.loads((root/'batches.json').read_text()):
        packed=root/b['gzip_path'];raw=gzip.decompress(packed.read_bytes())
        if hashlib.sha256(packed.read_bytes()).hexdigest()!=b['gzip_sha256']or hashlib.sha256(raw).hexdigest()!=b['raw_output_sha256']:raise ValueError('independent_trace_drift')
        for r in json.loads(raw)['results']:
            results[r['id']]=r
            if r['ok']:frames+=r['frames']
    return frames,results

def mirror_grid(module):
    detached=copy.deepcopy(module)
    for key in ['spawn','entry_port','exit_port','goal']:detached['case'][key]=detached['case'][key][:]
    m=mirrored(detached);width=int(m['spec']['space']['core_bounds'][2]/128)
    m['block_grid']['cells']=sorted([[width-1-x,y]for x,y in module['block_grid']['cells']])
    for p in m['ports'].values():
        p['grid']['cell'][0]=width-1-p['grid']['cell'][0];p['grid']['edge']={'W':'E','E':'W','N':'N','S':'S'}[p['grid']['edge']]
    m['block_grid']['port_bindings']=[dict(port_id=k,**p['grid'])for k,p in m['ports'].items()]
    m['case']['ports']=[dict(id=k,position=p['dock']['position'],normal=p['normal'],support_index=p['dock']['support_indices'][0])for k,p in m['ports'].items()]
    m['adaptation']['horizontal_mirror']='NEW variant; independent mirrored source and fresh assembled proof required'
    m['variant_id']+='/mirror';return m

def independent_hub(source):
    m=hub();root=Path(source)
    if cases_for(m)!=json.loads((root/'cases.json').read_text())['cases']:raise ValueError('block_hub_input_drift')
    if json.loads((root/'summary.json').read_text())['passed']!=13:raise ValueError('block_hub_directions_unverified')
    frames,_=traces(root)
    m['action_clearance']=[list(v)for v in dict.fromkeys((f['x']-12,f['y']-18,24,36)for f in frames[::2])]
    m['independent_evidence']=dict(run=str(root.relative_to(REPO)),scope='12 staging-to-staging directions and continuous tour; boundary crossings tested separately',general_admission=False)
    return m

def qualified_sources(source):
    from .catalog import case_for
    root=Path(source);modules=json.loads((root/'modules.json').read_text());rows=json.loads((root/'rows.json').read_text());good={r['id']for r in rows if r['ok']};_,result=traces(root/'physics');out=[]
    source_cases={c['id']:c for c in json.loads((root/'cases.json').read_text())['cases']}
    for m in modules:
        if m['variant_id']not in good:continue
        if case_for(m)!=source_cases[m['variant_id']]:raise ValueError('independent_module_input_binding_drift')
        frames=result[m['variant_id']]['frames'];m['action_clearance']=[list(v)for v in dict.fromkeys((f['x']-12,f['y']-18,24,36)for f in frames[::2])]
        errors=validate(m)
        if errors:raise ValueError('measured_module_space_invalid/'+m['variant_id']+':'+','.join(errors))
        m['source_shape_sha256']=digest(m['case']['platforms'])
        m['independent_evidence']=dict(run=str(root.relative_to(REPO)),case=m['variant_id'],scope='Exact adapted source direction; boundary and Map remain separately verified',general_admission=False)
        out.append(m)
    return out

def build(out,seed,graph_source,hub_source,source_probe):
    prior=json.loads((Path(graph_source)/'compiled.json').read_text());g=copy.deepcopy(prior['exploration_graph']);g['seed']=seed
    g['source']='Preserved PR #1 Exploration graph; fresh Block128 Module/shape assignment; old positions not consumed'
    g['block_size']=128;allocation=reward_requests(g)
    if not allocation['ok']:raise ValueError(allocation['errors'])
    h=independent_hub(hub_source);pool=qualified_sources(source_probe);domains={};requests=[]
    old={m['id']:m for m in prior['modules']}
    for n in g['nodes']:
        key=n['id'];es=[e for e in g['edges']if key in[e['from'],e['to']]]
        needed={e['id']:next(p for k,p in old[key]['ports'].items()if k==e['id'])['normal']for e in es}
        if key.startswith(('L','R')):templates=[h]
        else:
            row=int(key[1:-1]);family='timed-cache'if key.endswith('b')else'moving-ray-window'if row%2 else'thorn-slot'
            templates=[m for m in pool if m['selection_family']==family]
            want=needed[next(e['id']for e in es if e['to']==key)]
            templates=[m for m in templates if m['ports']['in']['normal']==want]
        request=dict(id='block-demand/'+key,roles=['junction']if key.startswith(('L','R'))else['traversal'],block_size=128,
            ports=[dict(edge=e,normal=v)for e,v in needed.items()],risk_reward=allocation['requests'][key],may_remove_edges=False)
        requests.append(request);values=[]
        for raw in templates:
            m=copy.deepcopy(raw);m['id']=key;m['spec'].update(id=request['id'],node_id=key,node=copy.deepcopy(n),design_contract=copy.deepcopy(request))
            mapping={}
            for eid,normal in needed.items():
                matches=[k for k,p in m['ports'].items()if p['normal']==normal]
                if len(matches)!=1:break
                mapping[matches[0]]=eid
            else:
                # Unconnected physical openings remain declared; no invented
                # missing ports and no silent erasure of the Module interface.
                mapping.update({k:'unused-'+k for k in m['ports']if k not in mapping})
                m=rename(apply_reward_request(m,allocation['requests'][key]),mapping)
                m['block_grid']['port_bindings']=[dict(port_id=k,**p['grid'])for k,p in m['ports'].items()]
                m['variant_id']=key+'/'+raw['variant_id'];values.append(m)
        domains[key]=values
    write(out/'challenge-specifications.json',requests);write(out/'catalog-domain-counts.json',{k:len(v)for k,v in domains.items()})
    result=search(g,domains,seed,budget=50000,require_blocks=True);ms=result.pop('modules',[]);write(out/'search.json',result)
    if not ms:
        write(out/'generator-feedback.json',dict(status='unsatisfied',empty_domains=[r for r in requests if not domains[r['id'].split('/')[-1]]],reason=result.get('reason',result['status']),maximum_local_revisions=2,may_delete_required_routes=False))
        return None
    # Existing quarantine library, exact hard demands only. A prior scoped Map
    # witness never exempts this new assembly from independent whole-map tests.
    library=CandidateLibrary();reuse=[]
    for i,m in enumerate(ms):
        hits=library.find_payload(m['spec'],isolated_experiment=True)
        matches=[v for v in hits if v['module']['case']==m['case'] and v['module']['ports']==m['ports'] and v['module'].get('block_grid')==m.get('block_grid')]
        if matches:
            ms[i]=matches[0]['module']
        reuse.append(dict(node=m['id'],exact_candidates=len(hits),reused=bool(matches),record=matches[0]['record']if matches else None,
            outcome='validated scoped payload reused; new Map verification mandatory'if matches else'independently verified Block Module adaptation selected; fresh Map verification mandatory'))
    write(out/'reuse-log.json',reuse)
    write(out/'precanonical.json',dict(graph=g,modules=ms));ms=export_reload(ms,out/'module-library',producer='pcg/map_directed/block_grid/build.py')
    seams=[dict(id=e['id'],kind=next(m for m in ms if m['id']==e['from'])['ports'][e['id']]['kind'])for e in g['edges']]
    c=assemble_modules(g,ms,seams);c.update(shop={},unresolved_rewards=[]);c['source']['graph_source']=g['source']
    write(out/'compiled.json',c);write(out/'assembly-audit.json',audit(c));write(out/'map-recipe.json',dict(seed=seed,modules=[m['canonical_document']for m in ms],hard_checks=c['hard_checks'],block_size=128))
    return c
