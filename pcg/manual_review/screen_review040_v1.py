"""One bounded clean/mild/moderate calibration screen per current candidate."""
import argparse
from pcg.migration import core,physics
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .probe_review040_v1 import AUTH

def run(row,version):
    folder=core.REPO/row['outputDirectory'];eng,cases,authors=physics._engine(folder,'approved-r040-'+row['reviewId']+'-control-screen-'+version,physics.FULL_PROTOCOL)
    core.write(eng.out/'screen-protocol.json',dict(maximumAttempts=13*len(cases),calibrationSeed=271028029,selection='one existing frozen control per route; first bounded screen only; unchanged formal gates',newIndependentHoldout=False,noise=dict(clean=1,mild=6,moderate=6)))
    inputs=[];labels={};counts={c['route_spec']['id']:dict(clean=0,mild=0,moderate=0)for c in cases};rows=[]
    for i,c in enumerate(cases):
        for level,total in [('clean',1),('mild',6),('moderate',6)]:
            for j in range(total):
                v=instantiate(physics.fresh(c,'screen-'+version),271028029,level,j);inputs.append(v);labels[v['id']]=(i,level)
    for c,r,e in eng.run(inputs,'bounded-control-screen'):
        i,level=labels[c['id']];q=checked_purpose(authors[i],c,r);counts[cases[i]['route_spec']['id']][level]+=q['ok'];rows.append(dict(route=cases[i]['route_spec']['id'],level=level,check=q,evidence=e))
    passed=all(v['clean']==1 and v['mild']==6 and v['moderate']>=5 for v in counts.values());core.write(eng.out/'screen.json',dict(passed=passed,counts=counts,rows=rows,sourceCases=physics.artifact(folder/'cases.json')));print(row['reviewId'],passed,counts,flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--version',required=True);p.add_argument('ids',nargs='+');a=p.parse_args()
    for r in core.read(AUTH/'handoff.json')['rows']:
        if r['reviewId']in a.ids:run(r,a.version)
