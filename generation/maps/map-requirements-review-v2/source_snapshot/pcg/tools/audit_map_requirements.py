"""Audit the rejected map and real planner outputs; never run Godot or fake maps."""
import argparse,json,shutil
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.block_grid.policy import load,review
from pcg.map_directed.block_grid.plan import run as plan
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha

SEEDS=['requirements-review-0','requirements-review-1','requirements-review-2']


def run(name):
    out=REPO/'generation/maps'/name
    out.mkdir(exist_ok=False)
    policy=load();write(out/'protocol.json',dict(seeds=SEEDS,design_attempts_per_seed=8,policy=policy,
        source='Existing PR #1 R2 planner and Graph+Block policy; no replacement topology generator',
        scope='Requirement audit and logical plans only; spatial assembly and physics NOT_RUN',production_admitted=False))
    previous=json.loads((REPO/'generation/maps/content-domains-region-v1/correspondence.json').read_text())['graph']
    old=review(previous,policy,physical={'all_passed':True})
    write(out/'previous-map-design-review.json',old)
    assert not old['ok']and not old['declared_requirements_satisfied']
    assert 'required_return_kind_missing/loop_back'in old['errors']and 'required_return_kind_missing/merge'in old['errors']
    rows=[]
    for i,seed in enumerate(SEEDS):
        folder=plan(name+'-plan-'+str(i),seed);target=out/('plan-'+str(i));target.mkdir()
        for p in folder.iterdir():
            if p.is_file():shutil.copy2(p,target/p.name)
        summary=json.loads((folder/'summary.json').read_text());rows.append(dict(seed=seed,**summary))
    write(out/'summary.json',dict(previous_map_rejected=True,plans=rows,physical_maps_generated=0,physics='NOT_RUN',
        general_graph_materializer='NOT_IMPLEMENTED; stage-specific selectors were deleted',regional_requirements_satisfied=False,production_admitted=False))
    bindings={name:file_sha(REPO/name)for name in [
        'pcg/map_directed/block_grid/plains-policy.json','pcg/map_directed/block_grid/policy.py','pcg/map_directed/block_grid/plan.py',
        'pcg/map_directed/direct_join/assemble.py','pcg/map_directed/direct_join/audit.py','pcg/tools/audit_map_requirements.py',
        'experiments/l4-mapgen/region_network.py','experiments/l4-mapgen/mapgen.py','pcg/map_directed/director.py',
        'pcg/prototype/workshop/production_loop.py','generation/maps/content-domains-region-v1/correspondence.json']}
    write(out/'source-binding.json',dict(files=bindings))
    for name in bindings:
        target=out/'source_snapshot'/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(REPO/name,target)
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();print(run(a.name))
