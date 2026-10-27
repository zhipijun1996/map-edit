"""Extend the established real Harness with this adapter's immutable sources."""
import shutil
from pathlib import Path
from ..content_domains.engine import ContentEngine
from ..director import REPO
from ..run import write
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest


class GraphMapEngine(ContentEngine):
    def __init__(self,out):
        super().__init__(out)
        files=list(Path(__file__).parent.glob('*'))+[REPO/'pcg/map_directed/shape_search/cycles.py',REPO/'pcg/map_directed/shape_search/block_cp.py',REPO/'pcg/map_directed/block_grid/policy.py',REPO/'pcg/map_directed/block_grid/plan.py',REPO/'pcg/prototype/plains/overhang_junction.py',REPO/'pcg/prototype/plains/branch_terraces.py',REPO/'pcg/prototype/plains/compound_terraces.py',REPO/'pcg/prototype/workshop/production_loop.py',REPO/'pcg/prototype/workshop/map_supports.py',REPO/'pcg/prototype/workshop/map_boundaries.py',REPO/'pcg/prototype/workshop/map_budget.py']
        for p in files:
            if p.suffix not in ['.py','.gd','.json']:continue
            rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p)
            target=self.out/'source_snapshot'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
        self.sim.runner_script=str(Path(__file__).with_name('runner.gd'))
        self.binding.update(runner=self.sim.runner_script,source_files=self.hashes,source_manifest_sha256=digest(self.hashes))
        write(self.out/'source_binding.json',self.binding)
