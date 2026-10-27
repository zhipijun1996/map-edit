"""Local rock-shoulder recipes requested by Port demands, never a Map skeleton."""
import copy,itertools
from .graph_landforms import make,walk,jump
from pcg.map_directed.content_domains.junctions import shelf_rise
from ..factory.core.quality import digest


def merge_rock_rows(rocks):
    bands={}
    for x,y,w,h in rocks:bands.setdefault((y,h),[]).append((x,x+w))
    result=[]
    for (y,h),spans in bands.items():
        for a,b in sorted(spans):
            if result and result[-1][1]==y and result[-1][3]==h and a<=result[-1][0]+result[-1][2]:result[-1][2]=max(b,result[-1][0]+result[-1][2])-result[-1][0]
            else:result.append([a,y,b-a,h])
    return result


def terrace(span=640,rise=128,drop=128):
    if span not in [512,640,768]or rise not in [128,256]or drop not in [128,256]:raise ValueError('outside_registered_terrace_domain')
    center=[128,334];upper=[span-64,334-rise];lower=[span-24,334+drop]
    low_x=min(384,span-192)
    rocks=[[0,352,384,96],[span-192,352-rise,192,64],[low_x,352+drop,span-low_x,96]]
    heights=[[320,206]]if rise==128 else[[224,206],[384,78]]
    for x,y in heights:rocks.append([x-64,y+18,128,64])
    if drop==256:rocks.append([320,480,128,64])
    def paths(c,key,inside):
        if key=='W':return [walk(c,center,'decision')]if inside else[walk(c,[24,334],'west-mouth')]
        if key=='upper':
            if inside:
                points=[upper]+list(reversed(heights))+[center]
                out=[]
                for a,b in zip(points,points[1:]):out.append(jump(c,b,'ridge-return',1 if b[0]>a[0]else-1,.15)if b[1]==a[1]else walk(c,b,'ridge-descent'))
                return out
            points=[center]+heights+[upper];return [jump(c,b,'ridge-recoil-'+str(i),1 if b[0]>a[0]else-1,.8 if b[1]<a[1]else.15)for i,(a,b)in enumerate(zip(points,points[1:]))]+[walk(c,[span-24,upper[1]],'upper-mouth')]
        if not inside:
            return ([walk(c,[416,462],'creek-rock')]if drop==256 else[])+[walk(c,lower,'lower-mouth')]
        if drop==256:
            return [walk(c,lower,'return-launch'),shelf_rise(c,[416,462],'creek-rise',-1),walk(c,[408,462],'rim-launch'),shelf_rise(c,[320,334],'return-to-rim',-1),walk(c,center,'decision')]
        return [walk(c,[408,462],'rim-launch'),shelf_rise(c,[320,334],'return-to-rim',-1),walk(c,center,'decision')]
    m=make('branch-terrace-'+str(span)+'-'+str(rise)+'-'+str(drop),merge_rock_rows(rocks),[],center,
        [('W',[0,2],'W',[24,334]),('upper',[span//128-1,2-rise//128],'E',[span-24,334-rise]),('lower',[span//128-1,2+drop//128],'E',lower)],paths)
    m['functional_roles']=['junction','fork','merge','open_space']
    return m


def turn(rise=128,span=512):
    if rise not in [128,256,384,512,640]or span not in [512,640]:raise ValueError('outside_registered_turn_domain')
    if rise>256:return tall_turn(rise,span)
    center=[span-64,334];rocks=[[0,352,span,96],[0,352-rise,256,64],[256,224,128,64]]
    def paths(c,key,inside):
        if key=='lower':return [walk(c,center,'turn-decision')]if inside else[walk(c,[24,334],'lower-mouth')]
        if inside:return ([walk(c,[320,206],'middle-return')]if rise==256 else[])+[walk(c,center,'turn-return')]
        if rise==128:return [shelf_rise(c,[320,206],'air-turn',-1),walk(c,[24,206],'upper-mouth')]
        return [shelf_rise(c,[320,206],'turn-middle',-1),jump(c,[192,78],'turn-upper',-1),walk(c,[24,78],'upper-mouth')]
    m=make('rock-turn-'+str(span)+'-'+str(rise),merge_rock_rows(rocks),[],center,[('lower',[0,2],'W',[24,334]),('upper',[0,2-rise//128],'W',[24,334-rise])],paths)
    m['functional_roles']=['traversal','directed_transfer'];return m


def tall_turn(rise,span):
    center=[span-64,334];top=[192,334-rise]
    steps=[[320 if i%2 else span-64,334-i*128]for i in range(1,rise//128)]+[top]
    rocks=[[0,352,span,96],[0,352-rise,256,64]]+[[x-64,y+18,128,64]for x,y in steps[:-1]]
    def paths(c,key,inside):
        if key=='lower':return [walk(c,center,'turn-entry')]if inside else[walk(c,[24,334],'lower-mouth')]
        if inside:return [walk(c,p,'cliff-descent-'+str(i))for i,p in enumerate(list(reversed(steps[:-1]))+[center])]
        points=[center]+steps
        return [shelf_rise(c,b,'cliff-recoil-'+str(i),1 if b[0]>a[0]else-1)for i,(a,b)in enumerate(zip(points,points[1:]))]+[walk(c,[24,334-rise],'upper-mouth')]
    return make('rock-turn-'+str(span)+'-'+str(rise),merge_rock_rows(rocks),[],center,[('lower',[0,2],'W',[24,334]),('upper',[0,2-rise//128],'W',[24,334-rise])],paths)


def ordered(m):
    m=copy.deepcopy(m);m['port_transitions']={a+'>'+b:copy.deepcopy(m['port_to_center'][a]+m['center_to_port'][b])for a,b in itertools.permutations(m['ports'],2)}
    m['center_port']=next(iter(m['ports']));m['center']=copy.deepcopy(m['ports'][m['center_port']]['dock'])
    m['content_version']='sha256:'+digest(dict(case=m['case'],ports=m['ports'],matrix=m['port_transitions']));m['source_version']=m['content_version'];return m


def request(value):
    """The existing Workshop dispatches this finite, independently tested family."""
    p=value.get('parameters',{});kind=p.get('kind','junction');port_count=value.get('ports',{}).get('count')
    expected=p.get('port_count',port_count)if kind=='compound'else 3 if kind=='junction'else 2
    if port_count!=expected:return dict(status='needs_design',gaps=['registered local recipe Port count mismatch'])
    variants=[]
    try:
        if kind=='junction':
            for span,rise,drop in itertools.product(p.get('spans',[512,640]),p.get('rises',[128,256]),p.get('drops',[128,256])):variants.append(ordered(terrace(span,rise,drop)))
        elif kind=='turn':
            for span,rise in itertools.product(p.get('spans',[512]),p.get('rises',[128,256])):variants.append(ordered(turn(rise,span)))
        elif kind=='compound':
            from .compound_terraces import generate
            variants.append(generate(port_count,p.get('seed','local-compound'),p.get('budget',12000),p.get('component_sources')))
        else:return dict(status='needs_design',gaps=['unknown local landform responsibility'])
    except ValueError as e:return dict(status='needs_design',gaps=[str(e)])
    if p.get('mirror'):
        from pcg.map_directed.content_domains.mirror import mirror
        variants=[mirror(m)for m in variants]
    return dict(status='requires_macro_physics',content_kind='macro',modules=variants,source='existing Workshop / graph_landforms.make',new_geometry=True,production_admitted=False,
        concept=dict(junction='Shared meadow shore; visible high recoil crossing and lower creek with earned climb back',turn='Two mouths on one cliff face; airborne reversal and physically separate return',no_map_layout=True))
