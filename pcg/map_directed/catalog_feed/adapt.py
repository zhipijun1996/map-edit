"""New versioned source-owned exterior cuts; never map-authored connection fill."""
import copy,gzip,json,math,functools
from pathlib import Path
from .catalog import load
from ..director import REPO
from pcg.prototype.factory.core.quality import digest

@functools.lru_cache(maxsize=1)
def samples():
    p=REPO/'pcg/results/catalog-feed-source-probe-v1';rows=json.loads((p/'rows.json').read_text());cache={};out={}
    for row in rows:
        if not row['ok']:continue
        e=row['evidence'];path=p/'physics'/e['output']
        if str(path)not in cache:cache[str(path)]=json.loads(gzip.decompress(path.read_bytes()))['results']
        out[(row['version'],row['id'])]=cache[str(path)][e['index']]['frames']
    extra=REPO/'pcg/results/catalog-feed-fork-depth-probe-v1'
    if(extra/'rows.json').exists():
        batches={}
        for row in json.loads((extra/'rows.json').read_text()):
            if not row['ok']:continue
            e=row['evidence'];path=extra/'physics'/e['output']
            if str(path)not in batches:batches[str(path)]=json.loads(gzip.decompress(path.read_bytes()))['results']
            out[(row['version'],row['id'])]=batches[str(path)][e['index']]['frames']
    return out

def target(c,point,label):
    x,y=point;indices=[i for i,r in enumerate(c['platforms'])if abs(r[1]-(y+18))<1.1 and r[0]<=x-11 and x+11<=r[0]+r[2]]
    if not indices:raise ValueError('no_full_body_ground_support/'+label)
    return dict(id=label,position=[x,y],region=[x-7,y-4,14,8],support_indices=indices,grounded=True,stable_ticks=6)

def leg(c,point,plan,label):return dict(kind='module',target=target(c,point,label),control_plan=copy.deepcopy(plan),budget_ticks=min(3600,c.get('max_frames',1600)+180))

