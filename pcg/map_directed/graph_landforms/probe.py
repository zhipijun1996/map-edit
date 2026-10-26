"""Independent finite-direction tests of complete, different landform Macros."""
import argparse,copy,json
from .engine import GraphEngine
from ..director import REPO
from ..run import write
from ..block_grid.build import qualified_sources,mirror_grid
from pcg.prototype.plains.graph_landforms import fork,ascent,descent,switchback,merge,reward

def templates():
    pool=qualified_sources(REPO/'pcg/results/block-grid-source-probe-v5')
    raw=next(m for m in pool if m['selection_family']=='thorn-slot'and m['ports']['in']['normal']==[-1,0]and 'c5825'in m['variant_id'])
    ms=[fork(),ascent(640,256),ascent(640,128),ascent(768,256),descent(640),descent(768),switchback(512),switchback(384),merge(),mirror_grid(reward(raw))]
    source=copy.deepcopy(next(m for m in pool if m['selection_family']=='timed-cache'and m['ports']['in']['normal']==[-1,0]));source['case']['reward_sites']=[];source['variant_id']='existing-timed-ridge';ms.append(source)
    return ms

def cases(m):
    routes=[(a,b)for a in m['ports']for b in m['ports']if a!=b and a in m['port_to_center']and b in m['center_to_port']]
    if len(m['ports'])==1:routes=[(next(iter(m['ports'])),next(iter(m['ports'])))]
    out=[]
    for a,b in routes:
        c=copy.deepcopy(m['case']);program=copy.deepcopy(m['port_to_center'][a]+m['center_to_port'][b])
        for i,p in enumerate(program):p.update(id=f'{i:03d}-'+p['target']['id'],edge_id='independent-macro')
        start,end=m['ports'][a]['dock'],m['ports'][b]['dock']
        c.update(id=m['variant_id']+'/'+a+'-to-'+b,spawn=start['position'][:],entry_port=start['position'][:],exit_port=(m['center']['position'][:]if a==b else end['position'][:]),goal=end['region'][:],pilot_program=program,map_budget_ticks=12000,extra_required=False,noise={})
        out.append(c)
    return out

def run(name,select=None):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable landform probe exists')
    out.mkdir();ms=templates()
    if select:ms=[m for m in ms if any(s in m['variant_id']for s in select)]
    cs=[c for m in ms for c in cases(m)];write(out/'modules.json',ms);write(out/'cases.json',dict(cases=cs));write(out/'protocol.json',dict(phase='calibration',whole_map=False,original_physics=True,roles=['fork','rise','brake_drop','switchback','merge','reward_foldback'],maximum_revisions=12,production_admitted=False));rows=[]
    for c,r,e in GraphEngine(out/'physics').run(cs,'landform-directions'):
        row=dict(id=c['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),failure=r.get('pilot',{}).get('failure'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps(dict(id=c['id'],ok=r['ok'],failure=row['failure']),ensure_ascii=False),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(cs),whole_map=False,production_admitted=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--select',nargs='+');a=p.parse_args();run(a.name,a.select)
