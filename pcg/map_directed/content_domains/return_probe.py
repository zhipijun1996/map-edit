import copy,json
from .probe import cases
from .returns import propose
from .engine import ContentEngine
from ..director import REPO
from ..run import write
from ..block_grid.build import traces

def run(name,sources):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable return probe exists')
    out.mkdir();ms=[];gaps=[];seen=set()
    for source in sources:
        root=REPO/source;_,rr=traces(root/'physics');stored=json.loads((root/'modules.json').read_text())
        for m in stored:
            if m['source_version']in seen:continue
            cs=cases(m)
            if len(cs)!=1 or not rr[cs[0]['id']]['ok']:continue
            try:proposed=propose(m,rr[cs[0]['id']])
            except ValueError as e:gaps.append(dict(version=m['source_version'],reason=str(e)));continue
            ms.append(proposed);seen.add(m['source_version'])
    # Prioritize the whole-library query's trigger and reload goals, retaining
    # the rest as explicit unspent candidate demands rather than pretending
    # every newly proposed reverse route has passed.
    selected=ms
    write(out/'modules.json',selected);write(out/'gaps.json',gaps);write(out/'deferred.json',[m['source_version']for m in ms if m not in selected]);cs=[]
    for m in selected:
        for c in cases(m):
            if'>entry/'in c['id']:cs.append(c)
        a,b=next(iter(m['port_transitions'])).split('>');pr=copy.deepcopy(m['port_transitions'][a+'>'+b]+m['port_transitions'][b+'>'+a]);c=copy.deepcopy(m['case'])
        for i,p in enumerate(pr):p.update(id=str(i)+'-'+p['target']['id'],edge_id='continuous-return')
        start=m['ports'][a]['dock'];end=m['ports'][b]['dock'];c.update(id=m['variant_id']+'/continuous-roundtrip',spawn=start['position'][:],entry_port=start['position'][:],exit_port=end['position'][:],goal=start['region'][:],pilot_program=pr,map_budget_ticks=12000,noise={},extra_required=True,extra_script=str(REPO/'pcg/map_directed/catalog_feed/extra.gd'));cs.append(c)
    write(out/'cases.json',dict(cases=cs));rows=[]
    engine=ContentEngine(out/'physics');engine.batch_size=8
    for c,r,e in engine.run(cs,'return-demand-without-helper-platforms'):
        row=dict(id=c['id'],ok=r['ok'],reason=r['reason'],failure=r.get('pilot',{}).get('failure'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps(row,ensure_ascii=False),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(cs),new_geometry=0,production_admitted=False))
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--sources',nargs='+',required=True);a=p.parse_args();run(a.name,a.sources)
