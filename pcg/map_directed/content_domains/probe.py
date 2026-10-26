"""Full catalog adaptation and bounded fresh real-physics candidate validation."""
import argparse,copy,json,collections,itertools
from .catalog import scan,describe
from .adapt import adapt
from .engine import ContentEngine
from ..director import REPO
from ..run import write

def cases(m):
    out=[]
    for pair,alternatives in m['transition_options'].items():
      for option_index,option in enumerate(alternatives):
        program=option['program'];a,b=pair.split('>');c=copy.deepcopy(m['case']);start,end=m['ports'][a]['dock'],m['ports'][b]['dock'];pr=copy.deepcopy(program)
        for i,p in enumerate(pr):p.update(id=str(i)+'-'+p['target']['id'],edge_id='native-direction')
        c.update(id=m['variant_id']+'/'+pair+'/option'+str(option_index),spawn=start['position'][:],entry_port=start['position'][:],exit_port=end['position'][:]if a!=b else next(p['dock']['position']for k,p in m['ports'].items()if k!=a),goal=end['region'][:],pilot_program=pr,map_budget_ticks=12000,noise={},extra_required=True,extra_script=str(REPO/'pcg/map_directed/catalog_feed/extra.gd'))
        out.append(c)
    return out

def run(name,limit=24,target_versions=None):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable content probe exists')
    out.mkdir();items,descs=scan(out/'full-library');ms=[];audit=[]
    for item,d in zip(items,descs):
        reasons=[];m=None
        base_normals={k:p['normal'][0]for k,p in d['ports'].items()if p['normal'][0]}
        entry=d['relations'][0]['from'];free=[k for k in base_normals if k!=entry]
        overrides=[{}]+[{k:-base_normals[k]for k,v in zip(free,bits)if v}for bits in itertools.product([0,1],repeat=len(free))if any(bits)]
        for bank_budget in [32,128]:
            for normal_changes in overrides:
                for vphase in [0,-16,16,-32,32]:
                    for phase in range(0,128,16):
                        try:m=adapt(item,phase,vphase,normal_changes,bank_budget);break
                        except ValueError as e:reasons.append(str(e))
                    if m:break
                if m:break
            if m:break
        audit.append(dict(version=d['version'],family=d['family'],port_count=len(d['ports']),status='requires_fresh_physics'if m else'needs_adaptation',reasons=sorted(set(reasons))if not m else[],variant=m['variant_id']if m else None))
        if m:ms.append(m)
    write(out/'adaptation-audit.json',audit)
    # Broad feature/port/high-delta coverage first; not a named family whitelist.
    remaining=[m for m in ms if not target_versions or any(m['source_version'].startswith(v)for v in target_versions)];selected=[];seen=set()
    while remaining and len(selected)<limit:
        def tags(m):
            return {('family',m['selection_family']),('ports',len(m['ports'])),*[(t,True)for r in m['transition_sources'].values()for t in r['features']]}
        chosen=max(remaining,key=lambda m:(len(tags(m)-seen),len(m['ports']),len(m['port_transitions']),-len(m['case']['platforms']),m['source_version']));selected.append(chosen);seen|=tags(chosen);remaining.remove(chosen)
    write(out/'modules.json',selected);write(out/'deferred-candidates.json',[dict(version=m['source_version'],variant=m['variant_id'],reason='physics_budget_not_yet_spent')for m in remaining]);cs=[c for m in selected for c in cases(m)];write(out/'cases.json',dict(cases=cs));write(out/'protocol.json',dict(versions_scanned=len(items),source_candidate_limit=limit,directions=len(cs),phase='calibration',named_family_whitelist=False,holdout_used=False,production_admitted=False));rows=[]
    engine=ContentEngine(out/'physics');engine.batch_size=8
    for c,r,e in engine.run(cs,'native-content-directions'):
        row=dict(id=c['id'],ok=r['ok'],reason=r['reason'],ticks=r.get('ticks'),failure=r.get('pilot',{}).get('failure'),extra=r.get('extra'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps({k:row[k]for k in ['id','ok','reason','failure']},ensure_ascii=False),flush=True)
    write(out/'summary.json',dict(versions_scanned=len(items),adapted_versions=len(ms),tested_versions=len(selected),passed=sum(r['ok']for r in rows),total=len(rows),passed_versions=sum(all(next(r for r in rows if r['id']==c['id'])['ok']for c in cases(m))for m in selected),production_admitted=False))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--limit',type=int,default=24);p.add_argument('--versions',nargs='+');a=p.parse_args();run(a.name,a.limit,a.versions)