def exterior(item,node,padding=0,fork=False):
    old=item['cases'][0];c=copy.deepcopy(old);version=item['record']['contentVersion'];fs=samples();allframes=[f for source in item['cases']for f in fs.get((version,source['id']),[])]
    if not allframes:raise ValueError('source_clean_witness_missing')
    c['source_case_binding']=dict(id=old['id'],module_sha256=old.get('module_sha256'),contentVersion=version)
    for k in ['factory_evidence','recorded_frames','validation_summary','module_sha256','factory_id']:c.pop(k,None)
    xmin=min(f['x']-12 for f in allframes);xmax=max(f['x']+12 for f in allframes);ymax=max(f['y']+18 for f in allframes)
    left=math.floor((xmin-24)/8)*8-padding;right=math.ceil((xmax+24)/8)*8+padding
    removed=[];rects=[];mapping={}
    for i,r in enumerate(c['platforms']):
        a,b=max(r[0],left),min(r[0]+r[2],right)
        if b-a<=0 or(r[1]>ymax+80 and r[2]>500):removed.append(dict(index=i,rect=r));continue
        mapping[i]=len(rects);rects.append([a,r[1],b-a,r[3]])
    c['platforms']=rects;c['one_way_platform_indices']=[mapping[i]for i in c.get('one_way_platform_indices',[])if i in mapping]
    for t in c.get('thorns',[]):
        if t['platform_index']not in mapping:raise ValueError('exterior_cut_would_remove_thorn_host')
        oldp=old['platforms'][t['platform_index']];t['platform_index']=mapping[t['platform_index']];newp=rects[t['platform_index']]
        if t['face']in ['top','bottom']:
            start=max(oldp[0]+t['start_offset'],newp[0]);end=min(oldp[0]+t['start_offset']+t['length'],newp[0]+newp[2]);t['start_offset']=start-newp[0];t['length']=end-start
            if t['length']<=0:raise ValueError('exterior_cut_would_remove_thorns')
    c.setdefault('shop_sites',[])
    for s in c['latches']:s.setdefault('prompt','')
    for s in c.get('reward_sites',[]):s['target']=target(c,s['position'],s['id']);s['amount']=s.get('amount',10)
    if not fork:
        exit_support=target(c,old['exit_port'],'exit')['support_indices'][0];r=c['platforms'][exit_support];bound=math.floor((r[0]+r[2])/8)*8
        if xmax>bound-12:raise ValueError('foldback_exit_requires_directional_macro_envelope')
        indexmap={};clipped=[]
        for i,r in enumerate(c['platforms']):
            if r[0]>=bound:removed.append(dict(index=i,rect=r));continue
            indexmap[i]=len(clipped);clipped.append([r[0],r[1],min(r[0]+r[2],bound)-r[0],r[3]])
        c['platforms']=clipped;c['one_way_platform_indices']=[indexmap[i]for i in c['one_way_platform_indices']if i in indexmap]
        for t in c.get('thorns',[]):
            if t['platform_index']not in indexmap:raise ValueError('exterior_would_remove_active_thorns')
            t['platform_index']=indexmap[t['platform_index']]
        for s in c.get('reward_sites',[]):s['target']=target(c,s['position'],s['id'])
    ports={};out={};inside={}
    def port(e,pt,normal):
        dock=[pt[0]-normal[0]*24,pt[1]];t=target(c,dock,node+'/'+e)
        ports[e]=dict(id=e,position=pt,normal=normal,kind='side',aperture=[pt[0]-48,pt[1]-64,96,128],connection_mode='continuous_terrain',dock=t)
        return t
    entry=old['entry_port'];entry_support=target(c,entry,'entry')['support_indices'][0];L=c['platforms'][entry_support][0]
    for i,r in enumerate(c['platforms']):
        if i in c['one_way_platform_indices']:continue
        if r[0]<entry[0]+12 and r[0]+r[2]>L and r[1]<entry[1]+17 and r[1]+r[3]>entry[1]-17:
            raise ValueError('source_entry_rear_wall_requires_different_ingress')
    port('in',[L,entry[1]],[-1,0]);inside['in']=[dict(kind='walk',target=target(c,entry,node+'/source-entry'))]
    center=target(c,entry,node+'/center')
    routes=item['cases']if fork else[old]
    for source in routes:
        pt=source['exit_port'];t=target(c,pt,'exit');r=c['platforms'][t['support_indices'][0]];R=math.floor((r[0]+r[2])/8)*8
        # The collider face itself, not only its marker, must be flush.
        r[2]=R-r[0]
        eid=source.get('route_spec',{}).get('to_port','out')if fork else'out';dock=port(eid,[R,pt[1]],[1,0])
        blockers=[e for e in c.get('enemies',[])if pt[0]-24<=e['position'][0]<=dock['position'][0]+24 and abs(e['position'][1]-pt[1])<60]
        if any(abs(e['position'][0]-pt[0])<48 for e in blockers):raise ValueError('source_goal_inside_live_enemy_exit_contact_requires_new_recipe')
        out[eid]=[leg(c,pt,source['control_plan'],node+'/'+eid+'/core'),dict(kind='jump'if blockers else'walk',target=dock)]
    m=dict(id=node,case=c,ports=ports,center=center,core=None,center_to_port=out,port_to_center=inside,core_visit_program=[],boundary_gates=[],
        spec=dict(id='catalog-feed/'+node,node_id=node,node=dict(id=node,role='junction'if fork else'challenge',label=item['title']),placement=[0,0],boundary_policy='open',space=dict(core_bounds=[0,0,max(r[0]+r[2]for r in rects),max(r[1]+r[3]for r in rects)]),ports=list(ports.values())),
        source_version=version,source_title=item['title'],variant_id=node+'/'+version[7:15]+'/'+str(padding),source_shape_sha256=digest(rects),
        action_clearance=[list(r)for r in dict.fromkeys((f['x']-12,f['y']-18,24,36)for f in allframes[::2])],motion_contract=dict(mode='grounded_dock',capabilities=['move','jump','shot_recoil'],entry_grounded=True,required_air_shots=1,maximum_entry_speed=1),
        adaptation=dict(source=version,exterior_x=[left,right],removed_nonserving_catch_banks=removed,added_geometry=0,status='NEW geometry and ports; source proof not inherited'))
    b=m['spec']['space']['core_bounds']
    for saw in c['saws']:
        b[2]=max(b[2],saw['origin'][0]+abs(saw['travel'][0])+saw['radius']);b[3]=max(b[3],saw['origin'][1]+abs(saw['travel'][1])+saw['radius'])
    m['content_version']='sha256:'+digest(dict(case=c,ports=ports));return m
