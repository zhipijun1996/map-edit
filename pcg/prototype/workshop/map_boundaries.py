"""Module-owned conditional one-way shutters, never Map connector terrain."""
import copy
from pcg.map_directed.block_grid.contracts import regions,raster,declare,validate
from pcg.map_directed.content_domains.reservation import connect
from pcg.prototype.factory.core.quality import digest


def configure(request):
    m=copy.deepcopy(request['module']);edge=request['edge'];key=edge['id'];owner=m['id'];p=m['ports'][key];inset=request.get('inset',0);height=request.get('height',512)
    if p['normal'][0]==0:return dict(status='needs_design',modules=[],gaps=['Vertical conditional shutter profile requires independent development'])
    px,py=p['position'];normal=p['normal'][0];floor=py+p.get('crossing_offset',[0,0])[1]+18;plane=px-normal*inset
    bounds=[plane-8 if normal>0 else plane,floor-height,8,height]
    for other,q in m['ports'].items():
        if other!=key and q['normal']==p['normal']and q['position'][0]==px and bounds[1]-18<q['dock']['position'][1]<floor+18:return dict(status='needs_design',modules=[],gaps=['Shutter would cut another same-face Port'])
    direction=p['normal'][:]if edge['from']==owner else[-v for v in p['normal']]
    gate=dict(id='state-boundary/'+key,edge_id=key,bounds=bounds,direction=direction,switch=edge.get('switch'),one_way=not edge['bidirectional'],owner_module=owner,from_module=edge['from'],to_module=edge['to'],source='Existing Workshop / exact Module boundary adapter',inset=inset,profile='basic-plains-shutter-'+str(height)+'/v1')
    m['boundary_gates'].append(gate)
    if gate['one_way']:
        forbidden=0 if owner==edge['from']else 1
        m['port_transitions']={pair:program for pair,program in m['port_transitions'].items()if pair.split('>')[forbidden]!=key}
        (m['port_to_center']if forbidden==0 else m['center_to_port']).pop(key,None)
    m['case']['gate_specs']=copy.deepcopy(m['boundary_gates']);m['case']['initial_opened_flags']=sorted({g['switch']for g in m['boundary_gates']if g.get('switch')})
    rr=regions(m)+[g['bounds']for g in m['boundary_gates']];cells=set().union(*(raster(r)for r in rr))
    try:cells,added=connect(cells,m['ports'])
    except ValueError as e:return dict(status='needs_design',modules=[],gaps=[str(e)])
    m=declare(m,cells);errors=validate(m)
    if errors:return dict(status='needs_design',modules=[],gaps=errors)
    m['adaptation']['state_boundary_binding']=dict(parent_version=m['content_version'],gate=gate,terrain_added=0,inputs_changed=False,physics='PENDING actual full-map states and bypass probes')
    m.pop('independent_evidence',None);m['content_version']='sha256:'+digest(dict(case=m['case'],ports=m['ports'],matrix=m['port_transitions'],boundary=m['boundary_gates']));m['variant_id']+='/state-'+key+'-'+str(inset)
    return dict(status='requires_macro_physics',modules=[m],gaps=[],production_admitted=False)
