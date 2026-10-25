"""Content-aware adaptation of the existing multiport producer.

No new physics or Map connector framework. All landforms exist in the canonical
Module before assembly; every changed instance requires whole-world evidence.
"""
import copy,math
from .room_modules import generate as room_generate, routes
from .synthesis import command
from ..factory.core.quality import digest


def generate(spec):
    caps=spec.get('capabilities',{})
    if caps.get('status')!='defined'or caps.get('anyOfGroups')or not {'move','jump','shot_recoil'}<=set(caps.get('allOf',[])):
        raise ValueError('unsupported_or_missing_real_recoil_capabilities')
    spec=copy.deepcopy(spec);spec['include_optional_core']=False
    m=room_generate(spec);c=m['case'];key=m['id'];W,H=spec['space']['core_bounds'][2:];base=H-spec.get('floor_margin',64)
    c['saws']=[];c['moving_platforms']=[];c['latches']=[];c['reward_sites']=[];c['shop_sites']=[]
    # Preserve the existing support/route representation and declared contacts.
    m=routes(m)
    def land(x,y,w,h,one=False):
        i=len(c['platforms']);c['platforms'].append([x,y,w,h])
        if one:c['one_way_platform_indices'].append(i)
        return i
    def target(x,y,idx,name):
        return dict(id=key+'/'+name,position=[x,y],region=[x-8,y-4,16,8],support_indices=[idx],grounded=True)
    def recoil(dest,direction=0):
        return dict(kind='module',target=copy.deepcopy(dest),budget_ticks=720,action_intent='airborne shot earns height; real landing restores actions',
            control_plan=[command('axis',value=direction),command('jump'),command('jump_release',8),command('shoot',10,direction=[0,1]),command('settle',6,target_x=dest['position'][0],deadband=4)])
    # Wide, uneven rock bodies at the lowest banks. A downward port keeps its
    # exact drop-through aperture; no solid body is inferred from the bounds.
    one=set(c['one_way_platform_indices']);down=[p for p in m['ports'].values()if p['kind']=='vertical'and p['normal'][1]>0]
    for lo,hi,i in m['floors'][base]:
        if any(lo<=p['position'][0]<=hi for p in down):continue
        one.discard(i);c['platforms'][i][3]=46
        for a,b,depth in [(0,.23,52),(.23,.64,94),(.64,1.,64)]:
            if (hi-lo)*(b-a)>0:land(lo+(hi-lo)*a,base+64,(hi-lo)*(b-a),min(depth,H-base-64))
    c['one_way_platform_indices']=sorted(one)
    # Existing lift columns become bounded recoil ascents. Intermediate broad
    # ledges alternate their landing position; there is no passive carrier.
    ascents={}
    for col in m['columns']:
        p=m['ports'].get(col['port'])if col['port']else None
        last=p['dock']if p else next(v['target']for eid,legs in m['center_to_port'].items()for v in legs if v.get('carrier_transfer',{}).get('id')==col['id']and v['carrier_transfer']['mode']=='ascend')
        height=base-last['position'][1];count=math.ceil(height/170);values=[]
        for ordinal in range(count):
            level=round(base-height*(ordinal+1)/count)
            if ordinal==count-1:dest=last
            else:
                x=col['x']+(-24 if ordinal%2 else 24)
                idx=land(col['x']-72,level+18,144,16,True);dest=target(x,level,idx,'recoil-bank/'+col['id']+'/'+str(ordinal))
            values.append(recoil(dest))
        ascents[col['id']]=values
    def convert(values):
        result=[]
        for leg in values:
            t=leg.get('carrier_transfer')
            if t:
                if t['mode']=='ascend':result+=copy.deepcopy(ascents[t['id']][:-1])+[recoil(leg['target'])]
                elif t['mode']=='cross':result.append(dict(kind='jump',target=copy.deepcopy(leg['target']),hold_ticks=20))
                else:raise ValueError('unsupported_carrier_relation/'+key)
            elif leg['kind']=='jump' and leg['target']['position'][1]==base and any(leg['target']==v['target']for eid,vs in m['port_to_center'].items()for v in vs[:1]) and spec.get('floor_margin',64)>125:
                result.append(recoil(leg['target']))
            else:result.append(copy.deepcopy(leg))
        return result
    for group in ['center_to_port','port_to_center']:
        m[group]={eid:convert(v)for eid,v in m[group].items()}
    # Reward demand is realized inside a free bank interval. This is the same
    # measured vertical bell/cache relationship, adapted to requested geometry.
    if spec['node']['role']=='reward':
        angled=spec.get('reward_mechanic')=='angled_timed_cache'
        reserved=[(col['x']-120,col['x']+120)for col in m['columns']]
        candidates=[]
        for lo,hi,idx in m['floors'][base]:
            for x in range(int(lo+100),int(hi-(400 if angled else 170)),16):
                a,b=(x-24,x+380)if angled else(x-64,x+152)
                if base<(408 if angled else 340)or any(a<r and b>l for l,r in reserved):continue
                if any(y!=base and base-(408 if angled else 340)<y<base and any(a<r and b>l for l,r,_ in spans)for y,spans in m['floors'].items()):continue
                if any(a<p['position'][0]+96 and b>p['position'][0]-96 for p in down):continue
                candidates.append((x,idx))
        if not candidates:raise ValueError('reward_chamber_space_unsatisfied/'+key)
        x,idx=candidates[0];entry=target(x,base,idx,'cache-takeoff');bell='cache-bell'
        if angled:
            offset=313.3171823051689
            upper=land(x+147.3171823051689,base-162,192,16,True)
            sealed_floor=land(x+295.3171823051689,base-162,84.682817694831,36)
            land(x+360,base-380,20,218);land(x+271.3171823051689,base-404,108.682817694831,24)
            dest=target(x+offset,base-180,upper,'cache-contact');dest['support_indices'].append(sealed_floor)
            c['latches'].append(dict(id=bell,bell=[x+24.519729614258,base-15.95894795656181],
                gate=[x+271.3171823051689,base-380,24,218],open_seconds=1.2,prompt='AIR SHOT / RECOIL / TIMED CACHE',return_access=[x+offset,base-245]))
            plan=[command('axis',value=1),command('jump'),command('jump_release',12),command('shoot',6,direction=[-.5,.8660254037844386]),command('settle',6,target_x=dest['position'][0],deadband=4)]
            outside=target(x+240,base-180,upper,'cache-exit');back=target(x+240,base,idx,'cache-return-bank')
            leaving=[dict(kind='module',target=dest,control_plan=[command('axis',value=0),command('shoot',direction=[0,-1]),command('wait',12)],budget_ticks=720),dict(kind='walk',target=outside),dict(kind='drop',target=back)]
        else:
            upper=land(x-64,base-162,192,16,True)
            sealed_floor=land(x+48,base-162,104,24);land(x+128,base-316,24,154);land(x+32,base-316,120,24)
            dest=target(x+60,base-180,upper,'cache-contact');dest['support_indices'].append(sealed_floor)
            c['latches'].append(dict(id=bell,bell=[x+4.567497253418,base-4.290283203125],gate=[x+32,base-292,16,130],open_seconds=0,prompt='AIR SHOT / RECOIL / CACHE'))
            plan=recoil(dest)['control_plan'];back=entry
            leaving=[dict(kind='walk',target=target(x,base-180,upper,'cache-exit')),dict(kind='drop',target=back)]
        c['reward_sites'].append(dict(id='cache',target=dest,required_bell=bell,reward=spec['risk_reward']['value'],opens=spec['node'].get('opens',[])))
        m['core']=dict(entry=entry,exit=dest,control_plan=plan,source='existing measured vertical/angled recoil and sealed cache; new geometry instance')
        # Route to/from the chamber across the actual existing shafts using
        # the original room router, then adapt its carrier actions to recoil.
        tmp=copy.deepcopy(m);tmp['ports']['__cache_entry']=dict(kind='side',normal=[1,0],position=entry['position'],dock=entry)
        tmp['ports']['__cache_return']=dict(kind='side',normal=[1,0],position=back['position'],dock=back)
        routed=routes(tmp)
        m['core_visit_program']=convert(routed['center_to_port']['__cache_entry'])+[dict(kind='module',target=dest,control_plan=plan,budget_ticks=720)]+leaving+convert(routed['port_to_center']['__cache_return'])
    if spec['node']['role']=='rest':
        c['shop_sites'].append(dict(id='merchant',position=m['center']['position'],price=8,item='damage_blue'))
    m['quality']={'human_fun':'unreviewed','production_admitted':False}
    m['origin']='Existing multiport generator → exposed rock / recoil banks / sealed optional bell cache; source-owned geometry, no lifts or Map fill'
    m['spec']=copy.deepcopy(spec)
    m['content_version']='sha256:'+digest({k:m[k]for k in ['case','ports','core','boundary_gates']})
    return m


