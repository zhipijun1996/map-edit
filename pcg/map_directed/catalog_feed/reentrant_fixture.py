"""Bounded physical integration fixture, not a replacement regional generator.

Six new four-direction rock-well prototypes and six original action Modules
exercise two actual cross-level loops. All geometry is Module-owned. The
existing shape CSP, canonical exporter, assembler and R2 state planner remain
the consumers. Full regional R2 demands remain separately unresolved.
"""
import copy,gzip,itertools,json,random
from pathlib import Path
from .adapt import exterior,apply_reward_request
from .catalog import load
from .build import rename
from .design_review import graph_review,reward_requests,review
from ..director import REPO
from ..run import write
from ..shape_search.search import search,closed_solids
from ..shape_search.catalog import reflect
from ..direct_join.canonical import export_reload
from ..direct_join.assemble import assemble_modules
from ..direct_join.audit import audit
from ..r2_full.orchestrate import logical_route,edge_cover_route
from ..region_scale.materialize import case_for
from pcg.prototype.plains.spatial_interchange import generate,cases_for as hub_cases
from pcg.prototype.factory.core.quality import digest

def mirrored(m):
    original=copy.deepcopy(m['case']);m=reflect(m);c=m['case'];W=m['spec']['space']['core_bounds'][2]
    def rect(r):return [W-r[0]-r[2],r[1],r[2],r[3]]
    for t in c.get('thorns',[]):
        host=original['platforms'][t['platform_index']]
        if t['face']in ['top','bottom']:t['start_offset']=host[2]-t['start_offset']-t['length']
        else:t['face']={'left':'right','right':'left'}[t['face']]
    for p in c['moving_platforms']:
        p['start'][0]=W-p['start'][0];p['finish'][0]=W-p['finish'][0]
    for s in c['reward_sites']:
        s['position'][0]=W-s['position'][0];s['region']=rect(s['region'])
    return m

def hub():
    m=generate('rooted');source=REPO/'pcg/results/spatial-interchange-probe-v10'
    # Corrected default source markers do not change any tested route case.
    if hub_cases(m)!=json.loads((source/'cases.json').read_text())['cases']:raise ValueError('prototype_route_input_drift')
    if json.loads((source/'summary.json').read_text())['passed']!=13:raise ValueError('prototype_directions_not_verified')
    frames=[]
    for b in json.loads((source/'batches.json').read_text()):
        raw=gzip.decompress((source/b['gzip_path']).read_bytes())
        if __import__('hashlib').sha256(raw).hexdigest()!=b['raw_output_sha256']:raise ValueError('prototype_trace_drift')
        for r in json.loads(raw)['results']:frames+=r['frames'][::2]
    m['action_clearance']=[list(v)for v in dict.fromkeys((f['x']-12,f['y']-18,24,36)for f in frames)]
    m['prototype_coverage']=dict(run=str(source.relative_to(REPO)),ordered_pairs=12,continuous_return=True,regular_qualified=False,assembly_unknown=True)
    return m

def candidates():
    rows=[]
    for x in load():
        if not x['row']['selected_for_plains_candidates']or len(x['cases'])!=1:continue
        c=x['cases'][0]
        if c['entry_port'][1]!=c['exit_port'][1]or c.get('expected_reward')is not None:continue
        if x['row']['family']not in ['thorn-slot','timed-cache','moving-ray-window','landing-reload-relay']:continue
        for pad in range(0,49,8):
            try:m=exterior(x,'action',pad)
            except ValueError:continue
            entry=m['center']['position'];end=c['exit_port']
            if abs(entry[0]-m['ports']['in']['dock']['position'][0])>64 or abs(end[0]-m['ports']['out']['dock']['position'][0])>80:continue
            # Exterior walk must not start behind the original closed gate.
            L=m['ports']['in']['dock']['position'][0]
            if any(not l.get('ferry_id')and l['gate'][0]<entry[0]+12 and l['gate'][0]+l['gate'][2]>L-12 and l['gate'][1]<entry[1]+18 and l['gate'][1]+l['gate'][3]>entry[1]-18 for l in c['latches']):continue
            for i in set(m['center']['support_indices'])|set(m['ports']['out']['dock']['support_indices']):m['case']['platforms'][i][3]=min(m['case']['platforms'][i][3],64)
            m['adaptation'].update(exterior_padding=pad,shore_underside_maximum=64)
            m['selection_family']=x['row']['family'];rows.append(m)
    return rows

