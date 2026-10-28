"""Read actual whole-world receipts; never infer generic Module admission."""
import argparse,gzip,json
from pathlib import Path
from ..run import write
from ..director import REPO
from ..region_scale.check_footprints import check
from ..valley_complete.gate_audit import reachable
from pcg.prototype.factory.core.engine import file_sha


def verify(run,out):
    run=Path(run).resolve();out=Path(out).resolve()
    if out.exists():raise ValueError('immutable_woven_checks_exist')
    out.mkdir(parents=True);c=json.loads((run/'compiled.json').read_text());g=c['exploration_graph'];cases={v['id']:v for v in json.loads((run/'cases.json').read_text())['cases']}
    seen=set();rows=[];failures=[];all_ids=set();reopened=[]
    for b in json.loads((run/'physics/batches.json').read_text()):
        path=run/'physics'/b['gzip_path']
        if file_sha(path)!=b['gzip_sha256']:raise ValueError('whole_map_raw_trace_changed')
        for result in json.loads(gzip.decompress(path.read_bytes()))['results']:
            case=cases[result['id']];all_ids.add(result['id']);legs={l['id']:l for l in case['pilot_program']}
            if not result['ok']:failures.append(result['id'])
            for w in result['pilot']['legs']:
                leg=legs[w['id']]
                if w.get('ok')and leg.get('edge_terminal'):seen.add((leg['edge_id'],leg['edge_from'],leg['edge_to']))
            rows.append(dict(id=result['id'],ok=result['ok'],seconds=result['ticks']/60,shots=result['shots'],held=bool(case.get('holdout')),
                chests=result['extra'].get('optional_challenge_events',[]),purchases=result['extra'].get('shop_events',[])))
    gates=[]
    for m in c['modules']:
        rects=[r for i,r in enumerate(m['case']['platforms'])if i not in m['case']['one_way_platform_indices']]
        for reward in m['case']['reward_sites']:
            latch=next(v for v in m['case']['latches']if v['id']==reward['required_bell'])
            start=m['core']['entry']['position'];target=reward['target']['position'];bounds=[-10000,-10000,30000,30000]
            closed=reachable(rects+[latch['gate']],start,target,bounds);opened=reachable(rects,start,target,bounds)
            gates.append(dict(module=m['id'],reward=reward['id'],closed_geometric_path=closed,open_geometric_path=opened,passed=not closed and opened))
    expected={(e['id'],e['from'],e['to'])for e in g['edges']}|{(e['id'],e['to'],e['from'])for e in g['edges']if e['bidirectional']}
    summary=json.loads((run/'summary.json').read_text())
    result=dict(schema='pcg/woven-region-checks/v1',all_passed=not failures and all_ids==set(cases)and expected<=seen and all(v['passed']for v in gates)and summary['all_passed'],
        expected_directed_edges=len(expected),observed_directed_edges=len(seen),missing_directed_edges=sorted(expected-seen),physical_failures=failures,
        geometry=check(c),closed_chamber_checks=gates,rows=rows,
        scope='Finite actual whole-world witnesses and solid enclosure; no universal ability/physical graph equivalence or human fun claim',production_admitted=False)
    write(out/'summary.json',result);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--out',required=True);a=p.parse_args();r=verify(a.run,a.out);print(json.dumps({k:r[k]for k in ['all_passed','expected_directed_edges','observed_directed_edges']},ensure_ascii=False))
    if not r['all_passed']:raise SystemExit(2)
