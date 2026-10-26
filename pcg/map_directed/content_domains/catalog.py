"""No family whitelist: inspect every version, world, capability and directed pair."""
import copy,json,math
from pathlib import Path
from ..catalog_feed.catalog import load as load_current
from ..director import REPO
from ..run import write
from pcg.prototype.factory.core.quality import digest

WORLD=['platforms','one_way_platform_indices','wall_platform_indices','hazards','thorns','saws','moving_platforms','latches','enemies','hooks','reward_sites']
def features(case):
    ops=case.get('control_plan',[]);names={c['op']for c in ops};cells={c.get('aim_cell',{}).get('kind')for c in ops};tags=set()
    if 'jump'in names and 'shoot'in names:tags.add('air_shot')
    if case.get('thorns')or case.get('saws')or case.get('hazards'):tags.add('hazard_precision')
    if 'bell'in cells:tags.add('shot_trigger')
    if case.get('moving_platforms'):tags.add('moving_target')
    if case.get('enemies'):tags.add('enemy_interaction')
    dy=case['exit_port'][1]-case['entry_port'][1]
    if dy>=96:tags.add('descent')
    if dy<=-96:tags.add('ascent')
    if 'shoot'in names and dy>=96 and any(c['op']=='axis'and c.get('value',0)<0 for c in ops):tags.add('air_brake')
    return sorted(tags)

def describe(item):
    gc=item['document']['generationContract'];ports={p['id']:dict(id=p['id'],position=p['position'][:],normal=p['normal'][:])for p in gc['ports']};relations=[]
    for case in item['cases']:
        r=case.get('route_spec',{});a,b=r.get('from_port'),r.get('to_port')
        if a is None:
            a=next((k for k,p in ports.items()if p['position']==case['entry_port']),None);b=next((k for k,p in ports.items()if p['position']==case['exit_port']),None)
        if a not in ports or b not in ports:raise ValueError('source_direction_binding_missing/'+case['id'])
        relations.append(dict(**{'from':a,'to':b},case_id=case['id'],features=features(case),role=r.get('role','traversal'),capabilities=case['capabilities'][:],world_sha256=digest({k:case.get(k,[])for k in WORLD}),evidence_scope='Existing finite policy only; new geometry/Map requires fresh physics'))
    common=len({r['world_sha256']for r in relations})==1
    return dict(version=item['record']['contentVersion'],title=item['title'],family=item['row']['family'],kind=gc['kind'],ports=ports,
        relations=relations,unknown_pairs=[dict(**{'from':a,'to':b},status='UNKNOWN')for a in ports for b in ports if a!=b and not any(r['from']==a and r['to']==b for r in relations)],
        shared_world=common,withdrawn=item['withdrawn'],record=item['row']['record'],features=sorted({t for r in relations for t in r['features']}))

def match(description,demand):
    reasons=[]
    if description['withdrawn']:reasons.append('content_withdrawn')
    if not description['shared_world']:reasons.append('multi_route_worlds_differ')
    n=len(description['ports']);lo,hi=demand.get('port_count',[1,32])
    if not lo<=n<=hi:reasons.append('port_count')
    pairs=[]
    for r in description['relations']:
        missing=set(r['capabilities'])-set(demand['capabilities'])
        if missing:continue
        if not set(demand.get('all_features',[]))<=set(r['features']):continue
        if demand.get('any_features')and not set(demand['any_features'])&set(r['features']):continue
        a,b=description['ports'][r['from']],description['ports'][r['to']];dx=b['position'][0]-a['position'][0];dy=b['position'][1]-a['position'][1]
        if abs(dx)>demand.get('max_span_x',4096)or abs(dy)>demand.get('max_span_y',2048):continue
        pairs.append(r)
    if not pairs:reasons.append('no_declared_direction_satisfies_gameplay_capability_space')
    if demand.get('choice'):
        by={p:len({r['to']for r in pairs if r['from']==p and r['from']!=r['to']})for p in description['ports']}
        if not any(v>=2 for v in by.values()):reasons.append('no_shared_ingress_choice')
    if demand.get('return')and not any(any(q['from']==r['to']and q['to']==r['from']for q in pairs)for r in pairs):reasons.append('no_declared_reverse_relation')
    return dict(status='matching_source_requires_adaptation'if not reasons else'not_matched',reasons=reasons,pairs=pairs if not reasons else[])

def demands():
    caps=['move','jump','shot_recoil']
    return [dict(id=k,capabilities=caps,port_count=count,all_features=allf,any_features=anyf,**kw)for k,count,allf,anyf,kw in [
        ('precision_air',[2,8],['air_shot','hazard_precision'],[],{}),('trigger_cross',[2,8],['shot_trigger'],[],{}),
        ('fall_brake',[2,8],['air_brake'],[],{}),('elevation_transfer',[2,8],['air_shot'],['ascent','descent'],{}),
        ('shared_choice',[3,8],[],[],dict(choice=True)),('return_route',[2,8],[],[],dict(**{'return':True})),
        ('moving_interaction',[2,8],['air_shot','moving_target'],[],{}),('combat_air',[2,8],['air_shot','enemy_interaction'],[],{})]]

def scan(out):
    out=Path(out);out.mkdir(exist_ok=False,parents=True);items=load_current();descriptions=[describe(x)for x in items];queries=demands();rows=[]
    for d in descriptions:rows.append(dict(source=d,queries={q['id']:match(d,q)for q in queries}))
    write(out/'source-catalog.json',descriptions);write(out/'demands.json',queries);write(out/'match-audit.json',rows)
    write(out/'summary.json',dict(versions_scanned=len(items),families=len({d['family']for d in descriptions}),multiport_versions=sum(len(d['ports'])>2 for d in descriptions),nonlevel_versions=sum(any(d['ports'][r['from']]['position'][1]!=d['ports'][r['to']]['position'][1]for r in d['relations'])for d in descriptions),matches={q['id']:sum(v['queries'][q['id']]['status']=='matching_source_requires_adaptation'for v in rows)for q in queries},general_admission=False))
    return items,descriptions
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();scan(a.out)
