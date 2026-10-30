if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,importlib,inspect
from . import verify_revision059_downloads_v1 as prior
from pcg.migration import core

def main(commit):
 source=inspect.getsource(prior.run)
 source=source.replace("archive=core.REPO/'pcg/archives/approved-revision059-implementation-v1'","archive=core.REPO/('pcg/archives/approved-revision'+VERSION+'-implementation-v1')")
 source=source.replace("'approved-revision059-v1-*/*.json'","'approved-revision'+VERSION+'-v1-*/*.json'")
 source=source.replace("paths +=[OUT/'verification/counter-scope-regressions.json',OUT/'verification/rejected-native-film.json',OUT/'videos/native-hq02-B-to-T-v2/native.avi']","paths +=[OUT/'verification/full-report-rederivation.json',OUT/'verification/video-scope-addendum.json',OUT/'downloads/index.json']\n paths +=[core.resolve_artifact(core.read(core.resolve_artifact(row['result']['path']))['nativePlayable']['zip']['path'])for row in index['results']]")
 source=source.replace("7 current results/native scenes/compiled data/parameters, all31 original native receipts, 7 current native movies/manifests/receipts, qualification scope, exact design sources, audits and all5 raw archive parts.","7 current results and ZIPs/native scenes/compiled data/parameters, all native receipts, 7 current native movies/manifests/receipts, qualification scope, exact design sources, audits and every raw archive part.")
 for v in ['060','061']:
  scope=importlib.import_module('pcg.manual_review.continue_revision'+v+'_v1');ns={**prior.__dict__,'OUT':scope.OUT,'VERSION':v,'__file__':__file__};exec(compile(source,__file__,'exec'),ns);ns['run'](commit)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--commit',required=True);main(p.parse_args().commit)