def build(out,seed):
    rng=random.Random(seed);pool=candidates();pairs={}
    levels=3+int(digest(seed)[0],16)%2
    for a,b in itertools.product(pool,pool):
        if a['selection_family']==b['selection_family']:continue
        width=sum(m['ports']['out']['position'][0]-m['ports']['in']['position'][0]for m in [a,b])
        pairs.setdefault(width,[]).append((a,b))
    choices=[]
    for width,options in sorted(pairs.items()):
        plain=[p for p in options if not any(m['case']['moving_platforms']for m in p)]
        moving=[p for p in options if any(m['case']['moving_platforms']for m in p)]
        if not plain or not moving:continue
        rng.shuffle(plain);rng.shuffle(moving)
        groups=None
        for upper,middle,lower in itertools.product(plain,plain,moving):
            versions={m['source_version']for p in [upper,middle,lower]for m in p}
            families={m['selection_family']for p in [upper,middle,lower]for m in p}
            if len(versions)>=4 and len(families)>=3:groups=(upper,middle,lower);break
        if groups:choices.append((width,groups))
        if len(choices)==3:break
    if not choices:raise ValueError('no_small_shore_three_row_assignment')
    attempts=[]
    for width,groups in choices:
        h=hub();nodes=[];edges=[];domains={};maps={};directions={};branches=[]
        row_groups=list(groups)if levels==3 else [groups[0],groups[1],groups[0],groups[2]]
        for row in range(levels):
            for side in ['L','R']:
                key=f'{side}{row}';m=copy.deepcopy(h);m['id']=key;m['spec']['node_id']=key;m['spec']['node']['id']=key;m['spec']['id']='reentrant-core/'+key;m['variant_id']=key+'/rock-well'
                domains[key]=[m];maps[key]={};directions[key]=dict(W='in',E='out')
                nodes.append(dict(id=key,role='hub',label='岩井换向 '+key,ideal=[400+(800+width if side=='R'else 0),642+row*480],grants=[],opens=[],reward=0,risk=1))
        def edge(a,b,pa,pb,bidirectional=False):
            key='e'+str(len(edges));edges.append(dict(id=key,**{'from':a,'to':b},bidirectional=bidirectional,requires=[],switch=None,cost=1,purpose='regional_route'));maps[a][pa]=key;maps[b][pb]=key
        for row in range(levels-1):
            for side in ['L','R']:edge(f'{side}{row}',f'{side}{row+1}','S','N',True)
        for row,pair in enumerate(row_groups):
            left,right=(f'L{row}',f'R{row}')if row%2==0 else(f'R{row}',f'L{row}')
            chain=[left,f'C{row}a',f'C{row}b',right]
            for i,raw in enumerate(pair):
                key=chain[i+1];m=copy.deepcopy(raw);m['id']=key;m['spec']['node_id']=key;m['spec']['node']['id']=key;m['spec']['id']='reentrant-core/'+key;m['variant_id']=key+'/'+m['variant_id'];maps[key]={}
                if row%2:m=mirrored(m)
                domains[key]=[m]
                # Actual conceptual positions are only for intent diagnostics;
                # the shape CSP does not consume these pose hints.
                if row%2==0:x=800+(0 if i==0 else pair[0]['ports']['out']['position'][0]-pair[0]['ports']['in']['position'][0])+m['center']['position'][0]-m['ports']['in']['position'][0]
                else:x=800+width-(0 if i==0 else pair[0]['ports']['out']['position'][0]-pair[0]['ports']['in']['position'][0])+m['center']['position'][0]-m['ports']['in']['position'][0]
                reward=18 if key=='C1b' else 30 if key==f'C{levels-1}b' else 0
                nodes.append(dict(id=key,role='reward'if reward else'challenge',label=m['source_title'],ideal=[x,402+row*480],grants=[],opens=[],reward=reward,risk=2 if reward else 1))
            edge(chain[0],chain[1],'E'if row%2==0 else'W','in');edge(chain[1],chain[2],'out','in');edge(chain[2],chain[3],'out','W'if row%2==0 else'E')
        graph=dict(schema='map-notes/exploration-graph/v1',region='plains',seed=seed,entry='L1',goal='R0',initial_abilities=['move','jump','shot_recoil'],nodes=nodes,edges=edges,core_nodes=[n['id']for n in nodes],branches=[],landmarks=['L0','L1','R2'],mission_policy=dict(boss_forecourt='R0',goal_kind='exit_landmark_no_boss_encounter'),
            reward_routes=[dict(id='middle-excursion',entry='R1',rejoin='L1',reward='C1b',nodes=['C1a','C1b'],return_mode='existing_core_loop'),dict(id='lower-excursion',entry=f'L{levels-1}'if levels%2 else f'R{levels-1}',rejoin=f'R{levels-1}'if levels%2 else f'L{levels-1}',reward=f'C{levels-1}b',nodes=[f'C{levels-1}a',f'C{levels-1}b'],return_mode='existing_core_loop')],source='Bounded alternating rock-well contact grammar: 3 or 4 crossings; not unrestricted regional topology generation')
        allocation=reward_requests(graph)
        if not allocation['ok']:raise ValueError(allocation['errors'])
        for key,vs in domains.items():domains[key]=[rename(apply_reward_request(m,allocation['requests'][key]),maps[key])for m in vs]
        result=search(graph,domains,seed,budget=50000);ms=result.pop('modules',[]);attempts.append(result);write(out/'search-attempts.json',attempts)
        if not ms:continue
        write(out/'precanonical.json',dict(graph=graph,modules=ms))
        ms=export_reload(ms,out/'module-library',producer='pcg/map_directed/catalog_feed/reentrant_fixture.py')
        c=assemble_modules(graph,ms,[dict(id=e['id'],kind=next(m for m in ms if m['id']==e['from'])['ports'][e['id']]['kind'])for e in edges]);c.update(shop={},unresolved_rewards=[]);c['source']['graph_source']=graph['source']
        write(out/'compiled.json',c);write(out/'assembly-audit.json',audit(c));intent=review(c);write(out/'design-review.json',intent)
        if not intent['ok']:raise ValueError(intent['errors'])
        return c
    raise ValueError('bounded_reentrant_shape_search_unsatisfied')

