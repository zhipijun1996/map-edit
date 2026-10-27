"""Reuse source content, adapt bounded bank cuts, and demand fresh verification."""
import copy,json,math
from pathlib import Path
from .contracts import declare,raster,regions,validate
from ..catalog_feed.catalog import load
from ..catalog_feed.adapt import exterior,target
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.plains.block_modules import port

def shift(m,dx,dy):
    m=copy.deepcopy(m);c=m['case']
    def rect(r):return [r[0]+dx,r[1]+dy,*r[2:]]
    c['platforms']=[rect(r)for r in c['platforms']];c['hazards']=[rect(r)for r in c.get('hazards',[])]
    for name in ['spawn','entry_port','exit_port']:c[name]=[c[name][0]+dx,c[name][1]+dy]
    c['goal']=rect(c['goal'])
    for l in c['latches']:
        l['bell']=[l['bell'][0]+dx,l['bell'][1]+dy];l['gate']=rect(l['gate'])
        if l.get('return_access'):l['return_access']=[l['return_access'][0]+dx,l['return_access'][1]+dy]
    for s in c['saws']:s['origin']=[s['origin'][0]+dx,s['origin'][1]+dy]
    for p in c['moving_platforms']:
        for k in ['start','finish']:p[k]=[p[k][0]+dx,p[k][1]+dy]
    for s in c.get('reward_sites',[]):
        if s.get('position'):s['position']=[s['position'][0]+dx,s['position'][1]+dy]
        if s.get('region'):s['region']=rect(s['region'])
    seen=set()
    def patch(v):
        if isinstance(v,dict):
            if id(v)in seen:return
            seen.add(id(v))
            if 'support_indices'in v:v['position']=[v['position'][0]+dx,v['position'][1]+dy];v['region']=rect(v['region'])
            if 'target_x'in v:v['target_x']+=dx
            if v.get('trigger',{}).get('dynamic',{}).get('kind')=='actor_x':v['trigger']['dynamic']['value']+=dx
            for x in v.values():patch(x)
        elif isinstance(v,list):
            for x in v:patch(x)
    for k in ['center','core','center_to_port','port_to_center','core_visit_program']:patch(m.get(k))
    patch(c.get('reward_sites',[]));patch(c['control_plan'])
    m['action_clearance']=[rect(r)for r in m['action_clearance']]
    return m

