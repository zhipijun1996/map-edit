"""Map-demanded terminal rock variants, preserving the original challenge plan."""
import argparse,copy,json
from .build import load,tags
from .probe import cases
from .mirror import mirror
from .engine import ContentEngine
from ..director import REPO
from ..run import write
from ..block_grid.contracts import declare,regions,raster,validate
from pcg.prototype.factory.core.quality import digest


def extend(m,blocks):
    m=copy.deepcopy(m);pair=next(iter(m['port_transitions']));a,b=pair.split('>');p=m['ports'][b];c=m['case'];amount=blocks*128
    if p['normal']!=[1,0]:raise ValueError('requires_right_terminal')
    idx=p['dock']['support_indices'][0]
    if any(t['platform_index']==idx for t in c.get('thorns',[])):raise ValueError('terminal_hazard_must_not_be_extended')
    old=p['dock']['position'][:];before=c['platforms'][idx][:];c['platforms'][idx][2]+=amount
    p['position'][0]+=amount;p['grid']['cell'][0]+=blocks;p['aperture'][0]+=amount;p['dock']['position'][0]+=amount;p['dock']['region'][0]+=amount
    for programs in [m['port_transitions'].values(),(o['program']for choices in m['transition_options'].values()for o in choices)]:
        for program in programs:
            if program[-1]['target']['position']==old:program[-1]['target']['position'][0]+=amount;program[-1]['target']['region'][0]+=amount
    c['exit_port']=p['dock']['position'][:];c['world_bounds'][2]+=amount
    c['ports']=[dict(id=k,position=v['dock']['position'],normal=v['normal'],support_index=v['dock']['support_indices'][0])for k,v in m['ports'].items()]
    m['action_clearance'].append([old[0]-12,old[1]-18,amount+24,36]);m['spec']['space']['core_bounds'][2]+=amount
    m['adaptation']['terminal_width_demand']=dict(blocks=blocks,index=idx,before=before,after=c['platforms'][idx],new_colliders=0,challenge_plan_changed=False,source_physics_inherited=False)
    m['variant_id']+='/exit-rock-'+str(blocks);m.pop('independent_evidence',None);m=declare(m,set().union(*(raster(r)for r in regions(m))))
    errors=validate(m)
    if errors:raise ValueError(','.join(errors))
    m['source_shape_sha256']=digest(c['platforms']);m['content_version']='sha256:'+digest(dict(case=c,ports=m['ports'],matrix=m['port_transitions']));return m


def run(name,sources):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_terminal_width_probe')
    out.mkdir();pool,audit=load(sources);ms=[];gaps=[];seen=set()
    for m in pool:
        if m['source_version']in seen or len(m['ports'])!=2 or len(m['port_transitions'])!=1:continue
        pair=next(iter(m['port_transitions']));a,b=pair.split('>');dy=m['ports'][b]['position'][1]-m['ports'][a]['position'][1]
        if dy!=-128 or 'ascent'not in tags(m,pair)or m['case'].get('moving_platforms')or m['case'].get('enemies')or m['case'].get('saws'):continue
        if m['case']['capabilities']!=['move','jump','shot_recoil']:continue
        seen.add(m['source_version'])
        for blocks in [1,2]:
            try:v=extend(m,blocks);ms.extend([v,mirror(v)])
            except ValueError as e:gaps.append(dict(version=m['source_version'],blocks=blocks,reason=str(e)))
    cs=[c for m in ms for c in cases(m)];write(out/'modules.json',ms);write(out/'cases.json',dict(cases=cs));write(out/'gaps.json',gaps);rows=[]
    engine=ContentEngine(out/'physics');engine.batch_size=8
    for c,r,e in engine.run(cs,'demanded-terminal-width'):
        row=dict(id=c['id'],ok=r['ok'],reason=r['reason'],failure=r.get('pilot',{}).get('failure'),evidence=e);rows.append(row);write(out/'rows.json',rows);print(json.dumps(row),flush=True)
    write(out/'summary.json',dict(passed=sum(r['ok']for r in rows),total=len(cs),parents=len(seen),production_admitted=False))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--sources',nargs='+',required=True);a=p.parse_args();run(a.name,a.sources)
