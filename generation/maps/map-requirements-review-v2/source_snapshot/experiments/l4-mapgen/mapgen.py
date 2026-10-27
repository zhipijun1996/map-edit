#!/usr/bin/env python3
"""Isolated L4 mission/exploration/constraint/layout experiment, never a physics proof."""
from __future__ import annotations
import argparse, copy, csv, hashlib, heapq, json, math, os, platform, sys, time, tracemalloc
from collections import Counter, defaultdict, deque
from pathlib import Path
VERSION = 'l4-mapgen-experiment-v1'
ROOT = Path(__file__).resolve().parent
if (ROOT / '.deps').exists(): sys.path.insert(0, str(ROOT / '.deps'))
try:
    import clingo
except ImportError:
    clingo = None
PROFILES = {
    'plains': {'abilities':['jump','shot_recoil'], 'main_nodes':6, 'vertical_weight':0.35},
    'forest': {'abilities':['jump','shot_recoil','grapple'], 'main_nodes':6, 'vertical_weight':0.70},
}
def canonical(data): return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',',':'))
def digest(data): return hashlib.sha256(canonical(data).encode()).hexdigest()
class RandomStream:
    """Same counter SHA256/52-bit selection as RunRandomStream, separate namespaces."""
    def __init__(self, seed, namespace, stage='experiment', version=VERSION):
        self.key=json.dumps([str(seed),namespace,stage,version,1],ensure_ascii=False,separators=(',',':')); self.counter=0
    def next_int(self,n):
        if n<=0: return -1
        h=hashlib.sha256((self.key+':'+str(self.counter)).encode()).hexdigest();self.counter+=1
        return int(h[:13],16)%n
    def choice(self,a): return a[self.next_int(len(a))]
    def shuffle(self,a):
        a=list(a)
        for i in range(len(a)-1,0,-1): j=self.next_int(i+1);a[i],a[j]=a[j],a[i]
        return a

def default_catalog():
    # Explicit synthetic footprints: never extracted from, or certified as, runtime modules.
    defs=[]
    for name,w,h,shape in [('court',7,5,'rect'),('shaft',5,7,'rect'),('bough',5,4,'L'),('nook',3,3,'rect')]:
        cells=[[x,y] for y in range(h) for x in range(w) if shape=='rect' or y>=h-2 or x<2]
        roles=['start','hub','lesson','rest','prep','boss'] if name in ['court','shaft'] else ['challenge','reward']
        defs.append({'id':'synthetic/'+name,'footprint':cells,'port_type':'grounded','roles':roles, 'requirements':[], 'physics':'unverified'})
    return {'version':1,'kind':'synthetic_fixed_catalog','units':'abstract_cells','provenance':{'source':'authored experiment fixtures','runtime_admitted':False},'templates':defs}

def add_edge(g,a=None,b=None,**kw):
    a = kw.pop("from", a); b = kw.pop("to", b)
    e={'id':f'e{len(g["edges"])}','from':a,'to':b,'requires':[],'switch':None,'cost':1.0,'purpose':'traverse','bidirectional':True}
    e.update(kw);g['edges'].append(e);return e

def mission(seed,region):
    rng=RandomStream(seed,'mission')
    g={'entry':'m0','goal':'m5','initial_abilities':PROFILES[region]['abilities'][:], 'nodes':[], 'edges':[], 'rewrite_log':[]}
    for i,role in enumerate(['start','hub','lesson','rest','prep','boss']):
        g['nodes'].append({'id':f'm{i}','role':role,'grants':[],'opens':['boss_access'] if role=='prep' else [], 'reward':0,'risk':0,'intent':role,'ideal':[i*16,0]})
    for i in range(5):add_edge(g,f'm{i}',f'm{i+1}',purpose='main',switch='boss_access' if i==4 else None,cost=1.0)
    # Rewriting replaces three abstract reward obligations with challenge chains.
    lengths=[3+rng.next_int(3),3+rng.next_int(3)]
    if sum(lengths)>9: lengths[1]-=1
    lengths.append(12-sum(lengths))
    anchors=[(1,3,-1),(0,2,1),(3,4,1)]
    branches=[]
    for bi,(n,(a,b,side)) in enumerate(zip(lengths,anchors)):
        chain=[]
        for j in range(n):
            nid=f'b{bi}_{j}';last=j==n-1
            if bi<2:
                x=a*16+(b-a)*16*(j+1)/(n+1); y=side*(12+2*rng.next_int(2))
            else:
                # Outer optional expedition, spacious enough for long chain templates.
                points=[[48,26],[64,26],[80,26],[96,26],[96,12],[80,12]]
                x,y=points[j]
            risk=1+bi+(1 if region=='forest' else 0)
            g['nodes'].append({'id':nid,'role':'reward' if last else 'challenge','grants':[], 'opens':['return_gate'] if last and bi==2 else [],'reward':[12,24,36][bi] if last else 0,'risk':risk,'intent':['sightline_rejoin','alternative_approach','deep_reward_return'][bi], 'ideal':[round(x),y]})
            chain.append(nid)
        required='grapple' if region=='forest' and bi==2 else 'shot_recoil'
        path=[f'm{a}']+chain+[f'm{b}']
        for j,(u,v) in enumerate(zip(path,path[1:])):
            add_edge(g,u,v,purpose='reward_challenge' if bi==2 else 'alternative_route',requires=[required] if j==0 else [],cost=1.3+0.4*bi,bidirectional=not (bi==2 and j==len(path)-2))
        branches.append({'id':f'branch_{bi}','nodes':chain,'entry':f'm{a}','rejoin':f'm{b}','reward':chain[-1]})
        g['rewrite_log'].append({'rule':'reward_obligation_to_challenge_rejoin','branch':bi,'length':n,'entry':f'm{a}','rejoin':f'm{b}'})
    g['branches']=branches
    # Discovery at deep reward opens a return shortcut, not an initially usable bridge.
    add_edge(g,branches[2]['reward'],'m3',purpose='return_shortcut',switch='return_gate',cost=0.7,bidirectional=False)
    return g