def snap_candidate(item,size=128):
    if size!=128:raise ValueError('needs_design/source_adapter_only_calibrated_at_128')
    m=exterior(item,'block-action',48);c=m['case']
    if c['entry_port'][1]!=c['exit_port'][1]:raise ValueError('requires_offset_port_recipe')
    if c.get('enemies'):raise ValueError('enemy_envelope_not_certified')
    L=m['ports']['in']['position'][0];R=m['ports']['out']['position'][0]
    xmin=min(r[0]for r in m['action_clearance']);xmax=max(r[0]+r[2]for r in m['action_clearance'])
    left_room=max(0,min(64,xmin-L-12,c['entry_port'][0]-L-36));right_room=max(0,min(64,R-xmax-12,R-c['exit_port'][0]-36))
    options=[]
    for width in sorted({math.floor((R-L)/size)*size,math.ceil((R-L)/size)*size},key=lambda w:abs(w-(R-L))):
        cut=R-L-width
        if width<256:continue
        if 0<=cut<=left_room+right_room:
            left_cut=max(0,cut-right_room);options.append((width,left_cut,cut-left_cut))
        elif -64<=cut<0:
            # Registered Module recipe adaptation, at most one 32px tile per
            # terminal bank. Never a Map connector or an extended action core.
            options.append((width,cut/2,cut/2))
    if not options:raise ValueError('no_grid_span_within_bounded_terminal_bank_recipe')
    width,left_cut,right_cut=options[0];lo=L+left_cut;hi=R-right_cut
    if left_cut<0:
        p=c['platforms'][m['center']['support_indices'][0]];end=p[0]+p[2];p[0]=lo;p[2]=end-lo
    if right_cut<0:
        p=c['platforms'][m['ports']['out']['dock']['support_indices'][0]];p[2]=hi-p[0]
    for i,p in enumerate(c['platforms']):
        a=max(lo,p[0]);b=min(hi,p[0]+p[2])
        if b<=a:raise ValueError('grid_cut_would_delete_physical_cell')
        if a!=p[0]or b!=p[0]+p[2]:
            if any(t['platform_index']==i for t in c['thorns']):raise ValueError('grid_cut_would_alter_required_hazard')
            p[0]=a;p[2]=b-a
    # Only trim/translate banks. Challenge geometry, timing and motion retain
    # their actual source values; all edited variants are new content versions.
    entry_y=c['entry_port'][1];m=shift(m,-lo,334-entry_y);c=m['case'];mechanism_edits=[]
    for latch in c['latches']:
        if latch['bell'][0]<14 or latch['bell'][0]>width-14:
            old=latch['bell'][:];latch['bell'][0]=48 if old[0]<14 else width-48
            mechanism_edits.append(dict(cell=latch['id'],before=old,after=latch['bell'][:],reason='Demand requires all bell entities inside the port boundary; new aim and physics proof mandatory'))
    c.setdefault('shop_sites',[])
    for i in set(m['center']['support_indices'])|set(m['ports']['out']['dock']['support_indices']):c['platforms'][i][3]=min(c['platforms'][i][3],64)
    ingress=[24,334]
    for mover in c['moving_platforms']:
        a,b=mover['start'],mover['finish'];w,h=mover['size'];envelope=[min(a[0],b[0])-w/2,min(a[1],b[1])-h/2,abs(a[0]-b[0])+w,abs(a[1]-b[1])+h]
        from ..shape_search.search import intersects
        if intersects([4,308,40,52],envelope):ingress=m['center']['position'][:]
    ports={'in':port(c,'in',[0,2],'W',ingress),'out':port(c,'out',[int(width/size)-1,2],'E',[width-24,334])}
    if ingress!=[24,334]:ports['in']['grid']['ingress_condition']='original ray-shutter phase window before boundary crossing'
    m['ports']=ports;m['port_to_center']['in']=[dict(kind='walk',target=copy.deepcopy(m['center']))]
    m['center_to_port']['out'][-1]['target']=copy.deepcopy(ports['out']['dock'])
    c['spawn']=ports['in']['dock']['position'][:];c['entry_port']=c['spawn'][:];c['exit_port']=ports['out']['dock']['position'][:];c['goal']=ports['out']['dock']['region'][:]
    c['ports']=[dict(id=k,position=p['dock']['position'],normal=p['normal'],support_index=p['dock']['support_indices'][0])for k,p in ports.items()]
    for a,b in [(ports['in']['dock']['position'],m['center']['position']),(c['exit_port'],m['center_to_port']['out'][0]['target']['position'])]:
        m['action_clearance'].append([min(a[0],b[0])-12,a[1]-18,abs(a[0]-b[0])+24,36])
    m['spec']['space']['core_bounds']=[0,0,width,640];m['spec']['ports']=list(ports.values())
    m['adaptation'].update(grid_bank_cut=[left_cut,right_cut],bank_extension=[max(0,-left_cut),max(0,-right_cut)],maximum_bank_extension_per_side=32,mechanism_edits=mechanism_edits,original_source=item['record']['contentVersion'],fresh_physics_required=True)
    m['functional_roles']=['traversal'];m['selection_family']=item['row']['family'];m['variant_id']='block-source/'+m['source_version'][7:19]+'/'+str(width)
    cells=set().union(*(raster(r,size)for r in regions(m)))
    # Reserve the internal air corridor; no physical terrain is added here.
    ys=[y for _,y in cells];cells|={(x,y)for x in range(int(width/size))for y in range(min(ys),max(ys)+1)}
    m=declare(m,cells,size);errors=validate(m)
    if errors:raise ValueError(','.join(errors))
    c=m['case'];c['world_bounds']=[-128,min(ys)*128-128,width+256,(max(ys)-min(ys)+3)*128]
    m['content_version']='sha256:'+digest(dict(case=c,ports=ports,block_grid=m['block_grid']));return m

def candidates(size=128):
    modules=[];rejected=[];families={}
    for item in load():
        if not item['row']['selected_for_plains_candidates']or len(item['cases'])!=1:continue
        if item['row']['family']not in ['thorn-slot','timed-cache','moving-ray-window','landing-reload-relay']:continue
        try:m=snap_candidate(item,size)
        except ValueError as error:rejected.append(dict(version=item['record']['contentVersion'],reason=str(error)));continue
        family=m['selection_family']
        if families.get(family,0)>=2:continue
        families[family]=families.get(family,0)+1;modules.append(m)
    return modules,rejected

def case_for(m):
    c=copy.deepcopy(m['case']);program=copy.deepcopy(m['port_to_center']['in']+m['center_to_port']['out'])
    for i,p in enumerate(program):p.update(id=f'{i:03d}-'+p['target']['id'],edge_id='independent-source')
    c.update(id=m['variant_id'],pilot_program=program,map_budget_ticks=5400,noise={},extra_required=False)
    return c

def probe(name):
    from ..director import REPO
    from ..run import write
    from .engine import BlockEngine
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_grid_catalog_probe_exists')
    from .build import mirror_grid
    out.mkdir();modules,rejected=candidates();modules=modules+[mirror_grid(m)for m in modules]
    write(out/'modules.json',modules);write(out/'rejected.json',rejected);cs=[case_for(m)for m in modules];write(out/'cases.json',dict(cases=cs))
    engine=BlockEngine(out/'physics');rows=[]
    for c,r,e in engine.run(cs,'block-source'):
        rows.append(dict(id=c['id'],ok=r['ok'],reason=r['reason'],failure=r.get('pilot',{}).get('failure'),evidence=e));write(out/'rows.json',rows);print(json.dumps(rows[-1]),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(rows),production_admitted=False));return out

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();print(probe(a.name))
