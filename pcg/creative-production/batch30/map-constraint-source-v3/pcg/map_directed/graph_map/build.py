"""Existing Director graph -> whole-library domains -> exact joint Block layout."""
import copy,json,shutil,time
from pathlib import Path
from .joint import expand,domains,fold
from ..content_domains.build import load
from ..block_grid.policy import review,demands
from ..shape_search.search import search
from .boundaries import bind as bind_boundaries
from ..direct_join.canonical import export_reload
from ..direct_join.assemble import assemble_modules
from ..direct_join.audit import audit
from ..director import REPO
from ..run import write
from pcg.prototype.plains.compound_terraces import compact_clearance
from pcg.prototype.workshop.production_loop import compile_request
from pcg.prototype.factory.core.quality import digest


def allocate_items(g):
    low=['damage_blue','health_blue','echo_magazine','damage_blue','health_blue'];index=high=0
    for a in g['reward_allocations']:
        if a['kind']=='major_item':
            if a.get('high_value'):
                a['item']='power_gold'if high==0 else'health_blue';high+=1
            else:a['item']=low[index%len(low)];index+=1
        elif a['kind']=='hidden_collectible':a['item']='efficient_grip'
        elif a['kind']=='currency':a['amount']=6
        elif a['kind']=='recovery':a['amount']=1
        a.update(value=None,value_status='UNCALIBRATED: real service, not a balanced economic value')


def finish(out,g,selected,policy):
    allocate_items(g);write(out/'exploration.json',g);write(out/'policy.json',policy);write(out/'challenge-specifications.json',demands(g,policy))
    bound=[];log=[]
    for m in selected:
        m=compile_request(dict(recipe='map-owned-supports/v1',module=m))['modules'][0];m['spec'].setdefault('design_contract',dict(input_node=m['id'],map_added_platforms=0,exact_ports=list(m['ports'])))
        m['spec']['node']=copy.deepcopy(next(n for n in g['nodes']if n['id']==m['id']))
        allocations=[a for a in g['reward_allocations']if a['node']==m['id']]
        response=compile_request(dict(recipe='map-budget-binding/v1',module=m,allocations=allocations));v=response['modules'][0]
        # Bounds are metadata, not a rectangular collider or frame.
        from ..block_grid.contracts import regions,raster,declare,validate
        from ..content_domains.reservation import connect
        rr=regions(v);x=min(r[0]for r in rr);y=min(r[1]for r in rr);right=max(r[0]+r[2]for r in rr);bottom=max(r[1]+r[3]for r in rr);v['spec']['space']['core_bounds']=[x,y,right-x,bottom-y]
        cells=set().union(*(raster(r)for r in rr));cells,added=connect(cells,v['ports']);v['adaptation']['budget_empty_reservations']=added;v=declare(v,cells)
        errors=validate(v)
        if errors:raise ValueError('budget_binding_invalid/'+m['id']+'/'+str(errors))
        bound.append(v);log.append(dict(node=m['id'],recipe='map-budget-binding/v1',status=response['status'],parent_version=m['content_version'],output_version=v['content_version'],allocations=allocations,whole_map_physics='PENDING'))
    write(out/'module-generation-log.json',log);write(out/'precanonical.json',dict(graph=g,modules=bound))
    bound=export_reload(bound,out/'module-library',producer='pcg/map_directed/graph_map/build.py')
    seams=[dict(id=e['id'],kind='side'if bound[0]['block_grid']else'side')for e in g['edges']]
    c=assemble_modules(g,bound,seams);c.update(shop={},unresolved_rewards=[],reward_flag_requirements={})
    for b in g['branches']:
        node=next(n for n in g['nodes']if n['id']==b['reward']);sites=[s['id']for s in c['case']['reward_sites']if s.get('allocation',{}).get('node')==b['reward']and s.get('reward_kind')=='major_item']
        for flag in node.get('opens',[]):c['reward_flag_requirements'][flag]=sites
    for gate in c['gate_specs']:gate.update(x=gate['bounds'][0],y=gate['bounds'][1],w=gate['bounds'][2],h=gate['bounds'][3])
    write(out/'map-recipe.json',dict(seed=g['seed'],exploration_sha256=digest(g),source_contract='Graph / Block / Module, exact placements and owned state boundaries',modules=[m['canonical_document']for m in bound],map_added_platforms=0,production_admitted=False));write(out/'assembly-audit.json',audit(c));write(out/'compiled.json',c);write(out/'input-binding.json',dict(exploration_sha256=digest(g),policy_sha256=digest(policy),whole_world_graph_sha256=c['source']['graph_sha256']))
    return c