def prepare_cases(c,protect_approach=False):
    lower=c['exploration_graph']['reward_routes'][-1];last=lower['reward']
    requests=[('main',logical_route(c,[c['exploration_graph']['goal']]),[]),('middle-reward-return',logical_route(c,['C1b','L1','L0','R0']),['C1b']),('lower-reward-return',logical_route(c,[last,lower['rejoin'],'L1','R0']),[last]),('all-declared-directions',edge_cover_route(c),['C1b',last])]
    cases=[]
    for name,path,rewards in requests:
        v=case_for(c,path,name);ids=[s['id']for s in c['case']['reward_sites']if s['id'].split('/')[0]in rewards]
        v.update(title='风铃平原 · 岩井区域核心 · '+name,extra_script=str(Path(__file__).with_name('reentrant_extra.gd')),required_reward_ids=ids,reward_claim_limit=0 if name=='main' else 2,maximum_coins=48,map_seed=c['exploration_graph']['seed'])
        for leg in v['pilot_program']:
            if leg['kind']=='module':leg['entry']=dict(grounded=True,required_air_shots=1,maximum_shot_cooldown=0)
        # A vertical ray shutter can sweep its own entrance. Grounded contact
        # alone is insufficient: wait on the PREVIOUS Module's safe dock for
        # its original source window, then cross in the same running world.
        from ..shape_search.search import intersects,sweeps,translated
        program=[];guards=[];by={m['id']:m for m in c['modules']}
        for leg in v['pilot_program']:
            if str(leg['target']['id']).startswith('seam/'):
                eid=leg['edge_id'];fr,to=leg['edge_from'],leg['edge_to'];m=by[to];port=c['nodes'][to]['ports'][eid]['target'];x,y=port['position']
                for mover in m['case']['moving_platforms']:
                    envelope=sweeps(dict(case=dict(saws=[],moving_platforms=[mover])))[0]
                    check=[x-12,y-18,24,36]
                    if protect_approach:
                        plane=c['nodes'][to]['ports'][eid]['position'];center=c['nodes'][to]['center']['position'];a,b=min(x,plane[0],center[0]),max(x,plane[0],center[0]);check=[a-12,y-18,b-a+24,36]
                    if not intersects(check,translated(envelope,m['spec']['placement'])):continue
                    safe=copy.deepcopy(c['nodes'][fr]['ports'][eid]['target']);pid=to+'/'+mover['platform_id']
                    guard=dict(id=leg['id']+'-dynamic-seam-guard',kind='module',target=safe,edge_id=eid,edge_from=fr,edge_to=to,edge_terminal=False,budget_ticks=300,
                        control_plan=[dict(op='axis',value=0,trigger=dict(after=0)),dict(op='wait',trigger=dict(dynamic=dict(kind='platform_phase',id=pid,window=[.78,.805]),timeout=240)),dict(op='settle',target_x=safe['position'][0],deadband=4,trigger=dict(after=0))])
                    program.append(guard);guards.append(dict(edge=eid,platform=pid,wait_on_previous_module=fr,window=[.78,.805],scope='Case-scoped dynamic entrance; no arbitrary-phase port admission'))
            program.append(leg)
        v['pilot_program']=program;v['seam_phase_guards']=guards
        cases.append(v)
    return cases
