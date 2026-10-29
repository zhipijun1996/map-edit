"""Anonymous byte verification of current delivery plus Git symlink objects.
Physical targets of aliases are supplied by the independently verified archive.
"""
import argparse,inspect,os,hashlib
from . import verify_revision059_downloads_v1 as prior
from .continue_revision062_v1 import OUT
from pcg.migration import core

def run(commit):
 s=inspect.getsource(prior.run).replace('approved-revision059-implementation-v1','approved-revision062-implementation-v1').replace('approved-revision059-v1-*','approved-revision062-v1-*')
 s=s.replace("paths +=[OUT/'verification/counter-scope-regressions.json',OUT/'verification/rejected-native-film.json',OUT/'videos/native-hq02-B-to-T-v2/native.avi']", "paths +=[OUT/'verification/full-report-rederivation.json',OUT/'verification/partial-holdout-lock-regression.json',OUT/'verification/hq07-fresh-pool-blocked.json',OUT/'verification/rs12-same-reserved-execution-alias.json',OUT/'downloads/index.json',OUT/'fixtures/rs12-native-neighbor-observation-v1/analysis.json',OUT/'fixtures/original-motor-margin-v1/report.json']\n paths +=[core.resolve_artifact(core.read(core.resolve_artifact(row['result']['path']))['nativePlayable']['zip']['path'])for row in index['results']]\n paths +=[core.REPO/p for p in ['pcg/results/approved-r062-rs12-qualified-final-v1/migration-physics-reobserved-v1.json','pcg/results/approved-r062-rs12-qualified-final-v1-same-input-resume-v1/migration-physics-reobserved-v1.json','pcg/results/approved-r062-rs12-qualified-final-v1-same-input-resume-v1/boundary-probes-reobserved-v1.json']]\n paths +=[core.REPO/row['aliasPath']for row in core.read(OUT/'verification/rs12-same-reserved-execution-alias.json')['links']]")
 s=s.replace("rel=core.relative(p);url=", "is_link=p.is_symlink();rel=p.relative_to(core.REPO).as_posix();url=")
 s=s.replace('expected=core.sha(p)',"expected=hashlib.sha256(os.readlink(p).encode()).hexdigest()if is_link else core.sha(p);expected_size=len(os.readlink(p).encode())if is_link else p.stat().st_size")
 s=s.replace('size==p.stat().st_size','size==expected_size').replace('bytes=size,passed=True)','bytes=size,passed=True,representation=\'git_symlink_target_text\'if is_link else\'file_bytes\',physicalTargetSha256=core.sha(p)if is_link else None)')
 s=s.replace('7 current results/native scenes/compiled data/parameters, all31 original native receipts, 7 current native movies/manifests/receipts, qualification scope, exact design sources, audits and all5 raw archive parts.','8 current results/ZIPs/native scenes/parameters, all34 native receipts,8 current movies, all12 raw archive parts, read-only reanalysis JSON and94 Git symlink target strings. Actual physical alias targets are SHA-bound through archive entries; symlink strings are not represented as physical raw downloads.')
 ns={**prior.__dict__,'OUT':OUT,'__file__':__file__,'os':os};exec(compile(s,__file__,'exec'),ns);ns['run'](commit)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--commit',required=True);run(p.parse_args().commit)
