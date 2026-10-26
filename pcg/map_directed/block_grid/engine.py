"""Source-freezing extension of FeedEngine; no simulation or acceptance fork."""
import shutil
from pathlib import Path
from ..catalog_feed.run import FeedEngine
from ..director import REPO
from ..run import write
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest

class BlockEngine(FeedEngine):
    def __init__(self,out):
        super().__init__(out)
        for p in Path(__file__).parent.glob('*'):
            if p.suffix not in ['.py','.gd','.json']:continue
            rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p);dest=self.out/'source_snapshot'/rel;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        self.root_files={}
        for name in ['module-contract.js','module-block-grid.js','model.js','capabilities.js','difficulty.js','experiments/l4-mapgen/region_network.py','experiments/l4-mapgen/mapgen.py']:
            p=REPO/name;self.root_files[name]=file_sha(p);dest=self.out/'root-contract-snapshot'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
        self.binding.update(source_files=self.hashes,source_manifest_sha256=digest(self.hashes),root_contract_files=self.root_files)
        write(self.out/'source_binding.json',self.binding)
    def run(self,cases,stage):
        for name,h in self.root_files.items():
            if file_sha(REPO/name)!=h:raise ValueError('frozen_root_contract_changed/'+name)
        for value in super().run(cases,stage):
            for name,h in self.root_files.items():
                if file_sha(REPO/name)!=h:raise ValueError('frozen_root_contract_changed/'+name)
            yield value
