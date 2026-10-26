"""Whole-library horizontal variants; all reflected directions need new proofs."""
import argparse,copy,json
from .build import load
from .mirror import mirror
from .probe import cases
from .engine import ContentEngine
from ..director import REPO
from ..run import write


def run(name,sources):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_mirror_probe')
    out.mkdir();pool,audit=load(sources);chosen={}
    for m in pool:
        if len(m['ports'])==2 and m.get('port_transitions')and m['case']['capabilities']==['move','jump','shot_recoil']:chosen.setdefault(m['source_version'],m)
    ms=[mirror(m)for m in chosen.values()];cs=[c for m in ms for c in cases(m)]
    for m in ms:
        if not m.get('adaptation',{}).get('return_proposal'):continue
        a,b=next(iter(m['port_transitions'])).split('>');pr=copy.deepcopy(m['port_transitions'][a+'>'+b]+m['port_transitions'][b+'>'+a]);c=copy.deepcopy(m['case'])
        for i,p in enumerate(pr):p.update(id=str(i)+'-'+p['target']['id'],edge_id='continuous-return')
        start=m['ports'][a]['dock'];end=m['ports'][b]['dock'];c.update(id=m['variant_id']+'/continuous-roundtrip',spawn=start['position'][:],entry_port=start['position'][:],exit_port=end['position'][:],goal=start['region'][:],pilot_program=pr,map_budget_ticks=12000,noise={},extra_required=True,extra_script=str(REPO/'pcg/map_directed/catalog_feed/extra.gd'));cs.append(c)
    write(out/'modules.json',ms);write(out/'cases.json',dict(cases=cs));write(out/'parent-qualification.json',audit);rows=[]
    engine=ContentEngine(out/'physics');engine.batch_size=8
    for c,r,e in engine.run(cs,'reflected-native-directions'):
        row=dict(id=c['id'],ok=r['ok'],reason=r['reason'],failure=r.get('pilot',{}).get('failure'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps(row),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(cs),versions=len(ms),production_admitted=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--sources',nargs='+',required=True);a=p.parse_args();run(a.name,a.sources)