def candidate_links(g):
    out=[]
    for b in g['branches']:
        chain=b['nodes']
        if len(chain)>=3:
            out.append({'from':chain[0],'to':chain[-1],'purpose':'risky_alternative','requires':['shot_recoil'],'cost':3.3,'bidirectional':True,'switch':None})
        out.append({'from':chain[-1],'to':b['entry'],'purpose':'reward_return_shortcut','requires':[],'cost':0.8,'bidirectional':False,'switch':'return_gate' if b['id']=='branch_2' else None})
    return out

def grammar_a(base,seed):
    g=copy.deepcopy(base);r=RandomStream(seed,'exploration_A')
    for link in r.shuffle(candidate_links(g))[:r.next_int(3)]:add_edge(g,**link)
    return g, {'method':'bounded graph rewrite recipe','added_links':len(g['edges'])-len(base['edges'])}

def asp_b(base,seed):
    if clingo is None: return None,{'error':'clingo_unavailable','method':'not_run'}
    # ASP checks a finite monotonic-switch state graph for every candidate selection.
    # Capability predicates are evaluated against this experiment's real initial profile;
    # no in-run grant is claimed here. Independent Python state exploration rechecks it.
    links=candidate_links(base);ids={n['id']:i for i,n in enumerate(base['nodes'])}
    all_switches=sorted({s for n in base['nodes'] for s in n['opens']})
    bits={s:1<<i for i,s in enumerate(all_switches)}
    masks=range(1<<len(bits));node_mask={n['id']:sum(bits[s] for s in n['opens']) for n in base['nodes']}
    facts=[f'node({n}).' for n in ids.values()]+[f'mask({m}).' for m in masks]
    for n in base['nodes']:
        if n['reward'] or n['role']=='boss':facts.append(f'objective({ids[n["id"]]}).')
    def transitions(e):
        if not set(e['requires'])<=set(base['initial_abilities']):return []
        pairs=[(e['from'],e['to'])]+([(e['to'],e['from'])] if e['bidirectional'] else [])
        return [(ids[a],m,ids[b],m|node_mask[b]) for a,b in pairs for m in masks if not e['switch'] or m&bits[e['switch']]]
    for e in base['edges']:
        for t in transitions(e):facts.append('fixed('+','.join(map(str,t))+').')
    for i,e in enumerate(links):
        facts.append(f'candidate({i}).')
        for t in transitions(e):facts.append('optional('+','.join(map(str,(i,)+t))+').')
    r=RandomStream(seed,'asp_preferences')
    for i in range(len(links)):facts.append(f'preference({i},{1+r.next_int(10)}).')
    goal=ids[base['goal']];entry=ids[base['entry']];initial=node_mask[base['entry']]
    facts.extend([f'goal({goal}).',f'entry({entry}).',f'reach({entry},{initial}).'])
    for m in masks:
        if m&bits['boss_access']:facts.append(f'boss_open({m}).')
    program='\n'.join(facts)+'''\n2 { selected(I):candidate(I) } 3.
arc(F,S,T,R) :- fixed(F,S,T,R).
arc(F,S,T,R) :- selected(I),optional(I,F,S,T,R).
reach(T,R) :- reach(F,S),arc(F,S,T,R).
objective_reached(N) :- reach(N,S).
:- objective(N),not objective_reached(N).
safe(N,S) :- entry(N),mask(S).
safe(N,S) :- goal(N),mask(S).
safe(F,S) :- arc(F,S,T,R),safe(T,R).
:- reach(N,S),not safe(N,S).
:- goal(N),reach(N,S),not boss_open(S).
#maximize { W,I : selected(I), preference(I,W) }.
#show selected/1.
'''
    ctl=clingo.Control(['--seed='+str(RandomStream(seed,'clingo').next_int(2147483647)),'--opt-mode=opt','--warn=none']);ctl.add('base',[],program);ctl.ground([('base',[])])
    selected=[];models=0;start=time.perf_counter()
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            models+=1;selected=sorted(a.arguments[0].number for a in model.symbols(shown=True))
        result=handle.get()
    if not result.satisfiable:return None,{'error':'asp_unsatisfiable','models':models}
    g=copy.deepcopy(base)
    for i in selected:add_edge(g,**links[i])
    return g,{'method':'clingo ASP candidate cyclic augmentation','solver':clingo.__version__,'selected':selected,'models':models,'solve_ms':(time.perf_counter()-start)*1000,'scope':'finite (node, monotonic opened-switch-mask) reachability, universal escape and boss gate; Python state validator independently rechecks','program_sha256':hashlib.sha256(program.encode()).hexdigest(),'program':program}

