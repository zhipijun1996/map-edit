"""Measured challenge cores adapted into source-owned banks, before assembly.

This deliberately finite adapter rejects incompatible geometry. It never turns
an unsupported challenge demand into an ordinary platform passage.
"""
import copy
from .synthesis import command
from ..factory.core.quality import digest


def target(m,x,y,index,label):
    return dict(id=m['id']+'/'+label,position=[x,y],region=[x-8,y-4,16,8],support_indices=[index],grounded=True)


def flatten(m,lo,hi,level):
    """Keep the bank's silhouette below its top; remove interfering terraces."""
    c=m['case'];spans=[];levels={}
    for y,values in m['floors'].items():
        for a,b,i in values:
            if a>=lo and b<=hi and abs(float(y)-level)<=80:
                levels[i]=float(y);spans.append((a,b,i));c['platforms'][i][1]=level+18
                c['platforms'][i][3]=min(c['platforms'][i][3],m['spec']['space']['core_bounds'][3]-level-18)
    if not spans or min(a for a,b,i in spans)!=lo or max(b for a,b,i in spans)!=hi:
        raise ValueError('challenge_bank_domain_unsatisfied/'+m['id'])
    seen=set()
    def patch(v):
        if isinstance(v,dict):
            if id(v)in seen:return
            seen.add(id(v))
            if any(i in levels for i in v.get('support_indices',[])):
                delta=level-v['position'][1];v['position'][1]=level;v['region'][1]+=delta
            for z in v.values():patch(z)
        elif isinstance(v,list):
            for z in v:patch(z)
    for f in ['center','ports','core','center_to_port','port_to_center','core_visit_program']:patch(m.get(f))
    for group in ['center_to_port','port_to_center']:
        for eid,values in m[group].items():
            out=[];at=m['center']if group=='center_to_port'else m['ports'][eid]['dock']
            for raw in values:
                leg=copy.deepcopy(raw);dest=leg['target']
                if lo<=at['position'][0]<=hi and lo<=dest['position'][0]<=hi and at['position'][1]==dest['position'][1]==level and leg['kind']in ['walk','jump']:
                    leg['kind']='walk';leg.pop('hold_ticks',None)
                if out and leg['kind']=='walk'and out[-1]['kind']=='walk'and out[-1]['target']['position'][1]==dest['position'][1] and lo<=dest['position'][0]<=hi and lo<=out[-1]['target']['position'][0]<=hi:
                    out[-1]=leg
                else:out.append(leg)
                at=dest
            m[group][eid]=out
    return spans


def cut(m,a,b,level):
    """Cut the actual rock and all roots. Rebind source support references."""
    c=m['case'];mapping={};one=set(c['one_way_platform_indices']);shared={p.get('shared_landing_index')for p in m['ports'].values()}
    for i,p in list(enumerate(copy.deepcopy(c['platforms']))):
        x,y,w,h=p
        if i in shared or y<level+18 or x>=b or x+w<=a:continue
        pieces=[q for q in [[x,y,max(0,min(a,x+w)-x),h],[max(b,x),y,max(0,x+w-max(b,x)),h]]if q[2]>0]
        if not pieces:
            # Retain index identity as a small source-owned root under a bank.
            c['platforms'][i]=[a-16,y,16,h];mapping[i]=[i];continue
        c['platforms'][i]=pieces[0];mapping[i]=[i]
        for piece in pieces[1:]:
            j=len(c['platforms']);c['platforms'].append(piece);mapping[i].append(j)
            if i in one:one.add(j)
    seen=set()
    def patch(v):
        if isinstance(v,dict):
            if id(v)in seen:return
            seen.add(id(v))
            if any(i in mapping for i in v.get('support_indices',[])):
                x,y=v['position'];indices=[j for i in v['support_indices']for j in mapping.get(i,[i])]
                v['support_indices']=[j for j in indices if c['platforms'][j][0]+12<=x<=c['platforms'][j][0]+c['platforms'][j][2]-12 and abs(c['platforms'][j][1]-y-18)<.01]
                if not v['support_indices']:raise ValueError('challenge_removed_required_landing/'+m['id']+'/'+str(v.get('id')))
            for z in v.values():patch(z)
        elif isinstance(v,list):
            for z in v:patch(z)
    for f in ['center','ports','core','center_to_port','port_to_center','core_visit_program']:patch(m.get(f))
    c['one_way_platform_indices']=sorted(one)


