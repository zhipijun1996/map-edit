"""Measured diagnostics and navigable diagrams, never a human fun score."""
import argparse,gzip,html,json,statistics
from pathlib import Path
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha

def inspect(run):
    run=Path(run);c=json.loads((run/'compiled.json').read_text());g=c['exploration_graph'];cs=json.loads((run/'cases.json').read_text())['cases'];cases={v['id']:v for v in cs};rows=[];covered=set();traces={}
    for batch in json.loads((run/'physics/batches.json').read_text()):
        packed=run/'physics'/batch['gzip_path']
        if file_sha(packed)!=batch['gzip_sha256']:raise ValueError('trace_hash_drift')
        raw=gzip.decompress(packed.read_bytes())
        if __import__('hashlib').sha256(raw).hexdigest()!=batch['raw_output_sha256']:raise ValueError('trace_bytes_drift')
        for r in json.loads(raw)['results']:
            legs=r.get('pilot',{}).get('legs',[]);lookup={v['id']:v for v in cases[r['id']]['pilot_program']}
            for leg in legs:
                q=lookup[leg['id']]
                if leg.get('ok')and q.get('edge_terminal'):covered.add((q['edge_id'],q['edge_from'],q['edge_to']))
            still=maximum=0
            for f in r['frames']:
                still=still+1 if f['grounded']and abs(f['vx'])<1 and abs(f['vy'])<1 else 0;maximum=max(maximum,still)
            trace=[(f['x'],f['y'])for f in r['frames'][::4]];traces[r['id']]=trace
            events=r.get('extra',{}).get('workshop',{}).get('events',[])
            rows.append(dict(id=r['id'],ok=r['ok'],seconds=round(r['ticks']/60,2),shots=r['shots'],
                shots_per_minute=round(r['shots']*3600/max(1,r['ticks']),1),
                walk_policy_fraction=round(sum(v['ticks']for v in legs if v['kind']=='walk')/max(1,r['ticks']),4),
                airborne_frame_fraction=round(sum(not f['grounded']for f in r['frames'])/max(1,len(r['frames'])),4),
                longest_grounded_stationary_seconds=round(maximum/60,2),health=r['hp'],returns=r['returns'],
                coins=r.get('extra',{}).get('workshop',{}).get('coins'),
                accepted_chests=[e['id']for e in events if e['type']=='chest_claim'and e['accepted']]))
    expected={(e['id'],e['from'],e['to'])for e in g['edges']}|{(e['id'],e['to'],e['from'])for e in g['edges']if e['bidirectional']}
    attempts=json.loads((run/'search-attempts.json').read_text())if(run/'search-attempts.json').exists()else[]
    result=dict(seed=g['seed'],run=str(run),modules=len(c['modules']),seams=len(c['seams']),
        cycle_rank=len(g['edges'])-len(g['nodes'])+1,directed_edges_covered=len(covered&expected),directed_edges_expected=len(expected),
        chests=len(c['case']['reward_sites']),currency=sum(v['amount']for v in c['case']['reward_sites']),
        source_versions=len({m['source_version']for m in c['modules']}),
        action_families=sorted({m['selection_family']for m in c['modules']if m.get('selection_family')}),
        world_bounds=c['case']['world_bounds'],map_added_terrain=c['hard_checks']['map_added_platforms'],
        search_expansions=[r['expanded']for r in attempts],search_seconds=round(sum(r['wall_seconds']for r in attempts),4),
        all_passed=all(r['ok']for r in rows),rows=rows,
        scope='Finite concrete whole-map policies; cycle rank is descriptive, not exploration quality',human_fun='awaiting_user_video_observation',production_admitted=False)
    return result,c,traces

def diagram(c,traces,path):
    x,y,w,h=c['case']['world_bounds'];colors=['#22c55e','#f59e0b','#c084fc','#38bdf8'];parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x-50} {y-110} {w+100} {h+180}">',f'<rect x="{x-50}" y="{y-110}" width="{w+100}" height="{h+180}" fill="#101a2b"/>',f'<text x="{x}" y="{y-45}" fill="white" font-size="30">Actual Module geometry and measured continuous routes — {html.escape(c["exploration_graph"]["seed"])}</text>']
    for i,p in enumerate(c['case']['platforms']):
        fill='#547773'if i not in c['case']['one_way_platform_indices']else'#bd9859'
        parts.append(f'<rect x="{p[0]}" y="{p[1]}" width="{p[2]}" height="{p[3]}" fill="{fill}" stroke="#a8c4b4" stroke-width="2"/>')
    for i,(name,points)in enumerate(traces.items()):
        if name not in ['full-region-main','full-region-middle-reward-return','full-region-lower-reward-return']:continue
        points=' '.join(f'{a:.1f},{b:.1f}'for a,b in points)
        parts.append(f'<polyline points="{points}" stroke="{colors[i%4]}" stroke-width="4" opacity=".8" fill="none"><title>{html.escape(name)}</title></polyline>')
    for key,node in c['nodes'].items():
        a,b=node['center']['position'];parts.append(f'<text x="{a+15}" y="{b-28}" fill="white" font-size="23">{html.escape(key)}</text>')
    for site in c['case']['reward_sites']:
        a,b=site['target']['position'];parts.append(f'<circle cx="{a}" cy="{b}" r="16" fill="#ffdf62"><title>{html.escape(site["id"])}</title></circle>')
    parts.append('</svg>');Path(path).write_text('\n'.join(parts))

def run(runs,out):
    out=Path(out)
    if out.exists():raise ValueError('immutable_review_exists')
    out.mkdir(parents=True);results=[]
    for i,folder in enumerate(runs):
        result,c,traces=inspect(folder);results.append(result);diagram(c,traces,out/f'map-{i}-routes.svg')
    write(out/'results.json',dict(schema='pcg/contact-grammar-review/v1',maps=results,total_passed=sum(sum(r['ok']for r in m['rows'])for m in results),total_cases=sum(len(m['rows'])for m in results),
        topology_scope='One alternating crossing grammar with three/four levels; not broad regional style coverage',
        grid_status='Port-derived discrete placements; 128-block conversion is not implemented or proven by this experiment',human_fun='unreviewed',production_admitted=False))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',required=True);p.add_argument('--out',required=True);a=p.parse_args();print(run(a.runs,a.out))