def expand_arcs(g,disabled_edges=frozenset()):
    adj=defaultdict(list)
    for e in g['edges']:
        if e['id'] in disabled_edges:continue
        adj[e['from']].append((e['to'],e))
        if e['bidirectional']:adj[e['to']].append((e['from'],e))
    return adj

def state_space(g,*,disabled_nodes=frozenset(),disabled_edges=frozenset(),max_states=16384):
    nodes={n['id']:n for n in g['nodes']};adj=expand_arcs(g,disabled_edges)
    def acquire(n,abilities,opened):
        if n in disabled_nodes:return abilities,opened
        return abilities|frozenset(nodes[n]['grants']),opened|frozenset(nodes[n]['opens'])
    a,s=acquire(g['entry'],frozenset(g['initial_abilities']),frozenset());start=(g['entry'],a,s)
    queue=deque([start]);seen={start};transitions=defaultdict(list);reverse=defaultdict(list)
    while queue:
        current=queue.popleft();nid,have,opened=current
        for to,e in adj[nid]:
            if not set(e['requires'])<=have or (e['switch'] and e['switch'] not in opened):continue
            new_a,new_s=acquire(to,have,opened);nxt=(to,new_a,new_s)
            transitions[current].append((nxt,e));reverse[nxt].append(current)
            if nxt not in seen:
                seen.add(nxt)
                if len(seen)>max_states:raise ValueError('state_budget_exceeded')
                queue.append(nxt)
    return start,seen,transitions,reverse

def shortest_states(start,transitions):
    distances={start:0.0};queue=[(0.0,0,start)];counter=0
    while queue:
        d,_,s=heapq.heappop(queue)
        if d!=distances[s]:continue
        for to,e in transitions[s]:
            nd=d+float(e['cost'])
            if nd+1e-9<distances.get(to,math.inf):
                distances[to]=nd;counter+=1;heapq.heappush(queue,(nd,counter,to))
    return distances

def validate_graph(g):
    errors=[];nodes={n['id']:n for n in g['nodes']}
    if len(nodes)!=len(g['nodes']):errors.append('duplicate_node_ids')
    if g['entry'] not in nodes or g['goal'] not in nodes:return ['missing_endpoints'],{}
    ids=[e['id'] for e in g['edges']]
    if len(set(ids))!=len(ids):errors.append('duplicate_edge_ids')
    known=set(g['initial_abilities'])|{a for n in nodes.values() for a in n['grants']};switches={a for n in nodes.values() for a in n['opens']}
    for e in g['edges']:
        if e['from'] not in nodes or e['to'] not in nodes:errors.append('unknown_edge_endpoint')
        if not set(e['requires'])<=known:errors.append('unknown_or_ungranted_ability:'+e['id'])
        if e['switch'] and e['switch'] not in switches:errors.append('unknown_switch:'+e['id'])
        if not math.isfinite(e['cost']) or e['cost']<=0:errors.append('invalid_cost:'+e['id'])
    if errors:return errors,{}
    try:start,states,trans,reverse=state_space(g)
    except ValueError as e:return [str(e)],{}
    reached={s[0] for s in states}
    if g['goal'] not in reached:errors.append('goal_unreachable')
    for n in nodes.values():
        if (n['reward'] or n['grants']) and n['id'] not in reached:errors.append('objective_unreachable:'+n['id'])
    # Universal reachable-state escape: every state must reach entry OR completion.
    safe={s for s in states if s[0] in [g['entry'],g['goal']]};queue=deque(safe)
    while queue:
        for previous in reverse[queue.popleft()]:
            if previous not in safe:safe.add(previous);queue.append(previous)
    if states-safe:errors.append('softlock_states:'+str(len(states-safe)))
    # Independent forbidden bypass witness: suppress prep's grant/open, boss must fail.
    prep={n['id'] for n in nodes.values() if n['role']=='prep'}
    if prep and any(s[0]==g['goal'] for s in state_space(g,disabled_nodes=prep)[1]):errors.append('boss_gate_bypass')
    return errors,{'reachable_states':len(states),'reachable_nodes':len(reached),'unsafe_states':len(states-safe),'ability_lock_correct':not errors,'boss_gate_correct':'boss_gate_bypass' not in errors,'scope':'monotonic capabilities/switches; no consumables, combat or physical resources'}

def graph_distances(g,source,disabled=None):
    adj=expand_arcs(g,frozenset([disabled]) if disabled else frozenset());q=[(0.0,source)];d={source:0.0}
    while q:
        x,n=heapq.heappop(q)
        if x!=d[n]:continue
        for v,e in adj[n]:
            nd=x+e['cost']
            if nd<d.get(v,math.inf):d[v]=nd;heapq.heappush(q,(nd,v))
    return d

def topology_signature(g,semantic=False):
    """Isomorphism invariant WL fingerprint, not an exact isomorphism certificate."""
    initial={n['id']:(n['role'] if semantic else ('entry' if n['id']==g['entry'] else 'goal' if n['id']==g['goal'] else 'node')) for n in g['nodes']}
    colors={k:digest(v) for k,v in initial.items()};adj=expand_arcs(g)
    for _ in range(len(g['nodes'])):
        nxt={}
        for n in colors:
            neighbors=[]
            for v,e in adj[n]:
                label=[e['purpose'],sorted(e['requires']),e['switch'],round(e['cost'],2)] if semantic else []
                neighbors.append([label,colors[v]])
            incoming=[]
            for e in g['edges']:
                if e['to']==n:incoming.append(colors[e['from']])
                if e['bidirectional'] and e['from']==n:incoming.append(colors[e['to']])
            nxt[n]=digest([initial[n],sorted(neighbors,key=canonical),sorted(incoming)])
        colors=nxt
    return digest(sorted(colors.values()))