def route_crossing(m,left,right,forward,reverse):
    """Replace a bank crossing in both directions; keep other port duties."""
    level=left['position'][1];a=left['position'][0];b=right['position'][0];count=0
    for group in ['center_to_port','port_to_center']:
        for eid,values in m[group].items():
            at=m['center']if group=='center_to_port'else m['ports'][eid]['dock'];out=[]
            for raw in values:
                x,y=at['position'];u,v=raw['target']['position']
                if raw['kind']=='walk'and y==v==level and ((x<=a and u>=b)or(x>=b and u<=a)):
                    out+=copy.deepcopy(forward if u>x else reverse);count+=1
                out.append(copy.deepcopy(raw));at=raw['target']
            m[group][eid]=out
    if not count:raise ValueError('challenge_not_on_declared_travel/'+m['id'])
    return count


def adapt(source,spec):
    m=copy.deepcopy(source);m.pop('canonical_document',None);m['spec']=copy.deepcopy(spec);c=m['case']
    demand=spec['design_contract']['challenge'];kind=demand['family'];base=spec['space']['core_bounds'][3]-spec['floor_margin']
    def land(x,y,w,h):c['platforms'].append([x,y,w,h]);return len(c['platforms'])-1
    def support(x):
        indices=[i for i,p in enumerate(c['platforms'])if p[0]+12<=x<=p[0]+p[2]-12 and abs(p[1]-base-18)<.01]
        if not indices:raise ValueError('challenge_missing_bank/'+m['id'])
        return indices[0]
    def walk(t):return dict(kind='walk',target=t)
    def flight(t,plan,label):return dict(kind='module',target=t,budget_ticks=720,control_plan=plan,action_intent=label)
    if kind=='enemy_refund_crossing':
        lo,hi=demand['bank'];flatten(m,lo,hi,base)
        if demand.get('upper_gallery_level') is not None:
            upper=demand['upper_gallery_level'];spans=flatten(m,lo,hi,upper)
            for _,_,i in spans:c['platforms'][i][3]=16
        x=max(lo+16,m['center']['position'][0]);end=x+507.6593067560774;a=x+160;b=end-88
        cut(m,a,b,base)
        entry=target(m,x,base,support(x),'refund-takeoff');dest=target(m,end,base,support(end),'refund-landing')
        c['enemies'].append(dict(id='refund-sentry',definition='plains_sentry',position=[x+68.61352926560528,base+2],initial_idle_cooldown=.43650123032667454))
        forward=[walk(entry),flight(dest,[command('axis',value=1),command('jump'),command('jump_release',12),command('shoot',12,direction=[-.45,.8930285549745876]),command('shoot',18,direction=[-1,.05]),command('settle',6,target_x=end,deadband=4)],'Hit a real enemy while airborne, refund the shot, recoil again to the far bank')]
        forward[-1]['depleted_enemy']='refund-sentry'
        forward[-1]['depleted_plan']=[command('axis',value=1),dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte',value=a-24),timeout=120)),command('jump'),command('jump_release',20),command('shoot',4,direction=[-1,0]),command('settle',6,target_x=end,deadband=4)]
        back_a=target(m,b+20,base,support(b+20),'refund-return-east');back_b=target(m,a-20,base,support(a-20),'refund-return-west')
        fight=flight(copy.deepcopy(back_a),[command('axis',value=0),command('shoot',aim_cell={'kind':'enemy','id':'refund-sentry'},direction=[-1,0]),command('settle',target_x=back_a['position'][0],deadband=4),command('shoot',30,aim_cell={'kind':'enemy','id':'refund-sentry'},direction=[-1,0]),command('wait',36)],'Defeat the surviving sentry from the broad far bank; actively countersteer the ground recoil between shots')
        reverse=[walk(back_a),fight,flight(back_b,[command('axis',value=-1),command('jump'),command('jump_release',12),command('shoot',2,direction=[1,0]),command('settle',6,target_x=back_b['position'][0],deadband=4)],'Return across the gap without assuming an enemy is still alive'),dict(kind='jump',target=copy.deepcopy(entry),hold_ticks=12)]
        used=route_crossing(m,entry,dest,forward,reverse)
        pit=land(a,base+72,b-a,24)
        c['thorns'].append(dict(surface_id='refund-pit',platform_index=pit,face='top',start_offset=0,length=b-a,depth=12,damage=1,contact_interval=.7))
    elif kind in ['timed_recoil_tunnel','precision_recoil_tunnel']:
        if kind=='timed_recoil_tunnel':
            lo,hi=demand['bank'];flatten(m,lo,hi,base);a,b=demand['gap'];cut(m,a,b,base)
            arch=land(a-16,base-144,b-a+32,32)
        else:
            a,_,width=m['landform_features']['recoil_ravine'];b=a+width;arch=m['landform_features']['low_rock_arch']
        left=target(m,a-20,base,support(a-20),'tunnel-west');right=target(m,b+20,base,support(b+20),'tunnel-east')
        plans=[]
        for d,dest in [(1,right),(-1,left)]:
            plans.append([command('axis',value=d),command('jump'),command('jump_release',8),command('shoot',2,direction=[-d,0]),command('settle',6,target_x=dest['position'][0],deadband=4)])
        if kind=='timed_recoil_tunnel':
            c['latches'].append(dict(id='tunnel-bell',bell=[left['position'][0]-12,base-62],gate=[b-28,base-112,20,208],open_seconds=.8,prompt='AIR SHOT + RECOIL',return_access=[right['position'][0]+12,base-62]))
            plans[1]=[command('axis',value=0),command('shoot',direction=[.1900219068833979,-.9817798505642229]),command('wait',18)]+plans[1]
            used=route_crossing(m,left,right,[walk(left),flight(right,plans[0],'Shoot behind while airborne; the same shot opens the gate and propels the crossing')],[walk(right),flight(left,plans[1],'Reopen from the stable return bank, then recoil across; no state reset')])
        else:
            # Replace existing ravine policies so causal metadata survives export.
            used=0
            for group in ['center_to_port','port_to_center']:
                for values in m[group].values():
                    for leg in values:
                        if 'low-arch airborne' in leg.get('action_intent',''):
                            leg['action_intent']='Precision recoil under a real spiked rock ceiling';used+=1
            if not used:raise ValueError('precision_demand_has_no_actual_crossing')
        p=c['platforms'][arch]
        c['thorns'].append(dict(surface_id='tunnel-ceiling',platform_index=arch,face='bottom',start_offset=8,length=p[2]-16,depth=8,damage=1,contact_interval=.7))
        pit=land(a,base+72,b-a,24)
        c['thorns'].append(dict(surface_id='tunnel-pit',platform_index=pit,face='top',start_offset=0,length=b-a,depth=12,damage=1,contact_interval=.7))
    else:raise ValueError('unsupported_challenge_family/'+kind)
    m['realized_challenge']=dict(family=kind,demand=demand,affected_routes=used,fun_approval=False)
    m['origin']='Demand-driven adaptation of measured action cores; failed content is never replaced by generic banks'
    m['content_version']='sha256:'+digest({k:m[k]for k in ['case','ports','core','boundary_gates']})
    return m
