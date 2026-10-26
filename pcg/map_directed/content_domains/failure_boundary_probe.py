"""Map-context variants remove only deep, unvisited, non-serving failure floors."""
import argparse,copy,json
from .build import load
from .probe import cases
from .engine import ContentEngine
from .reservation import connect
from ..director import REPO
from ..run import write
from ..block_grid.contracts import declare,regions,raster,validate,connected
from pcg.prototype.factory.core.quality import digest


def prune(module):
    m=copy.deepcopy(module);c=m['case'];protected=set()
    def protect(t):protected.update(t.get('support_indices',[]));protected.update(t.get('allowed_transit_support_indices',[]))
    protect(m['center'])
    for p in m['ports'].values():protect(p['dock'])
    for program in m.get('port_transitions',{}).values():
        for leg in program:protect(leg['target'])
    for site in c.get('reward_sites',[]):protect(site.get('target',{}))
    bottom=max(y+h for x,y,w,h in m['action_clearance']);removed={i for i,r in enumerate(c['platforms'])if r[2]>=600 and r[1]>bottom+80 and i not in protected}
    if not removed:return None
    mapping={i:j for j,i in enumerate(i for i in range(len(c['platforms']))if i not in removed)}
    old=[dict(index=i,rect=c['platforms'][i])for i in sorted(removed)];thorns=[t for t in c.get('thorns',[])if t['platform_index']in removed]
    c['platforms']=[r for i,r in enumerate(c['platforms'])if i not in removed]
    c['one_way_platform_indices']=[mapping[i]for i in c.get('one_way_platform_indices',[])if i in mapping];c['wall_platform_indices']=[mapping[i]for i in c.get('wall_platform_indices',[])if i in mapping]
    c['thorns']=[dict(t,platform_index=mapping[t['platform_index']])for t in c.get('thorns',[])if t['platform_index']not in removed]
    visited_targets=set()
    def target(t):
        # Targets can be shared by a Port and several ordered programs.
        # deepcopy preserves those aliases; platform indices must change once.
        if id(t) in visited_targets:return
        visited_targets.add(id(t))
        for key in ['support_indices','allowed_transit_support_indices']:
            if key in t:t[key]=[mapping[i]for i in t[key]]
    target(m['center'])
    for p in m['ports'].values():target(p['dock'])
    for mapping2 in [m.get('port_transitions',{}),m.get('center_to_port',{}),m.get('port_to_center',{})]:
        for program in mapping2.values():
            for leg in program:target(leg['target'])
    for options in m.get('transition_options',{}).values():
        for option in options:
            for leg in option['program']:target(leg['target'])
    for site in c.get('reward_sites',[]):
        if 'target'in site:target(site['target'])
    for p in c.get('ports',[]):p['support_index']=mapping[p['support_index']]
    m['adaptation']['map_failure_boundary']=dict(removed_floors=old,removed_floor_hazards=thorns,measured_body_bottom=bottom,minimum_separation=80,failure_behavior_changed=True,source_physics_inherited=False,
          scope='New Map-context variant; original death/recovery boundary is not preserved, essential route hazards stay intact')
    m['variant_id']+='/map-failure-boundary';m.pop('independent_evidence',None)
    cells=set().union(*(raster(r)for r in regions(m)))
    if not connected(cells):cells,added=connect(cells,m['ports']);m['adaptation']['empty_reserved_blocks_added']=added
    m=declare(m,cells);errors=validate(m)
    if errors:raise ValueError(','.join(errors))
    m['source_shape_sha256']=digest(c['platforms']);m['content_version']='sha256:'+digest(dict(case=c,ports=m['ports'],matrix=m['port_transitions']));return m


def run(name,sources):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_failure_boundary_probe')
    out.mkdir();pool,audit=load(sources);ms=[];gaps=[]
    for m in pool:
        if not m.get('transition_options'):continue
        try:v=prune(m)
        except ValueError as e:gaps.append(dict(version=m['source_version'],variant=m['variant_id'],reason=str(e)));continue
        if v:ms.append(v)
    cs=[c for m in ms for c in cases(m)]
    for m in ms:
        if not m['adaptation'].get('return_proposal'):continue
        a,b=next(iter(m['port_transitions'])).split('>');pr=copy.deepcopy(m['port_transitions'][a+'>'+b]+m['port_transitions'][b+'>'+a]);c=copy.deepcopy(m['case'])
        for i,p in enumerate(pr):p.update(id=str(i)+'-'+p['target']['id'],edge_id='continuous-return')
        start=m['ports'][a]['dock'];end=m['ports'][b]['dock'];c.update(id=m['variant_id']+'/continuous-roundtrip',spawn=start['position'][:],entry_port=start['position'][:],exit_port=end['position'][:],goal=start['region'][:],pilot_program=pr,map_budget_ticks=12000,noise={},extra_required=True,extra_script=str(REPO/'pcg/map_directed/catalog_feed/extra.gd'));cs.append(c)
    write(out/'modules.json',ms);write(out/'cases.json',dict(cases=cs));write(out/'gaps.json',gaps);rows=[];engine=ContentEngine(out/'physics');engine.batch_size=8
    for c,r,e in engine.run(cs,'map-context-failure-boundary'):
        row=dict(id=c['id'],ok=r['ok'],reason=r['reason'],failure=r.get('pilot',{}).get('failure'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps(row),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(cs),variants=len(ms),production_admitted=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--sources',nargs='+',required=True);a=p.parse_args();run(a.name,a.sources)
