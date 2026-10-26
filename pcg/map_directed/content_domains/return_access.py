"""Return adaptation: original access bell first, then a separate airborne recoil."""
import copy,json
from pathlib import Path
from .returns import propose
from .probe import cases
from .engine import ContentEngine
from ..block_grid.build import traces
from ..director import REPO
from ..run import write
from pcg.prototype.workshop.rules import cmd,settle
from pcg.prototype.factory.core.quality import digest

def adapt_access(m):
    m=copy.deepcopy(m)
    for pair,pr in list(m['port_transitions'].items()):
        if m['transition_sources'].get(pair,{}).get('status')!='NEW_UNVERIFIED':continue
        new=[]
        for leg in pr:
            aimed=next((op for op in leg.get('control_plan',[])if op.get('aim_cell',{}).get('receiver')=='access'),None)
            if aimed:
                if not new:raise ValueError('supported_return_launch_required')
                launch=new[-1]['target'];query=copy.deepcopy(aimed['aim_cell']);direction=1 if leg['target']['position'][0]>launch['position'][0]else-1
                new.append(dict(kind='module',target=copy.deepcopy(launch),control_plan=[cmd('axis',value=0),cmd('shoot',aim_cell=query),cmd('wait',12),settle(launch['position'][0])],budget_ticks=720))
                leg=copy.deepcopy(leg)
                for op in leg['control_plan']:
                    if op.get('aim_cell',{}).get('receiver')=='access':op.pop('aim_cell');op['direction']=[-direction*.9886859966642595,.15]
            new.append(leg)
        m['port_transitions'][pair]=new;m['transition_options'][pair][0]['program']=new
    m['variant_id']+='/access-preparation';m['adaptation']['return_access_preparation']=dict(original_gate_window_preserved=True,extra_air_shots=0,resources_written=False,geometry_added=0)
    m['content_version']='sha256:'+digest(dict(case=m['case'],ports=m['ports'],transitions=m['port_transitions']));return m

def run(name,source):
    root=REPO/source;out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable access probe exists')
    out.mkdir();_,results=traces(root/'physics');ms=[]
    for m in json.loads((root/'modules.json').read_text()):
        c=cases(m)[0]
        if results[c['id']]['ok']:ms.append(adapt_access(propose(m,results[c['id']])))
    cs=[]
    for m in ms:
        cs += [c for c in cases(m)if'>entry/'in c['id']]
        a,b=next(iter(m['port_transitions'])).split('>');pr=copy.deepcopy(m['port_transitions'][a+'>'+b]+m['port_transitions'][b+'>'+a]);c=copy.deepcopy(m['case'])
        for i,leg in enumerate(pr):leg.update(id=str(i)+'-'+leg['target']['id'],edge_id='same-world-return')
        start,end=m['ports'][a]['dock'],m['ports'][b]['dock'];c.update(id=m['variant_id']+'/continuous-roundtrip',spawn=start['position'][:],entry_port=start['position'][:],exit_port=end['position'][:],goal=start['region'][:],pilot_program=pr,map_budget_ticks=12000,noise={},extra_required=True,extra_script=str(REPO/'pcg/map_directed/catalog_feed/extra.gd'));cs.append(c)
    write(out/'modules.json',ms);write(out/'cases.json',dict(cases=cs));rows=[]
    for c,r,e in ContentEngine(out/'physics').run(cs,'return-access-preparation'):
        row=dict(id=c['id'],ok=r['ok'],reason=r['reason'],failure=r.get('pilot',{}).get('failure'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps(row,ensure_ascii=False),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(rows),geometry_added=0,gate_timing_changed=False))
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--source',required=True);a=p.parse_args();run(a.name,a.source)
