"""Two paired actual return routes; frozen map, no optimization or retries."""
import argparse,copy,gzip,json,shutil
from pathlib import Path
from pcg.map_directed.woven_region.run import WovenEngine,make
from pcg.map_directed.r2_full.orchestrate import path_to,state_after
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest


def run(source,out):
    source=Path(source).resolve();out=Path(out).resolve()
    if out.exists():raise ValueError('immutable_return_experiment_exists')
    out.mkdir(parents=True);c=json.loads((source/'compiled.json').read_text());g=c['exploration_graph'];allcases=json.loads((source/'cases.json').read_text())['cases'];cases=[]
    write(out/'protocol.json',dict(source=str(source.relative_to(REPO)),source_sha256=file_sha(source/'compiled.json'),
        fixed_cases=4,attempts_per_case=1,selection='Both original expeditions, direct earned return versus shortest graph-valid alternative; no seed/layout/content changes',scope='Fresh original entry in each case; compare identical measured prefixes and actual return intervals'))
    shutil.copy2(__file__,out/'experiment-source.py')
    for i,branch in enumerate(g['branches']):
        original=next(v for v in allcases if v['id']=='woven-plains-reward-expedition-'+str(i))
        prefix=[];state=state_after(g,(g['entry'],frozenset(g['initial_abilities']),frozenset()),g['entry'])
        for step in original['r2_semantics']['logical_route']:
            prefix.append(step);state=state_after(g,state,step['to'])
            if step['to']==branch['reward']:break
        shortcut=next(e for e in g['edges']if e['purpose']=='return_shortcut'and e['from']==branch['reward'])
        for mode in ['shortcut','detour']:
            if mode=='shortcut':tail=[dict(edge_id=shortcut['id'],**{'from':shortcut['from'],'to':shortcut['to']})]
            else:
                altered=copy.deepcopy(g);altered['edges']=[e for e in g['edges']if e['id']!=shortcut['id']]
                tail,_,_=path_to(altered,state,branch['entry'])
            case=make(c,prefix+tail,'return-'+str(i)+'-'+mode,[branch['reward']]);case['return_pair']=dict(branch=i,mode=mode,shortcut=shortcut['id'],reward=branch['reward'])
            cases.append(case)
    write(out/'compiled.json',c);write(out/'cases.json',dict(cases=cases));engine=WovenEngine(out/'physics');rows=[]
    for case,result,ev in engine.run(cases,'paired-return'):
        reward=case['return_pair']['reward'];optional=[l for l in result['pilot']['legs']if l['id'].startswith('optional/'+reward)and l.get('ok')]
        start=optional[-1]['end']['frame']+1 if optional else None
        keys=['frame','x','y','vx','vy','axis','requested','shot_charges','shot_cooldown','energy','hp']
        prefix=digest([{k:f[k]for k in keys}for f in result['frames']if start is not None and f['frame']<start])
        row=dict(case=case['id'],ok=result['ok'],reason=result['reason'],**case['return_pair'],
            return_start_frame=start,return_seconds=(result['ticks']-start)/60 if start is not None else None,prefix_sha256=prefix,evidence=ev)
        rows.append(row);write(out/'rows.json',rows);print(json.dumps(row,ensure_ascii=False),flush=True)
    pairs=[]
    for i in range(2):
        a=next(r for r in rows if r['branch']==i and r['mode']=='shortcut');b=next(r for r in rows if r['branch']==i and r['mode']=='detour')
        valid=a['ok']and b['ok']and a['prefix_sha256']==b['prefix_sha256']
        pairs.append(dict(branch=i,valid=valid,identical_actual_prefix=a['prefix_sha256']==b['prefix_sha256'],
            shortcut_seconds=a['return_seconds'],detour_seconds=b['return_seconds'],saved_seconds=b['return_seconds']-a['return_seconds'] if valid else None))
    write(out/'summary.json',dict(all_passed=all(p['valid']for p in pairs),pairs=pairs,rows=rows,production_admitted=False))
    if not all(p['valid']for p in pairs):raise SystemExit(2)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);a=p.parse_args();run(a.source,a.out)
