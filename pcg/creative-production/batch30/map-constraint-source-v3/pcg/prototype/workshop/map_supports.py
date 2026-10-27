"""Explicit coplanar unions of OWNED terrain; positions and inputs stay exact."""
import copy
from pcg.prototype.factory.core.quality import digest


def configure(request):
    m=copy.deepcopy(request['module']);changes=[]
    def visit(value):
        if isinstance(value,dict):
            if all(k in value for k in ['position','region','support_indices']):
                x,y=value['position'];half=12+max(abs(value['region'][0]-x),abs(value['region'][0]+value['region'][2]-x));same=[i for i,r in enumerate(m['case']['platforms'])if abs(r[1]-y-18)<1.1 and r[0]<x+half and r[0]+r[2]>x-half]
                # Every old expected support remains required to exist at the
                # exact target height. Add only its own coplanar neighbours.
                if not set(value['support_indices'])<=set(same):raise ValueError('declared_support_not_at_target_floor')
                if same!=value['support_indices']:changes.append(dict(target=value.get('id'),before=value['support_indices'][:],after=same));value['support_indices']=same
            for v in value.values():visit(v)
        elif isinstance(value,list):
            for v in value:visit(v)
    for name in ['ports','center','core','port_transitions','port_to_center','center_to_port','core_visit_program']:
        if name in m:visit(m[name])
    for site in m['case'].get('reward_sites',[]):visit(site)
    m['adaptation']['owned_support_union']=dict(parent_version=m['content_version'],changes=changes,position_or_region_changed=False,control_inputs_changed=False,foreign_module_supports_added=False,physics='PENDING fresh whole-world verification')
    m.pop('independent_evidence',None);m['content_version']='sha256:'+digest(dict(case=m['case'],ports=m['ports'],matrix=m.get('port_transitions'),center=m['center'],boundary=m['boundary_gates']))
    return dict(status='requires_macro_physics',modules=[m],gaps=[],production_admitted=False)