def graph_metrics(g, signatures=True):
    start,states,trans,_=state_space(g);d=shortest_states(start,trans)
    goal_cost=min((cost for s,cost in d.items() if s[0]==g['goal']),default=math.inf)
    rewards=[]
    for n in g['nodes']:
        if not n['reward']:continue
        cost=min((v for s,v in d.items() if s[0]==n['id']),default=math.inf)
        via=min((d[s0]+min((v for s,v in shortest_states(s0,trans).items() if s[0]==g['goal']),default=math.inf) for s0 in states if s0[0]==n['id']),default=math.inf)
        rewards.append({'node':n['id'],'value':n['reward'],'first_visit_cost':round(cost,3),'completion_detour':round(via-goal_cost,3),'risk':n['risk']})
    shortcuts=[]
    for e in g['edges']:
        if 'shortcut' not in e['purpose']:continue
        before=graph_distances(g,e['from'],e['id']).get(g['entry'],math.inf)
        after=graph_distances(g,e['from']).get(g['entry'],math.inf)
        saving=before-after
        shortcuts.append({'edge':e['id'],'return_saving_all_open':round(saving,3),'effective':math.isfinite(saving) and saving>0.01,'requires_discovery':bool(e['switch'])})
    # Count bounded simple route choices; finite cap is reported, not hidden.
    count=0;adj=expand_arcs(g);cap=128
    def walk(n,seen):
        nonlocal count
        if count>=cap:return
        if n==g['goal']:count+=1;return
        for v,e in adj[n]:
            if v not in seen:walk(v,seen|{v})
    walk(g['entry'],{g['entry']})
    depths=[len(b['nodes']) for b in g['branches']]
    # Value/cost mismatch is diagnostic. Reward values are fixed, not fitted to metric.
    ratios=[r['value']/max(1,r['completion_detour']+r['risk']) for r in rewards]
    mean=sum(ratios)/len(ratios);variance=sum((x-mean)**2 for x in ratios)/len(ratios)
    choices=sum(1 for n in g['nodes'] if len({x for x,_ in adj[n['id']]})>=3)
    score=10/(1+goal_cost/5)+min(choices,7)*0.5+sum(s['effective'] for s in shortcuts)*1.1+sum(min(r['completion_detour'],8) for r in rewards)*0.12-math.sqrt(variance)*0.25
    return {'main_completion_cost':round(goal_cost,3),'branch_depths':depths,'branch_depth_range':max(depths)-min(depths),'cycle_rank_undirected':len({tuple(sorted((e['from'],e['to']))) for e in g['edges']})-len(g['nodes'])+1,'route_choices_bounded':count,'route_choices_cap':cap,'route_choices_are_all_open':True,'decision_hubs':choices,'rewards':rewards,'shortcuts':shortcuts,'effective_shortcuts':sum(s['effective'] for s in shortcuts),'reward_value_cost_ratio_std':round(math.sqrt(variance),3),'quality_heuristic':round(score,4),'quality_is_fun_rating':False,'topology_wl_signature':topology_signature(g) if signatures else None,'experience_wl_signature':topology_signature(g,True) if signatures else None}

def mutate(g,rng,base_edge_count):
    child=copy.deepcopy(g);extras=child['edges'][base_edge_count:];links=candidate_links(child)
    operation=rng.next_int(3)
    if operation==0 and extras:
        victim=rng.choice(extras);child['edges'].remove(victim)
    elif operation==1 and extras:
        victim=rng.choice(extras);victim['cost']=rng.choice([0.8,1.5,2.5,3.3]);victim['bidirectional']=rng.next_int(2)==0
    else:
        choices=[l for l in links if not any(e['from']==l['from'] and e['to']==l['to'] for e in child['edges'])]
        if choices and len(extras)<4:add_edge(child,**rng.choice(choices))
    for i,e in enumerate(child['edges']):e['id']=f'e{i}'
    return child