def add_recoil_ravine(m):
    """Replace a real bank span, including its rock root, by a recoil crossing.

    Rewrites the existing policies over that changed source geometry. A gap is
    never added after Map assembly. This finite adapter is not universal routing.
    """
    c=m['case'];base=m['spec']['space']['core_bounds'][3]-m['spec'].get('floor_margin',64);key=m['id']
    occupied=[]
    def collect(v):
        if isinstance(v,dict):
            if 'position'in v and 'support_indices'in v and abs(v['position'][1]-base)<.01:occupied.append(v['position'][0])
            for z in v.values():collect(z)
        elif isinstance(v,list):
            for z in v:collect(z)
    for field in ['center','ports','core','center_to_port','port_to_center','core_visit_program']:collect(m.get(field))
    chosen=None
    for lo,hi,idx in sorted(m['floors'][base],key=lambda z:-(z[1]-z[0])):
        for center in range(int((lo+hi)/2),int(hi-170),16):
            a,b=center-110,center+110
            protected=[p['position'][0]for p in m['ports'].values()if p['kind']=='vertical']+[p['x']for p in m['columns']]
            if a-lo<160 or hi-b<160 or any(a-28<x<b+28 for x in occupied)or any(a-120<x<b+120 for x in protected):continue
            chosen=(lo,hi,idx,a,b);break
        if chosen:break
    if not chosen:return m
    lo,hi,idx,a,b=chosen;original=copy.deepcopy(c['platforms'][idx]);c['platforms'][idx][2]=a-lo
    right=len(c['platforms']);c['platforms'].append([b,original[1],hi-b,original[3]])
    if idx in c['one_way_platform_indices']:c['one_way_platform_indices'].append(right)
    roots=list(enumerate(copy.deepcopy(c['platforms'])));shared={p.get('shared_landing_index')for p in m['ports'].values()}
    for i,p in roots:
        if i in [idx,right]or i in shared or p[1]<base+36 or p[0]>=b or p[0]+p[2]<=a:continue
        x,y,w,h=p
        pieces=[q for q in [[x,y,max(0,min(a,x+w)-x),h],[max(b,x),y,max(0,x+w-max(b,x)),h]]if q[2]>0]
        if not pieces:c['platforms'][i]=[a-16,y,16,h]
        else:
            c['platforms'][i]=pieces[0]
            c['platforms']+=pieces[1:]
    seen=set()
    def rebind(v):
        if isinstance(v,dict):
            if id(v)in seen:return
            seen.add(id(v))
            if idx in v.get('support_indices',[])and v['position'][0]>=b:v['support_indices']=[right if j==idx else j for j in v['support_indices']]
            for z in v.values():rebind(z)
        elif isinstance(v,list):
            for z in v:rebind(z)
    for field in ['center','ports','core','center_to_port','port_to_center','core_visit_program']:rebind(m.get(field))
    rebind(c['reward_sites'])
    m['floors'][base]=[t for t in m['floors'][base]if t[2]!=idx]+[(lo,a,idx),(b,hi,right)]
    # A natural low rock arch makes height management part of the crossing.
    arch=len(c['platforms']);c['platforms'].append([a-16,base-144,b-a+32,32])
    def t(x,s,label):return dict(id=key+'/'+label,position=[x,base],region=[x-8,base-4,16,8],support_indices=[s],grounded=True)
    west=t(a-20,idx,'ravine-west');east=t(b+20,right,'ravine-east')
    def adapt_legs(values,start):
        out=[];at=start
        for raw in values:
            dest=raw['target'];x,y=at['position'];u,v=dest['position']
            crosses=raw['kind']=='walk'and abs(y-base)<.01 and abs(v-base)<.01 and ((x<a and u>b)or(x>b and u<a))
            if crosses:
                d=1 if u>x else-1;take,land=(west,east)if d>0 else(east,west)
                out.append(dict(kind='walk',target=copy.deepcopy(take)))
                out.append(dict(kind='module',target=copy.deepcopy(land),budget_ticks=720,action_intent='low-arch airborne lateral recoil across an actual ravine',
                    control_plan=[command('axis',value=d),command('jump'),command('jump_release',8),command('shoot',2,direction=[-d,0]),command('settle',6,target_x=land['position'][0],deadband=4)]))
            out.append(copy.deepcopy(raw));at=dest
        return out
    m['center_to_port']={eid:adapt_legs(v,m['center'])for eid,v in m['center_to_port'].items()}
    m['port_to_center']={eid:adapt_legs(v,m['ports'][eid]['dock'])for eid,v in m['port_to_center'].items()}
    m['core_visit_program']=adapt_legs(m['core_visit_program'],m['center'])
    m['landform_features']={'recoil_ravine':[a,base,b-a],'low_rock_arch':arch}
    m['content_version']='sha256:'+digest({k:m[k]for k in ['case','ports','core','boundary_gates']})
    return m


