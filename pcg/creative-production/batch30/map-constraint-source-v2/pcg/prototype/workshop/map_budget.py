"""Bind optional Module reward sockets to the Director's finite allocations.

No challenge geometry or movement program is changed. Disabled source sockets
remain lineage; only allocated services can award currency/items in this version.
This is a fresh semantic candidate and must be verified in its actual Map.
"""
import copy
from pcg.map_directed.catalog_feed.adapt import target
from pcg.prototype.factory.core.quality import digest


def checkpoint(m):
    programs=list(m.get('port_transitions',{}).values());common=None
    for program in programs:
        values={tuple(leg['target']['position'])for leg in program}
        common=values if common is None else common&values
    if common:
        center=m['center']['position'];return list(min(common,key=lambda p:sum((p[i]-center[i])**2 for i in range(2))))
    return m['center']['position'][:]


def configure(request):
    m=copy.deepcopy(request['module']);allocations=request.get('allocations',[]);source=copy.deepcopy(m['case'].get('reward_sites',[]));sites=[];shops=[];p=checkpoint(m)
    for i,allocation in enumerate(allocations):
        if allocation['kind']=='shop':shops.append(dict(id=allocation['id'],position=p[:],price=8,item='damage_blue',allocation=allocation));continue
        if source:slot=copy.deepcopy(source[min(i,len(source)-1)])
        else:
            t=target(m['case'],p,'allocated-reward');slot=dict(position=p[:],target=t,region=[p[0]-22,p[1]-8,44,16])
        slot.update(id=allocation['id'],reward_kind=allocation['kind'],amount=allocation.get('amount',1),allocation=copy.deepcopy(allocation))
        if allocation.get('item'):slot['item']=allocation['item']
        sites.append(slot)
    m['case']['reward_sites']=sites;m['case']['shop_sites']=shops
    m['adaptation']['reward_budget_binding']=dict(parent_version=m['content_version'],allocated=[s['id']for s in allocations],inactive_source_sockets=source,geometry_changed=False,source_reward_proof_inherited=False,requires_whole_map_economy_verification=True)
    m['content_version']='sha256:'+digest(dict(case=m['case'],ports=m['ports'],programs=m.get('port_transitions'),allocations=allocations));m.pop('independent_evidence',None)
    return dict(status='requires_macro_physics',modules=[m],gaps=[],production_admitted=False)
