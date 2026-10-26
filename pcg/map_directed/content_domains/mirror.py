"""Rigid horizontal variants retain all ordered programs; always fresh physics."""
import copy
from pcg.prototype.factory.core.quality import digest


def mirror(module):
    m=copy.deepcopy(module);g=m['block_grid'];w=(max(p[0]for p in g['cells'])+1)*g['size']
    def point(p):return[w-p[0],p[1]]
    def rect(r):return[w-r[0]-r[2],*r[1:]]
    def target(t):
        t=copy.deepcopy(t);t['position']=point(t['position']);t['region']=rect(t['region']);return t
    def plan(ops):
        out=copy.deepcopy(ops)
        for o in out:
            if o['op']=='axis':o['value']=-o['value']
            if 'direction'in o:o['direction'][0]*=-1
            if 'target_x'in o:o['target_x']=w-o['target_x']
            d=o.get('trigger',{}).get('dynamic',{})
            if d.get('kind')=='actor_x':d['value']=w-d['value'];d['direction']={'gte':'lte','lte':'gte'}[d['direction']]
        return out
    def legs(raw):
        result=copy.deepcopy(raw)
        for l in result:
            l['target']=target(l['target'])
            for k in ['control_plan','depleted_plan']:
                if k in l:l[k]=plan(l[k])
        return result
    c=m['case'];old=c['platforms'];c['platforms']=[rect(r)for r in old];c['hazards']=[rect(r)for r in c.get('hazards',[])]
    for t in c.get('thorns',[]):
        if t['face']in ['top','bottom']:t['start_offset']=old[t['platform_index']][2]-t['start_offset']-t['length']
        else:t['face']={'left':'right','right':'left'}[t['face']]
    for s in c.get('saws',[]):s['origin']=point(s['origin']);s['travel'][0]*=-1
    for p in c.get('moving_platforms',[]):p['start']=point(p['start']);p['finish']=point(p['finish'])
    for l in c.get('latches',[]):
        l['bell']=point(l['bell']);l['gate']=rect(l['gate'])
        if l.get('return_access'):l['return_access']=point(l['return_access'])
        for k in ['occupancy','carrier_dock']:
            if l.get(k):l[k]['rect']=rect(l[k]['rect'])
        if l.get('sequence_gate'):l['sequence_gate']=rect(l['sequence_gate'])
    for e in c.get('enemies',[]):e['position']=point(e['position'])
    for h in c.get('hooks',[]):h['x']=w-h['x']
    for k in ['reward_sites','shop_sites']:
        for s in c.get(k,[]):
            if 'position'in s:s['position']=point(s['position'])
            if 'region'in s:s['region']=rect(s['region'])
            if 'target'in s:s['target']=target(s['target'])
    for k in ['spawn','entry_port','exit_port']:c[k]=point(c[k])
    c['goal']=rect(c['goal']);c['world_bounds']=rect(c['world_bounds']);c['control_plan']=plan(c['control_plan'])
    for p in m['ports'].values():
        p['position']=point(p['position']);p['normal'][0]*=-1;p['aperture']=rect(p['aperture']);p['dock']=target(p['dock'])
        p['grid']['cell'][0]=w//g['size']-1-p['grid']['cell'][0];p['grid']['edge']={'W':'E','E':'W','N':'N','S':'S'}[p['grid']['edge']]
    c['ports']=[dict(id=k,position=p['dock']['position'],normal=p['normal'],support_index=p['dock']['support_indices'][0])for k,p in m['ports'].items()]
    m['center']=target(m['center']);m['action_clearance']=[rect(r)for r in m['action_clearance']]
    for k in ['center_to_port','port_to_center','port_transitions']:m[k]={key:legs(v)for key,v in m.get(k,{}).items()}
    for choices in m.get('transition_options',{}).values():
        for choice in choices:choice['program']=legs(choice['program'])
    g['cells']=sorted([[w//g['size']-1-x,y]for x,y in g['cells']]);g['port_bindings']=[dict(port_id=k,**p['grid'])for k,p in m['ports'].items()]
    m['spec']['ports']=list(m['ports'].values());m['variant_id']+='/mirror-x';m['source_shape_sha256']=digest(c['platforms'])
    for key in ['explicit_empty_reservations','empty_reserved_blocks_added','measured_empty_reservation_added']:
        if key in m['adaptation']:m['adaptation'][key]=[[w//g['size']-1-x,y]for x,y in m['adaptation'][key]]
    m['adaptation']['horizontal_mirror']=dict(width=w,source_physics_inherited=False);m.pop('independent_evidence',None)
    m['content_version']='sha256:'+digest(dict(case=c,ports=m['ports'],out=m['center_to_port'],incoming=m['port_to_center'],matrix=m.get('port_transitions',{})))
    return m