def sculpt_banks(m):
    """Turn long level galleries into broad rock terraces, then route over them.

    This is a source-Module geometry revision. Contact faces remain unchanged;
    internal policies explicitly jump the elevation changes. No visual-only rock.
    """
    c=m['case'];W,H=m['spec']['space']['core_bounds'][2:];base=H-m['spec'].get('floor_margin',64)
    spans=[];mapping={};one=set(c['one_way_platform_indices']);key=m['id']
    down=[p for p in m['ports'].values()if p['kind']=='vertical'and p['normal'][1]>0]
    reward=m.get('core')is not None
    for rawlevel,values in list(m['floors'].items()):
        level=float(rawlevel)
        for lo,hi,idx in values:
            # A downward-export bank retains its authored one-way aperture.
            retain_drop=(level==base and any(lo<=p['position'][0]<=hi for p in down))or(level!=base and base-level<240)
            pieces=[]
            if hi-lo>=480 and not reward and not retain_drop:
                rise=-(40+8*(int(digest(key+str(idx))[:2],16)%4))if level>=120 else 48
                cuts=[lo,round(lo+(hi-lo)*.32),round(lo+(hi-lo)*.70),hi]
                for j,offset in enumerate([0,rise,0]):
                    x,r=cuts[j],cuts[j+1];top=level+offset+18
                    body=min(112 if level==base else 80,H-top)
                    pi=idx if j==0 else len(c['platforms'])
                    rect=[x,top,r-x,body]
                    if j==0:c['platforms'][pi]=rect
                    else:c['platforms'].append(rect)
                    one.discard(pi);pieces.append((x,r,level+offset,pi))
            else:
                if not retain_drop:
                    top=c['platforms'][idx][1];c['platforms'][idx][3]=min(96 if level==base else 72,H-top);one.discard(idx)
                pieces=[(lo,hi,level,idx)]
            mapping[idx]=pieces;spans.append((level,lo,hi,pieces))
    c['one_way_platform_indices']=sorted(one)
    seen=set()
    def patch(v):
        if isinstance(v,dict):
            if id(v)in seen:return
            seen.add(id(v))
            old=v.get('support_indices',[])
            hit=next((i for i in old if i in mapping),None)
            if hit is not None:
                x,y=v['position'];part=next((p for p in mapping[hit]if p[0]<=x<=p[1]),None)
                if part is None:raise ValueError('terrace_target_outside_original_support/'+key)
                delta=part[2]-y;v['position'][1]=part[2];v['region'][1]+=delta
                v['support_indices']=[part[3]if i==hit else i for i in old]
            for z in v.values():patch(z)
        elif isinstance(v,list):
            for z in v:patch(z)
    for f in ['center','ports','core','center_to_port','port_to_center','core_visit_program']:patch(m.get(f))
    patch(c['reward_sites']);patch(c['shop_sites'])
    m['floors']={}
    for _,_,_,parts in spans:
        for a,b,y,i in parts:m['floors'].setdefault(y,[]).append((a,b,i))
    def t(x,p,label):return dict(id=key+'/'+label,position=[x,p[2]],region=[x-8,p[2]-4,16,8],support_indices=[p[3]],grounded=True)
    def rewrite(values,start):
        at=start;out=[]
        for raw in values:
            dest=raw['target'];x,y=at['position'];u,v=dest['position']
            if raw['kind']=='walk':
                same=next((ps for level,lo,hi,ps in spans if lo<=min(x,u)and max(x,u)<=hi and any(p[0]<=x<=p[1]and abs(y-p[2])<.01 for p in ps)and any(p[0]<=u<=p[1]and abs(v-p[2])<.01 for p in ps)),None)
                if same:
                    d=1 if u>x else-1
                    pairs=list(zip(same,same[1:]))
                    if d<0:pairs.reverse()
                    for left,right in pairs:
                        boundary=left[1]
                        if not min(x,u)<boundary<max(x,u)or left[2]==right[2]:continue
                        a,b=(left,right)if d>0 else(right,left)
                        take=t(boundary-d*28,a,'terrace-takeoff/'+str(boundary));land=t(boundary+d*28,b,'terrace-landing/'+str(boundary))
                        out.append(dict(kind='walk',target=take));out.append(dict(kind='jump',target=land,hold_ticks=12))
            elif raw['kind']=='drop'and y<v-100:
                # Rock galleries cannot be dropped through. Step into the real
                # open recoil shaft first, then descend through its ledges.
                options=[]
                for col in m['columns']:
                    if abs(x-col['x'])>160:continue
                    for i in c['one_way_platform_indices']:
                        p=c['platforms'][i];py=p[1]-18
                        if y+24<py<v-20 and p[0]<=col['x']<=p[0]+p[2]:options.append((py,abs(x-col['x']),i,col))
                if options:
                    _,_,_,col=min(options,key=lambda z:(z[0],z[1]));tx=col['x']+(24 if dest['position'][0]>col['x']else-24)
                    # Stay inside this open shaft past EVERY solid gallery;
                    # steering toward the bottom bank early can hit a lower
                    # gallery before the final destination. Stop only on the
                    # actual source-owned ledges, with full-body separation.
                    chain=sorted((py,i)for py,_,i,q in options if q['id']==col['id'])
                    for py,i in chain:
                        out.append(dict(kind='drop',target=dict(id=key+'/shaft-descent/'+str(i),position=[tx,py],region=[tx-8,py-4,16,8],support_indices=[i],grounded=True)))
            out.append(copy.deepcopy(raw));at=dest
        return out
    m['center_to_port']={eid:rewrite(v,m['center'])for eid,v in m['center_to_port'].items()}
    m['port_to_center']={eid:rewrite(v,m['ports'][eid]['dock'])for eid,v in m['port_to_center'].items()}
    m['core_visit_program']=rewrite(m['core_visit_program'],m['center'])
    m['content_version']='sha256:'+digest({k:m[k]for k in ['case','ports','core','boundary_gates']})
    return m


def steer_recoil_routes(m):
    """Choose takeoff steering from the actual preceding certified target.

    Only Router input policies change; no actor movement/resource assignment.
    """
    def rewrite(values,start):
        at=start
        for leg in values:
            if leg.get('action_intent')=='airborne shot earns height; real landing restores actions':
                dx=leg['target']['position'][0]-at['position'][0]
                axis=0 if abs(dx)<64 else 1 if dx>0 else-1
                leg['control_plan'][0]['value']=axis
            at=leg['target']
    for eid,v in m['center_to_port'].items():rewrite(v,m['center'])
    for eid,v in m['port_to_center'].items():rewrite(v,m['ports'][eid]['dock'])
    rewrite(m['core_visit_program'],m['center'])
    # Policies are also frozen by the canonical exporter; the raw version
    # deliberately binds them too rather than reusing a geometry-only identity.
    m['content_version']='sha256:'+digest({k:m[k]for k in ['case','ports','core','boundary_gates','center_to_port','port_to_center','core_visit_program']})
    return m
