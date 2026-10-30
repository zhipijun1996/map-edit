"""Every successful/failed raw, setup rejection and immutable snapshot retained."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics
from pcg.tools.build_archive import build
from pcg.tools.restore_archive import restore
from .continue_revision053_v1 import OUT

def main():
 paths=sorted(p.relative_to(core.REPO/'pcg').as_posix()for p in(core.REPO/'pcg/results').glob('approved-r053-*')if p.is_dir());assert paths
 name='approved-revision053-implementation-v1';m=build(name,paths,deduplicate=True,stream_parts=True);v=restore(name,verify_parts_only=True)
 core.write(OUT/'verification/raw-archive.json',dict(passed=True,runDirectories=len(paths),paths=paths,manifest=physics.artifact(core.REPO/'pcg/archives'/name/'manifest.json'),verification=v,scope='All diagnostic/screen/formal/delivery/interface/fixture successful and failed records, source snapshots and readonly reanalysis. No raw rewriting.',files=m['files']))
if __name__=='__main__':main()
