"""Freeze new graph-driven producers through the existing Block/Feed Harness."""
import shutil
from pathlib import Path
from ..block_grid.engine import BlockEngine
from ..director import REPO
from ..run import write
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest
class GraphEngine(BlockEngine):
    def __init__(self,out):
        super().__init__(out)
        files=list(Path(__file__).parent.glob('*'))+[REPO/'pcg/prototype/plains/graph_landforms.py']
        for p in files:
            if p.suffix not in ['.py','.json','.gd']:continue
            rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p);q=self.out/'source_snapshot'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
        self.binding.update(source_files=self.hashes,source_manifest_sha256=digest(self.hashes));write(self.out/'source_binding.json',self.binding)
