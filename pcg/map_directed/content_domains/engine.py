"""Original physics pipeline with all new matching, matrix and grid sources frozen."""
import shutil
from pathlib import Path
from ..graph_landforms.engine import GraphEngine
from ..director import REPO
from ..run import write
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest
class ContentEngine(GraphEngine):
    def __init__(self,out):
        super().__init__(out)
        for p in Path(__file__).parent.glob('*'):
            if p.suffix not in ['.py','.gd','.json']:continue
            rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p);q=self.out/'source_snapshot'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
        self.sim.runner_script=str(Path(__file__).with_name('native_runner.gd'));self.binding.update(runner=self.sim.runner_script,source_files=self.hashes,source_manifest_sha256=digest(self.hashes));write(self.out/'source_binding.json',self.binding)