def evolve_c(base,seed,evaluations=24,mutation=True):
    rng=RandomStream(seed,'evolution_C' if mutation else 'random_C_control');archive={};history=[];valid=0
    for i in range(evaluations):
        if archive and mutation:
            parent=rng.choice([archive[k][1] for k in sorted(archive)]);g=mutate(parent,rng,len(base['edges']))
        else:
            g=copy.deepcopy(base)
            for link in rng.shuffle(candidate_links(g))[:rng.next_int(5)]:add_edge(g,**link)
        errors,_=validate_graph(g)
        if errors:history.append({'evaluation':i,'valid':False,'errors':errors});continue
        m=graph_metrics(g, signatures=False);valid+=1
        descriptor=(min(5,int(m['main_completion_cost']//2)),min(4,m['effective_shortcuts']),min(3,int(m['reward_value_cost_ratio_std']//1)))
        score=m['quality_heuristic'];accepted=descriptor not in archive or score>archive[descriptor][0]
        if accepted:archive[descriptor]=(score,g)
        history.append({'evaluation':i,'valid':True,'descriptor':descriptor,'score':score,'archive_replaced':accepted})
    if not archive:return None,{'error':'no_valid_evolution_candidate','evaluations':evaluations,'history':history}
    # Seed selects a style bin; no single global best is imposed on runtime samples.
    chosen=rng.choice(sorted(archive));return archive[chosen][1],{'method':'mutation MAP-Elites' if mutation else 'equal-evaluations independent random control','evaluations':evaluations,'valid_evaluations':valid,'archive_cells':len(archive),'chosen_descriptor':chosen,'archive':[{'descriptor':k,'score':v[0],'signature':topology_signature(v[1])} for k,v in sorted(archive.items())],'history':history}

# Spatial layer: mask collisions, directional typed ports, A* routing, bounded placement.
def shifted_cells(template,x,y):return {(x+c[0],y+c[1]) for c in template['footprint']}
def port_candidates(room):
    cells={tuple(c) for c in room['cells']};cx=sum(x for x,y in cells)/len(cells);cy=sum(y for x,y in cells)/len(cells);out=[]
    for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
        boundary=[c for c in cells if (c[0]+dx,c[1]+dy) not in cells]
        boundary.sort(key=lambda c:abs(c[1]-cy) if dx else abs(c[0]-cx))
        for c in boundary:out.append({'cell':list(c),'outside':[c[0]+dx,c[1]+dy],'direction':[dx,dy],'type':room['port_type']})
    return out

def astar(start,end,blocked,bounds,budget=12000):
    if start in blocked or end in blocked:return None,0
    xmin,ymin,xmax,ymax=bounds
    def h(c):return abs(c[0]-end[0])+abs(c[1]-end[1])
    heap=[(h(start),0,start)];cost={start:0};parent={};visits=0
    while heap and visits<budget:
        _,d,c=heapq.heappop(heap);visits+=1
        if d!=cost[c]:continue
        if c==end:
            path=[c]
            while c!=start:c=parent[c];path.append(c)
            return path[::-1],visits
        for dx,dy in [(1,0),(0,1),(-1,0),(0,-1)]:
            n=(c[0]+dx,c[1]+dy)
            if n in blocked or not(xmin<=n[0]<=xmax and ymin<=n[1]<=ymax):continue
            nd=d+1
            if nd<cost.get(n,math.inf):cost[n]=nd;parent[n]=c;heapq.heappush(heap,(nd+h(n),nd,n))
    return None,visits

def route_layout(g,rooms,rng):
    occupied={tuple(c) for r in rooms for c in r['cells']};byid={r['node']:r for r in rooms};ports={k:port_candidates(v) for k,v in byid.items()}
    room_halo=set(occupied)
    for x,y in occupied:
        for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:room_halo.add((x+dx,y+dy))
    xs=[x for x,y in occupied];ys=[y for x,y in occupied];bounds=(min(xs)-18,min(ys)-18,max(xs)+18,max(ys)+18)
    pairs={}
    for e in g['edges']:pairs.setdefault(tuple(sorted([e['from'],e['to']])),[]).append(e['id'])
    def distance(pair):
        a,b=[byid[n] for n in pair];return abs(a['x']-b['x'])+abs(a['y']-b['y'])
    # Route long topology cycles first; alternative ordering is part of bounded search.
    ordered=sorted(pairs,key=lambda p:(distance(p),p),reverse=bool(rng.next_int(2)))
    reserved=set();used_ports=defaultdict(set);routes=[];visits=0
    for a,b in ordered:
        options=[]
        for pa in ports[a]:
            if tuple(pa['outside']) in used_ports[a]:continue
            for pb in ports[b]:
                if tuple(pb['outside']) in used_ports[b] or pa['type']!=pb['type']:continue
                s,t=tuple(pa['outside']),tuple(pb['outside']);options.append((abs(s[0]-t[0])+abs(s[1]-t[1]),pa,pb))
        options.sort(key=lambda z:z[0]);chosen=None
        for _,pa,pb in options[:48]:
            # One-cell separation prevents accidental connections between unrelated corridors.
            blocked=(room_halo-{tuple(pa['outside']),tuple(pb['outside'])})|reserved
            path,v=astar(tuple(pa['outside']),tuple(pb['outside']),blocked,bounds);visits+=v
            if path:
                chosen=(pa,pb,path);break
        if chosen is None:return None,{'reason':'corridor_route_unsatisfied','pair':[a,b],'astar_visits':visits,'routed_pairs':len(routes)}
        pa,pb,path=chosen
        # A corridor may approach its own endpoints but no other corridor may touch it.
        for c in path:
            reserved.add(c)
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:reserved.add((c[0]+dx,c[1]+dy))
        used_ports[a].add(tuple(pa['outside']));used_ports[b].add(tuple(pb['outside']))
        routes.append({'from':a,'to':b,'edges':pairs[(a,b)],'from_port':pa,'to_port':pb,'points':[list(c) for c in [tuple(pa['cell'])]+path+[tuple(pb['cell'])]],'physical_status':'unverified abstract corridor'})
    return routes,{'astar_visits':visits}

def validate_layout(g,layout):
    """Independent final abstract geometry check, never a physics certification."""
    if not layout.get('ok'):return ['layout_not_complete']
    errors=[];room_by_id={r['node']:r for r in layout['rooms']};owner={}
    edge_by_id={e['id']:e for e in g['edges']}
    if set(room_by_id)!={n['id'] for n in g['nodes']}:errors.append('missing_or_extra_rooms')
    for r in layout['rooms']:
        for c in map(tuple,r['cells']):
            if c in owner:errors.append('overlapping_room_masks')
            owner[c]=r['node']
    paths={};covered=[]
    for i,route in enumerate(layout['corridors']):
        points=list(map(tuple,route['points']));a=route['from'];b=route['to'];pa=route['from_port'];pb=route['to_port']
        covered.extend(route['edges'])
        for edge_id in route['edges']:
            edge=edge_by_id.get(edge_id)
            if edge is None or {edge['from'],edge['to']}!={a,b}:errors.append('edge_endpoint_mismatch')
        if pa['type']!=pb['type']:errors.append('port_type_mismatch')
        if not points or points[0]!=tuple(pa['cell']) or points[-1]!=tuple(pb['cell']):errors.append('port_endpoint_mismatch');continue
        if len(points)<3 or points[1]!=tuple(pa['outside']) or points[-2]!=tuple(pb['outside']):errors.append('port_path_mismatch')
        for port in [pa,pb]:
            direction=port.get('direction')
            if direction not in [[1,0],[-1,0],[0,1],[0,-1]]:errors.append('invalid_port_direction');continue
            if port['outside']!=[port['cell'][0]+direction[0],port['cell'][1]+direction[1]]:errors.append('port_direction_mismatch')
        if owner.get(points[0])!=a or owner.get(points[-1])!=b:errors.append('port_owner_mismatch')
        for u,v in zip(points,points[1:]):
            if abs(u[0]-v[0])+abs(u[1]-v[1])!=1:errors.append('noncontiguous_corridor')
        interior=points[1:-1]
        explicit=defaultdict(set)
        explicit[tuple(pa['outside'])].add(a);explicit[tuple(pb['outside'])].add(b)
        for c in interior:
            if c in owner:errors.append('corridor_crosses_room')
            for dx,dy in [(1,0),(-1,0),(0,1),(0,-1)]:
                neighbor=(c[0]+dx,c[1]+dy)
                if neighbor in owner and owner[neighbor] not in explicit.get(c,set()):errors.append('undeclared_room_contact')
                if neighbor in paths and paths[neighbor]!=i:errors.append('undeclared_corridor_contact')
            if c in paths:errors.append('overlapping_corridors')
            paths[c]=i
    if Counter(covered)!=Counter(e['id'] for e in g['edges']):errors.append('missing_or_duplicate_edge_realization')
    return sorted(set(errors))

def strict_catalog_feasibility(g,catalog):
    """Reject invented multi-port hubs when inventory supplies only canonical ports.

    This is a necessary static count/type check, not sufficient physical admission.
    An external template must explicitly list distinct ports; no four-door default.
    """
    adjacency=defaultdict(set)
    for e in g['edges']:
        adjacency[e['from']].add(e['to']);adjacency[e['to']].add(e['from'])
    errors=[];assignments={}
    for n in g['nodes']:
        eligible=[]
        for t in catalog.get('templates',[]):
            if n['role'] not in t.get('roles',[]):continue
            ports=t.get('ports',[])
            if len({p.get('id') for p in ports})<len(adjacency[n['id']]):continue
            if any(p.get('type') not in ['grounded'] for p in ports):continue
            eligible.append(t['id'])
        assignments[n['id']]=eligible
        if not eligible:errors.append({'node':n['id'],'required_distinct_connections':len(adjacency[n['id']]),'reason':'no_explicit_typed_port_capacity'})
    return {'ok':not errors,'errors':errors,'eligible_templates':assignments,'scope':'necessary static count/type feasibility only; no physics or geometry certificate'}

def embed(g,seed,catalog,region,attempts=8):
    rng=RandomStream(seed,'layout');templates=catalog['templates'];nodes=g['nodes'];placement_trials=0;failures=[];route_backjumps=[];route_checks=0
    node_index={n['id']:i for i,n in enumerate(nodes)}
    # Routing conflicts backjump to the later endpoint, so module placement receives
    # feedback from cyclic corridor closure. Global attempts remain strictly bounded.
    for attempt in range(attempts):
        occupied=set();rooms=[];backtracks=0;conflict_index=len(nodes);solved_routes=None;solved_detail=None;attempt_checks=0
        def place(index):
            nonlocal placement_trials,backtracks,conflict_index,solved_routes,solved_detail,attempt_checks,route_checks
            if index==len(nodes):
                if attempt_checks>=6:conflict_index=-1;return False
                attempt_checks+=1;route_checks+=1
                corridors,detail=route_layout(g,rooms,rng)
                if corridors is not None:
                    candidate={'ok':True,'rooms':rooms,'corridors':corridors}
                    final_errors=validate_layout(g,candidate)
                    if not final_errors:solved_routes=corridors;solved_detail=detail;return True
                    detail={'reason':'final_geometry_validation_failed','errors':final_errors}
                pair=detail.get('pair',[]);conflict_index=max((node_index[n] for n in pair),default=len(nodes)-1)
                route_backjumps.append({'attempt':attempt,'route_check':route_checks,'backjump_to':nodes[conflict_index]['id'],'conflict':detail})
                failures.append({'attempt':attempt,**detail});return False
            n=nodes[index];eligible=[t for t in templates if n['role'] in t['roles'] and set(t.get('requirements',[]))<=set(g['initial_abilities'])]
            if not eligible:return False
            ix,iy=n['ideal'];candidates=[]
            for t in rng.shuffle(eligible):
                for dx,dy in rng.shuffle([(0,0),(2,0),(-2,0),(0,2),(0,-2),(3,3),(-3,-3)]):
                    x,y=ix+dx,iy+dy
                    if region=='forest':x,y=round(ix*0.8)+dx,round(iy*1.4)+dy
                    cells=shifted_cells(t,x,y);padded=set(cells)
                    for xx,yy in cells:
                        for ax,ay in [(1,0),(-1,0),(0,1),(0,-1)]:padded.add((xx+ax,yy+ay))
                    if occupied&padded:continue
                    candidates.append((t,x,y,cells))
            for t,x,y,cells in candidates[:12]:
                placement_trials+=1
                if placement_trials>4000:return False
                rooms.append({'node':n['id'],'template':t['id'],'x':x,'y':y,'cells':[list(c) for c in sorted(cells)],'footprint':t['footprint'],'port_type':t['port_type'],'physics':'unverified'})
                occupied.update(cells)
                if place(index+1):return True
                occupied.difference_update(cells);rooms.pop();backtracks+=1
                if conflict_index<index:return False
                conflict_index=len(nodes)
            return False
        if not place(0):
            failures.append({'attempt':attempt,'reason':'placement_or_route_budget_unsatisfied'});continue
        xs=[c[0] for r in rooms for c in r['cells']];ys=[c[1] for r in rooms for c in r['cells']]
        return {'ok':True,'rooms':rooms,'corridors':solved_routes,'bounds':[min(xs),min(ys),max(xs)+1,max(ys)+1],'attempt':attempt,'placement_trials':placement_trials,'backtracks':backtracks,'route_checks':route_checks,'route_backjumps':route_backjumps,'attempt_failures':failures,'status':'abstract_mask_and_corridor_embedding','physics':'unverified','astar_visits':solved_detail['astar_visits']}
    return {'ok':False,'rooms':rooms,'corridors':[],'attempt_failures':failures,'placement_trials':placement_trials,'route_checks':route_checks,'route_backjumps':route_backjumps,'reason':'embedding_budget_exhausted','physics':'unverified'}

def generate(algorithm,seed,region,catalog=None,search_budget=24,embedding_attempts=8):
    if region not in PROFILES:raise ValueError('unknown_region')
    if algorithm not in ['A','B','C','C_random']:raise ValueError('unknown_algorithm')
    catalog=catalog or default_catalog();start=time.perf_counter();base=mission(str(seed),region)
    mission_graph={'entry':'m0','goal':'m5','objectives':[{'id':n['id'],'role':n['role'],'reward':n['reward'],'requires_before':['m4'] if n['role']=='boss' else []} for n in base['nodes'] if n['role'] not in ['challenge']],'dependency_edges':[{'from':'m4','to':'m5','type':'boss_access'}],'rewrite_log':base['rewrite_log']}
    if algorithm=='A':g,search=grammar_a(base,seed)
    elif algorithm=='B':g,search=asp_b(base,seed)
    else:g,search=evolve_c(base,seed,search_budget,algorithm=='C')
    manifest={'schema':'mapgen-experiment/v1','id':f'{region}-{algorithm}-{seed}','version':VERSION,'seed':str(seed),'algorithm':algorithm,'region':region,'profile':PROFILES[region], 'catalog_digest':digest(catalog),'catalog_provenance':catalog['provenance'],'mission_graph':mission_graph,'search':search,'failures':[],'physics':{'status':'unverified','reason':'abstract footprints/corridors have no PlayerMotor assembly or traces'},'subjective':{'status':'unverified'},'runtime_admitted':False,'content_kind':'synthetic_spatial_proxy' if catalog.get('kind')=='synthetic_fixed_catalog' else catalog.get('kind','external_catalog'),'not_comparable_to_full_gameplay':True}
    if g is None:manifest.update(exploration_graph=None,layout={'ok':False,'reason':'topology_generation_failed'},metrics={});manifest['failures'].append(search.get('error','topology_generation_failed'))
    else:
        errors,proof=validate_graph(g);manifest['exploration_graph']=g;manifest['logic_validation']={'ok':not errors,**proof};manifest['failures'].extend(errors)
        manifest['metrics']=graph_metrics(g) if not errors else {}
        layout=embed(g,seed,catalog,region,embedding_attempts) if not errors else {'ok':False,'reason':'invalid_logic'};manifest['layout']=layout
        if layout['ok']:
            geometric_errors=validate_layout(g,layout);layout['validation']={'ok':not geometric_errors,'errors':geometric_errors}
            if geometric_errors:layout['ok']=False;layout['reason']='final_geometry_validation_failed';manifest['failures'].extend(geometric_errors)
        if not layout['ok']:manifest['failures'].append(layout['reason'])
    manifest['performance']={'generation_ms':round((time.perf_counter()-start)*1000,3),'python':platform.python_version(),'clingo':clingo.__version__ if clingo else None,'timing_scope':'topology+validation+optimization+embedding; no engine'}
    manifest['deterministic_digest']=digest({k:v for k,v in manifest.items() if k not in ['performance'] and k!='search'} | {'search':{k:v for k,v in search.items() if k!='solve_ms'}})
    return manifest

def deep_size(value,seen=None):
    seen=set() if seen is None else seen
    if id(value) in seen:return 0
    seen.add(id(value));size=sys.getsizeof(value)
    if isinstance(value,dict):size+=sum(deep_size(k,seen)+deep_size(v,seen) for k,v in value.items())
    elif isinstance(value,(list,tuple,set,frozenset)):size+=sum(deep_size(v,seen) for v in value)
    return size

def benchmark(seeds,out,catalog=None,algorithms=('A','B','C','C_random'),search_budget=24,embedding_attempts=8):
    out=Path(out);out.mkdir(parents=True,exist_ok=True);(out/'manifests').mkdir(exist_ok=True);rows=[]
    for region in PROFILES:
        for seed in range(seeds):
            for algorithm in algorithms:
                m=generate(algorithm,str(seed),region,catalog,search_budget,embedding_attempts);peak=deep_size(m)
                m['performance']['retained_manifest_python_bytes']=peak
                m['performance']['memory_scope']='deep sys.getsizeof of retained manifest; transient/native peak not measured'
                (out/'manifests'/f'{region}-{algorithm}-{seed}.json').write_text(json.dumps(m,ensure_ascii=False,indent=2))
                metric=m['metrics'];row={'region':region,'algorithm':algorithm,'seed':seed,'logic_ok':m.get('logic_validation',{}).get('ok',False),'layout_ok':m['layout']['ok'],'physics':'unverified','generation_ms':m['performance']['generation_ms'],'retained_manifest_python_bytes':peak,'main_cost':metric.get('main_completion_cost'),'branch_depths':canonical(metric.get('branch_depths',[])),'effective_shortcuts':metric.get('effective_shortcuts'),'cycle_rank':metric.get('cycle_rank_undirected'),'route_choices':metric.get('route_choices_bounded'),'heuristic':metric.get('quality_heuristic'),'topology_signature':metric.get('topology_wl_signature'),'experience_signature':metric.get('experience_wl_signature'),'failures':canonical(m['failures'])};rows.append(row)
                print(f'{region} {algorithm} seed={seed} logic={row["logic_ok"]} layout={row["layout_ok"]} ms={row["generation_ms"]}',flush=True)
    with (out/'results.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summaries=[]
    for region in PROFILES:
        for alg in algorithms:
            rr=[r for r in rows if r['region']==region and r['algorithm']==alg];times=sorted(r['generation_ms'] for r in rr);valid=[r for r in rr if r['logic_ok']]
            summaries.append({'region':region,'algorithm':alg,'samples':len(rr),'logic_passes':sum(r['logic_ok'] for r in rr),'layout_passes':sum(r['layout_ok'] for r in rr),'physics_passes':None,'physics_status':'unverified','median_ms':times[len(times)//2],'p95_ms':times[min(len(times)-1,math.ceil(len(times)*.95)-1)],'max_retained_manifest_python_bytes':max(r['retained_manifest_python_bytes'] for r in rr),'unique_topology_wl_fingerprints':len({r['topology_signature'] for r in valid}),'unique_experience_wl_fingerprints':len({r['experience_signature'] for r in valid}),'mean_heuristic':round(sum(r['heuristic'] for r in valid)/len(valid),4) if valid else None})
    summary={'schema':'mapgen-benchmark/v1','version':VERSION,'seed_range':[0,seeds-1],'catalog_digest':digest(catalog or default_catalog()),'environment':{'python':platform.python_version(),'platform':platform.platform(),'clingo':clingo.__version__ if clingo else None},'summaries':summaries,'limitations':['Synthetic fixed abstract templates unless catalog supplied','No PlayerMotor physics evidence','Memory is retained manifest deep sys.getsizeof; transient/native peak and engine memory are not measured','WL fingerprints are invariants, not exact non-isomorphism certificates','A/B/C graph policies differ; heuristic is uncalibrated and not human fun','C_random uses the same topology evaluation count as C, not equal wall-clock time']}
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2))
    runs=[json.loads(p.read_text()) for p in sorted((out/'manifests').glob('*.json'))]
    (out/'runs.json').write_text(json.dumps({'schema':'mapgen-runs/v1','summary':summary,'runs':runs},ensure_ascii=False,separators=(',',':')))
    return summary

def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    q=sub.add_parser('generate');q.add_argument('--algorithm',choices=['A','B','C','C_random'],default='A');q.add_argument('--seed',default='0');q.add_argument('--region',choices=list(PROFILES),default='plains');q.add_argument('--out',required=True)
    b=sub.add_parser('benchmark');b.add_argument('--seeds',type=int,default=30);b.add_argument('--out',required=True);b.add_argument('--algorithms',nargs='+',default=['A','B','C','C_random'])
    for s in [q,b]:s.add_argument('--catalog');s.add_argument('--search-budget',type=int,default=24);s.add_argument('--embedding-attempts',type=int,default=8)
    a=p.parse_args();catalog=json.loads(Path(a.catalog).read_text()) if a.catalog else None
    if a.command=='generate':
        m=generate(a.algorithm,a.seed,a.region,catalog,a.search_budget,a.embedding_attempts);Path(a.out).parent.mkdir(parents=True,exist_ok=True);Path(a.out).write_text(json.dumps(m,ensure_ascii=False,indent=2));print(json.dumps({'id':m['id'],'logic':m.get('logic_validation'),'layout_ok':m['layout']['ok'],'failures':m['failures'],'ms':m['performance']['generation_ms']}))
        return 0 if not m['failures'] else 1
    summary=benchmark(a.seeds,a.out,catalog,tuple(a.algorithms),a.search_budget,a.embedding_attempts);print(json.dumps(summary,ensure_ascii=False,indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
