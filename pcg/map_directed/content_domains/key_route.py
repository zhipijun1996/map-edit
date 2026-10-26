"""A short reward-return route inside the unchanged 43-node physical world."""
import argparse,json
from .engine import ContentEngine
from ..director import REPO
from ..run import write
from ..graph_landforms.run import steps
from ..region_scale.materialize import case_for
from ..block_grid.verify import verify
from pcg.prototype.factory.core.engine import file_sha


def run(name,source):
    parent=REPO/source;out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_region_key_route')
    out.mkdir();c=json.loads((parent/'compiled.json').read_text());p=c['exploration_graph']['stages'][0];nodes=[p['fork'],p['reward'],p['fork']]+p['upper'][1:];case=case_for(c,steps(c,nodes),'reward-return-in-full-region')
    case.update(title='风铃平原 · 回风崖径',preview_title='完整地图中的奖励折返与高路汇合',extra_script=str(REPO/'pcg/map_directed/catalog_feed/reentrant_extra.gd'),required_reward_ids=[s['id']for s in c['case']['reward_sites']if s['id'].startswith(p['reward']+'/')],reward_claim_limit=1,maximum_coins=18)
    for leg in case['pilot_program']:
        if leg['kind']=='module':leg['entry']=dict(grounded=True,required_air_shots=1,maximum_shot_cooldown=0)
    write(out/'cases.json',dict(cases=[case]));write(out/'protocol.json',dict(parent=source,parent_compiled_sha256=file_sha(parent/'compiled.json'),whole_world_modules=len(c['modules']),scope='Short route in complete unchanged region; not a standalone Module scene'))
    rows=[]
    for unused,result,evidence in ContentEngine(out/'physics').run([case],'full-world-reward-key-route'):
        a=verify(c,case,result);row=dict(id=case['id'],ok=a['ok'],physics_ok=result['ok'],reason=result['reason'],errors=a['errors'],ticks=result.get('ticks'),evidence=evidence);rows.append(row)
    write(out/'rows.json',rows);write(out/'summary.json',dict(all_passed=all(r['ok']for r in rows),rows=rows,scope='Only this key route; parent carries the complete-region validation'))
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--source',required=True);a=p.parse_args();run(a.name,a.source)
