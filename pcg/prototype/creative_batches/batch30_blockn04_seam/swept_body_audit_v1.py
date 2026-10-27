"""Conservative adjacent-frame body reservations; original geometry raster."""
import gzip,json
from pathlib import Path
from . import fixtures_v2 as fixtures
from pcg.map_directed.block_grid.contracts import raster
from pcg.prototype.factory.core.engine import file_sha
HERE=Path(__file__).parent
REPO=HERE.parents[3]
def main():
    run=REPO/'pcg/results/workshop-batch30-blockn04-seam-full-v2'
    case=fixtures.fixture();owned=set(map(tuple,case['block_grid']['cells']));rows=[]
    for batch in json.loads((run/'batches.json').read_text()):
        packed=run/batch['gzip_path'];assert file_sha(packed)==batch['gzip_sha256']
        for result in json.loads(gzip.decompress(packed.read_bytes()))['results']:
            outside=[]
            for a,b in zip(result['frames'],result['frames'][1:]):
                x=min(a['x'],b['x'])-12;y=min(a['y'],b['y'])-18
                w=abs(a['x']-b['x'])+24;h=abs(a['y']-b['y'])+36
                if not raster([x,y,w,h])<=owned:outside.append(b['frame'])
            rows.append(dict(id=result['id'],unreserved_swept_body_frames=outside))
    assert len(rows)==50 and all(not r['unreserved_swept_body_frames']for r in rows)
    actor=REPO/'pcg/prototype/godot/scenes/player/player.tscn'
    assert 'size = Vector2(24, 36)'in actor.read_text()
    value=dict(schema='pcg/N04-real-body-sweep-audit/v1',actual_physics_cases=0,source_actual_cases=50,body_size=[24,36],actor_shape=dict(path=str(actor.relative_to(REPO)),sha256=file_sha(actor)),method='Conservative swept AABB of every adjacent real-frame24x36 body pair, rasterized by original upstream geometry helper; not a physics replacement',all_sweeps_in_exact_source_union=True,rows=rows)
    out=HERE/'body-sweep-audit-v1.json'
    if out.exists():raise ValueError('immutable sweep audit exists')
    out.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    old=HERE/'handoff-v1.json';handoff=json.loads(old.read_text());handoff['schema']='pcg/existing-module-continuous-fixture/v2';handoff['previous_handoff']=dict(path=str(old.relative_to(REPO)),sha256=file_sha(old));handoff['swept_real_body_audit']=dict(path=str(out.relative_to(REPO)),sha256=file_sha(out))
    (HERE/'handoff-v2.json').write_text(json.dumps(handoff,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(actual_source_traces=50,all_conservative_body_sweeps_owned=True,new_physics_cases=0)))
if __name__=='__main__':main()
