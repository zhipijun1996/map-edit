"""A real two-Macro assembly exercises each new vertical boundary direction."""
import argparse,copy,json
from .build import load,rename
from .engine import ContentEngine
from ..director import REPO
from ..run import write
from ..direct_join.canonical import export_reload
from ..direct_join.assemble import assemble_modules
from ..region_scale.materialize import case_for
from ..block_grid.verify import verify
from ..shape_search.search import search


def aperture(module):
    m=copy.deepcopy(module)
    for p in m['ports'].values():
        if p['grid']['profile']=='vertical-recoil-128/v2':p['aperture']=[p['position'][0]-64,p['position'][1]-32,128,64]
    m['adaptation']['vertical_aperture_pixels']=128
    return m


def run(name,source):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_vertical_probe')
    out.mkdir();pool,audit=load([source]);write(out/'source-qualification.json',audit);assembled=[];allcases=[]
    for i in range(2):
        mirrored=bool(i);merge=next(m for m in pool if m['selection_family']=='folding-open-merge'and('/mirror-x'in m['variant_id'])==mirrored)
        fork=next(m for m in pool if m['selection_family']=='folding-cliff-fork'and('/mirror-x'in m['variant_id'])!=mirrored)
        g=dict(entry='merge',goal='fork',nodes=[dict(id=k,role='junction',grants=[],opens=[],reward=0)for k in ['merge','fork']],edges=[dict(id='s',**{'from':'merge','to':'fork'},bidirectional=True,requires=[],switch=None,cost=1,purpose='vertical_region_transfer')],initial_abilities=['move','jump','shot_recoil'],seed=name+'/'+str(i),region='plains',branches=[])
        m=rename(aperture(merge),{k:('s'if k=='onward'else'unused-'+k)for k in merge['ports']});f=rename(aperture(fork),{k:('s'if k=='ingress'else'unused-'+k)for k in fork['ports']})
        for key,v in [('merge',m),('fork',f)]:v['id']=key;v['spec']['node_id']=key;v['spec']['node']['id']=key
        s=search(g,dict(merge=[m],fork=[f]),g['seed'],require_blocks=True);ms=s.pop('modules',[]);write(out/('search-'+str(i)+'.json'),s)
        if not ms:continue
        ms=export_reload(ms,out/('modules-'+str(i)),producer='pcg/map_directed/content_domains/seam_probe.py');c=assemble_modules(g,ms,[dict(id='s',kind='vertical_ledge')]);c.update(shop={},unresolved_rewards=[]);assembled.append(c);write(out/('compiled-'+str(i)+'.json'),c)
        down=[dict(edge_id='s',**{'from':'merge','to':'fork'})];up=[dict(edge_id='s',**{'from':'fork','to':'merge'})]
        for label,path in [('down',down),('roundtrip',down+up)]:
            case=case_for(c,path,'vertical-'+str(i)+'-'+label);case.update(extra_script=str(REPO/'pcg/map_directed/catalog_feed/reentrant_extra.gd'),reward_claim_limit=0,maximum_coins=0);allcases.append((c,case))
    write(out/'cases.json',dict(cases=[v for c,v in allcases]));rows=[];engine=ContentEngine(out/'physics');engine.batch_size=4
    for (c,case),(unused,result,evidence)in zip(allcases,engine.run([v for c,v in allcases],'vertical-boundary')):
        a=verify(c,case,result);row=dict(id=case['id'],ok=a['ok'],physics_ok=result['ok'],reason=result['reason'],errors=a['errors'],failure=result.get('pilot',{}).get('failure'),crossings=a['crossings'],evidence=evidence);rows.append(row);write(out/'rows.json',rows);print(json.dumps(row),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(rows),layouts=len(assembled),production_admitted=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--source',required=True);a=p.parse_args();run(a.name,a.source)
