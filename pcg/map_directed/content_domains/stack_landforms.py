"""Folding-region interfaces: a cliff fork and an open merge with a lower exit."""
from pcg.prototype.plains.graph_landforms import make,walk,jump
from .junctions import shelf_rise,merge
from pcg.map_directed.block_grid.contracts import declare,validate
from pcg.prototype.plains.block_modules import port
from pcg.prototype.factory.core.quality import digest


def cliff_fork(reward=False):
    p=[[0,352,384,96],[0,448,128,128],[256,224,128,64],[128,96,128,32],
       [256,-32,128,32],[384,-160,256,32],[384,480,256,128],[256,-288,128,32],[384,-416,128,32]]
    center=[128,334]
    def routes(c,k,inside):
        if k=='upper':return []if inside else[jump(c,[320,206],'first-rock',1),jump(c,[192,78],'second-rock',-1),jump(c,[320,-50],'upper-rise',1),jump(c,[576,-178],'upper-overlook',1),walk(c,[616,-178],'upper-port')]
        if k=='lower':return [walk(c,[408,462],'under-rim-launch'),jump(c,[320,334],'base-return',-1),walk(c,center,'choice')]if inside else[walk(c,[320,334],'lower-rim'),walk(c,[448,462],'lower-choice'),walk(c,[616,462],'lower-port')]
        if k=='reward':return [walk(c,center,'choice')]if inside else[walk(c,[24,334],'cache-mouth')]
        if inside:return [walk(c,[320,-306],'cliff-upper-ledge'),walk(c,[576,-178],'cliff-overlook'),walk(c,[320,-50],'third-rock'),walk(c,[192,78],'second-rock'),walk(c,[320,206],'first-rock'),walk(c,center,'shared-choice')]
        return [jump(c,[320,206],'first-rock',1),jump(c,[192,78],'second-rock',-1),jump(c,[320,-50],'third-rock',1),jump(c,[576,-178],'overlook',1),walk(c,[528,-178],'cliff-rise-launch'),shelf_rise(c,[320,-306],'cliff-upper-ledge',-1),shelf_rise(c,[480,-434],'high-entrance',1)]
    # The boundary cell includes air used by the seam. It is deliberately
    # separate from the grounded staging ledge, not a connector platform.
    ports=[('ingress',[4,-4],'N',[480,-434]),('upper',[4,-2],'E',[616,-178]),('lower',[4,3],'E',[616,462])]
    if reward:ports.append(('reward',[0,2],'W',[24,334]))
    m=make('folding-cliff-fork'+('-cache'if reward else''),p,[],center,ports,routes,reserved_cells=[(4,-4),(1,1),(2,0),(2,-2),(3,-3)],estimate_clearance=False)
    m['ports']['ingress']['grid']['profile']='vertical-recoil-128/v2'
    m['block_grid']['port_bindings']=[dict(port_id=k,**p['grid'])for k,p in m['ports'].items()]
    m['functional_roles']=['junction','fork','vertical_traversal'];return m


def lower_merge(third=False):
    m=merge(256);c=m['case'];c['platforms'][2]=[448,224,96,32];c['platforms'][3]=[544,320,1,1]
    # Remove the non-serving decorative column rather than hide a collision.
    c['platforms'].pop(3)
    # Target support indices after removal must be rebuilt from the real rocks.
    from pcg.map_directed.catalog_feed.adapt import target
    for mapping in [m['center_to_port'],m['port_to_center']]:
        for program in mapping.values():
            for leg in program:leg['target']=target(c,leg['target']['position'],leg['target']['id'])
    m['center']=target(c,[512,206],'landmark')
    m['ports']['upper']['dock']=target(c,[24,-178],'upper/staging');m['ports']['lower']['dock']=target(c,[280,462],'lower/staging')
    if third:
        c['platforms'][-1][2]=256
        p=port(c,'third',[3,3],'E',[488,462]);m['ports']['third']=p
        m['port_to_center']['third']=[walk(c,[280,462],'low-bank-choice')]+m['port_to_center']['lower']
        m['center_to_port']['third']=m['center_to_port']['lower']+[walk(c,[488,462],'third-port')]
    p=port(c,'onward',[4,1],'S',[512,206]);p['grid']['profile']='vertical-recoil-128/v2';m['ports']['onward']=p
    m['center_to_port']['onward']=[walk(c,[512,206],'lower-exit-launch')];m['port_to_center']['onward']=[walk(c,[512,206],'return-from-cliff')]
    m['id']=m['variant_id']=m['selection_family']='folding-open-merge'+('-three-routes'if third else'');m['functional_roles']=['merge','open_space','directed_transfer']
    from pcg.map_directed.block_grid.contracts import regions,raster
    m=declare(m,set().union(*(raster(r)for r in regions(m))));errors=validate(m)
    if errors:raise ValueError(errors)
    c=m['case'];c['ports']=[dict(id=k,position=p['dock']['position'],normal=p['normal'],support_index=p['dock']['support_indices'][0])for k,p in m['ports'].items()]
    m['source_shape_sha256']=digest(c['platforms']);m['content_version']='sha256:'+digest(m);m['source_version']=m['content_version'];return m


def return_fork(high_row=-5,with_reward=True):
    """Three actual route choices, plus a high inbound return ledge."""
    m=cliff_fork(with_reward);c=m['case'];c['platforms'].pop(7);c['platforms'][7][1]=high_row*128+96
    from pcg.map_directed.catalog_feed.adapt import target
    for mapping in [m['center_to_port'],m['port_to_center']]:
        mapping.pop('ingress',None)
        for program in mapping.values():
            for leg in program:leg['target']=target(c,leg['target']['position'],leg['target']['id'])
    p=port(c,'ingress',[4,high_row],'N',[480,high_row*128+78]);p['grid']['profile']='vertical-recoil-128/v2';m['ports']['ingress']=p
    m['port_to_center']['ingress']=[walk(c,[576,-178],'return-overlook'),walk(c,[320,-50],'third-rock'),walk(c,[192,78],'second-rock'),walk(c,[320,206],'first-rock'),walk(c,[128,334],'route-choice')]
    m['center_to_port']['ingress']=[]
    m['center']=target(c,[128,334],'route-choice')
    for k,p in m['ports'].items():p['dock']=target(c,p['dock']['position'],p['dock']['id'])
    from pcg.map_directed.block_grid.contracts import regions,raster
    from .reservation import connect
    cells=set().union(*(raster(r)for r in regions(dict(m,action_clearance=[]))))
    cells.add((4,high_row));cells,extra=connect(cells,m['ports'])
    m['action_clearance']=[];m=declare(m,cells);m['adaptation']['explicit_empty_reservations']=extra+[[4,high_row]]
    m['adaptation']['return_direction']='High return ledge is ingress only; reverse UNKNOWN until counterexample analysis'
    m['id']=m['variant_id']=m['selection_family']='three-route-return-cliff'+str(high_row)+('-cache'if with_reward else'');m['spec']['space']['core_bounds']=[0,high_row*128-128,640,896-high_row*128]
    c=m['case'];c['world_bounds']=[-128,high_row*128-128,896,768-high_row*128];c['ports']=[dict(id=k,position=p['dock']['position'],normal=p['normal'],support_index=p['dock']['support_indices'][0])for k,p in m['ports'].items()]
    errors=validate(m)
    if errors:raise ValueError(errors)
    m['source_shape_sha256']=digest(c['platforms']);m['content_version']='sha256:'+digest(m);m['source_version']=m['content_version'];return m