def build(out,g,policy,sources,attempts=4,seconds=60,preselected=None):
    out=Path(out);out.mkdir(exist_ok=False,parents=True);started=time.perf_counter();write(out/'protocol.json',dict(sources=sources,attempts=attempts,seconds_per_attempt=seconds,original_graph_sha256=digest(g),map_added_platforms=0,scope='Joint local Macro search; no fixed regional skeleton or family whitelist',production_admitted=False))
    design=review(g,policy);write(out/'policy-review.json',design)
    if not design['ok']:raise ValueError('design_rejected/'+str(design['errors']))
    pool,qualification=load(sources);pool=[compact_clearance(m)for m in pool];write(out/'source-qualification.json',qualification)
    if preselected:
        # Explicit rigid-layout replay only; it never becomes a regional fallback.
        required={e['id']for e in g['edges']if(not e['bidirectional']or e.get('switch'))and not(g.get('condition_definitions',{}).get(e.get('switch'),{}).get('kind')=='knowledge'and e['bidirectional'])}
        present={q['edge_id']for m in preselected for q in m.get('boundary_gates',[])}
        if present and not required<=present:raise ValueError('partial_preselected_state_boundaries')
        if not present:
            preselected,log=bind_boundaries(g,preselected);write(out/'state-boundary-binding.json',log)
            if preselected is None:raise ValueError('preselected_layout_state_boundaries_unsatisfied')
        return finish(out,g,preselected,policy)
    history=[]
    for i in range(attempts):
        ex,mapping=expand(g,g['seed']+'/components-'+str(i));D,A=domains(ex,pool);write(out/('domain-counts-'+str(i)+'.json'),{k:len(v)for k,v in D.items()})
        accepted={};rejections=[]
        def complete(ms):
            try:folded=fold(g,mapping,ms)
            except ValueError as e:
                if len(rejections)<12:rejections.append(dict(stage='fold',reason=str(e)))
                return False
            gated,log=bind_boundaries(g,folded)
            if gated is None:
                if len(rejections)<12:rejections.append(dict(stage='state_boundary',attempts=log))
                return False
            accepted.update(modules=gated,boundaries=log);return True
        r=search(ex,D,g['seed']+'/space-'+str(i),budget=100000,require_blocks=True,allow_shared_air=True,ideal_scale_blocks=.4,forward_check=True,probe_budget=3500000,wall_budget_seconds=seconds,solution_check=complete)
        ms=r.pop('modules',[]);write(out/('search-'+str(i)+'.json'),r);write(out/('solution-rejections-'+str(i)+'.json'),rejections);history.append(dict(attempt=i,status=r['status']))
        if not ms:continue
        selected=accepted['modules'];write(out/'state-boundary-binding.json',accepted['boundaries'])
        write(out/'component-mapping.json',mapping);write(out/'expanded-modules.json',ms);write(out/'expanded-constraints.json',ex);write(out/'search-history.json',history)
        return finish(out,g,selected,policy)
    write(out/'search-history.json',history);write(out/'generator-feedback.json',dict(status='needs_design',reason='No qualified joint shape layout within budget',source_graph_sha256=digest(g),unresolved_nodes=[n['id']for n in g['nodes']],may_delete_required_edges=False,history=history))
    write(out/'summary.json',dict(status='spatial_unsatisfied',physics='NOT_RUN',seconds=time.perf_counter()-started,production_admitted=False));return None
