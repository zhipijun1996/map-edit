"""Demanded verifier work, not new geometry or invented all-to-all interfaces."""
import argparse,copy,itertools,json
from .engine import GraphMapEngine
from ..content_domains.build import load
from ..content_domains.junction_probe import cases
from ..director import REPO
from ..run import write
from pcg.prototype.factory.core.quality import digest


def proposals(pool):
    result=[]
    for source in pool:
        if source.get('port_transitions'):continue
        m=copy.deepcopy(source);matrix={}
        pairs=list(itertools.permutations(m['ports'],2))
        if len(m['ports'])==1:pairs=[(next(iter(m['ports'])),next(iter(m['ports'])))]
        for a,b in pairs:
            inbound=m.get('port_to_center',{}).get(a);outbound=m.get('center_to_port',{}).get(b)
            if inbound is None or outbound is None:continue
            if not inbound and m['ports'][a]['dock']['position']!=m['center']['position']:continue
            if not outbound and m['ports'][b]['dock']['position']!=m['center']['position']:continue
            matrix[a+'>'+b]=copy.deepcopy(inbound+outbound)
        if not matrix:continue
        m['port_transitions']=matrix;m['center_port']=next(iter(m['ports']))
        if len(m['ports'])>1:m['center']=copy.deepcopy(m['ports'][m['center_port']]['dock'])
        m['variant_id']+='/ordered-pair-proposal';m.pop('independent_evidence',None)
        m['adaptation']['ordered_pair_verification']='New continuous Port-to-Port program in the same geometry; individual centre legs are not inherited proof'
        m['content_version']='sha256:'+digest(dict(case=m['case'],ports=m['ports'],matrix=matrix));result.append(m)
    return result


def run(name,sources):
    out=REPO/'pcg/results'/name;out.mkdir(exist_ok=False)
    pool,audit=load(sources);modules=proposals(pool);cs=[c for m in modules for c in cases(m)]
    write(out/'protocol.json',dict(sources=sources,scope='Fresh ordered-pair verifier proposals only; no geometry generation, Map or universal state claim',candidate_variants=len(modules),directions=len(cs),batch_size=8,production_admitted=False))
    write(out/'source-qualification.json',audit);write(out/'modules.json',modules);write(out/'cases.json',dict(cases=cs));rows=[]
    engine=GraphMapEngine(out/'physics');engine.batch_size=8
    for case,r,e in engine.run(cs,'demanded-ordered-pairs'):
        row=dict(id=case['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),failure=r.get('pilot',{}).get('failure'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps(row),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(cs),physics_only=True,whole_map='NOT_RUN',production_admitted=False))
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--sources',nargs='+',required=True);a=p.parse_args();run(a.name,a.sources)
