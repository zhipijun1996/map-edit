"""Reproduce exact-demand warm-library retrieval and new physical tests.

Fixed reference run must be restored first. Choose --name for a fresh output.
"""
from pathlib import Path
import json,time
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.map_directed.block_grid.build import build
from pcg.map_directed.block_grid.run import cases
from pcg.map_directed.block_grid.engine import BlockEngine
from pcg.map_directed.block_grid.verify import verify
import argparse
p=argparse.ArgumentParser();p.add_argument('--name',default='block-grid-warm-reuse-v1');a=p.parse_args()
out=REPO/'pcg/results'/a.name
if out.exists():raise ValueError('immutable warm run exists')
out.mkdir();start=time.perf_counter()
write(out/'protocol.json',dict(seed='block-map-eval-0',source='block-grid-evaluation-0-v1',kind='Exact-demand candidate reuse; fresh real world tests, not new holdouts',production_admitted=False))
c=build(out,'block-map-eval-0',REPO/'pcg/results/contact-grammar-evaluation-0-v3',REPO/'pcg/results/block-grid-hub-probe-v2',REPO/'pcg/results/block-grid-source-probe-v5')
reuse=json.loads((out/'reuse-log.json').read_text());assert all(v['reused']for v in reuse),reuse
cs=cases(c);write(out/'cases.json',dict(cases=cs));rows=[];audits=[]
for case,r,e in BlockEngine(out/'physics').run(cs,'warm-block-demand'):
 a=verify(c,case,r);audits.append(dict(id=case['id'],**a));write(out/'boundary-state-verification.json',audits)
 rows.append(dict(id=case['id'],ok=a['ok'],physics_ok=r['ok'],reason=r['reason'],evidence=e));write(out/'rows.json',rows)
 print(case['id'],a['ok'],flush=True)
write(out/'summary.json',dict(all_passed=len(rows)==len(cs)and all(r['ok']for r in rows),rows=rows,passed=sum(r['ok']for r in rows),total=len(cs),payloads_reused=sum(r['reused']for r in reuse),new_generator_calls=0,seconds=time.perf_counter()-start,production_admitted=False,human_fun='unreviewed',scope='Repeated exact-demand retrieval and fresh full-world tests. Same immutable library records retained; no second enrollment of identical instance. Not fresh input holdouts.'))
