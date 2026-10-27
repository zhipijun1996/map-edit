"""Arc consistency for finite Port displacement/normal triangles.

This rejects algebraically impossible cycles before geometric backtracking.
No edge or node is removed; missing shapes remain explicit content demands.
"""

def mode(p):return tuple(p['normal'])+(p.get('grid',{}).get('profile','legacy'),)+tuple(p.get('crossing_offset',[0,0]))
def opposite(value):return (-value[0],-value[1],*value[2:])
def signature(m,enter,leave):
    a,b=m['ports'][enter],m['ports'][leave]
    return mode(a),mode(b),b['position'][0]-a['position'][0],b['position'][1]-a['position'][1]


def prune(graph,domains):
    adjacency={n['id']:set()for n in graph['nodes']};edges={}
    for e in graph['edges']:
        a,b=e['from'],e['to'];adjacency[a].add(b);adjacency[b].add(a);edges[frozenset([a,b])]=e['id']
    triangles=[(a,b,c)for a in sorted(adjacency)for b in sorted(adjacency[a])if b>a for c in sorted(adjacency[a]&adjacency[b])if c>b]
    result={k:list(v)for k,v in domains.items()};audit=[];changed=True
    while changed:
        changed=False
        for a,b,c in triangles:
            ab,bc,ca=[edges[frozenset(pair)]for pair in [(a,b),(b,c),(c,a)]];pairs=[(ca,ab),(ab,bc),(bc,ca)];keys=[a,b,c]
            sets=[{signature(m,*p)for m in result[k]}for k,p in zip(keys,pairs)];supported=[set(),set(),set()]
            for ai,ao,ax,ay in sets[0]:
                for bi,bo,bx,by in sets[1]:
                    if opposite(ao)!=bi:continue
                    required=(opposite(bo),opposite(ai),-ax-bx,-ay-by)
                    if required in sets[2]:supported[0].add((ai,ao,ax,ay));supported[1].add((bi,bo,bx,by));supported[2].add(required)
            for k,p,allowed in zip(keys,pairs,supported):
                old=len(result[k]);result[k]=[m for m in result[k]if signature(m,*p)in allowed]
                if len(result[k])!=old:
                    changed=True;audit.append(dict(node=k,cycle=keys,before=old,after=len(result[k]),reason='No compatible normal/profile and zero-sum integer Port displacement in this triangle'))
            if any(not result[k]for k in keys):return result,audit
    return result,audit
