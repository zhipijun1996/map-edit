"""Fresh validation of minimal rock junctions and existing scoped reward content."""
import copy,json
from .junctions import fork,merge
from .scoped import discover
from .engine import ContentEngine
from ..director import REPO
from ..run import write

def cases(m):
    c0=m['case'];out=[]
    if m.get('port_transitions'):
        programs=[(m['ports'][a]['dock'],m['ports'][b]['dock'],pr,pair)for pair,pr in m['port_transitions'].items()for a,b in[pair.split('>')]]
    else:
        programs=[]
        for k,p in m['ports'].items():
            if m['center_to_port'].get(k):programs.append((m['center'],p['dock'],m['center_to_port'][k],'choice-to-'+k))
            if m['port_to_center'].get(k):programs.append((p['dock'],m['center'],m['port_to_center'][k],k+'-to-choice'))
    for start,end,raw,name in programs:
        c=copy.deepcopy(c0);pr=copy.deepcopy(raw)
        for i,p in enumerate(pr):p.update(id=str(i)+'-'+p['target']['id'],edge_id='independent-landform')
        marker=end['position']if start['position']!=end['position']else next((p['dock']['position']for p in m['ports'].values()if p['dock']['position']!=start['position']),m['center']['position'])
        c.update(id=m['variant_id']+'/'+name,spawn=start['position'][:],entry_port=start['position'][:],exit_port=marker[:],goal=end['region'][:],pilot_program=pr,map_budget_ticks=12000,noise={},extra_required=True,extra_script=str(REPO/'pcg/map_directed/catalog_feed/extra.gd'),required_reward_ids=[r['id']for r in c.get('reward_sites',[])])
        out.append(c)
    return out

def run(name):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable junction probe exists')
    out.mkdir();rewards,audit=discover();write(out/'scoped-library-audit.json',audit)
    # Deduplicate identical physical rewards. The parent versions and all
    # scanned records remain in the audit, not counted as new gameplay types.
    chosen=[];seen=set()
    for m in rewards:
        signature=json.dumps(m['case']['platforms'],sort_keys=True)
        if signature not in seen:seen.add(signature);chosen.append(m)
    ms=[fork(),merge(0),merge(256)]+chosen;cs=[c for m in ms for c in cases(m)];write(out/'modules.json',ms);write(out/'cases.json',dict(cases=cs));rows=[]
    engine=ContentEngine(out/'physics');engine.batch_size=8
    for c,r,e in engine.run(cs,'rock-junction-and-existing-reward'):
        row=dict(id=c['id'],ok=r['ok'],reason=r['reason'],failure=r.get('pilot',{}).get('failure'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps(row,ensure_ascii=False),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(cs),scoped_versions_scanned=len(audit),new_junctions=3,production_admitted=False))
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
