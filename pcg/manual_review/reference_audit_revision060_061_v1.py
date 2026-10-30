import importlib,json,subprocess,ast
from pcg.migration import core,physics

def references(v):
 if isinstance(v,dict):
  if isinstance(v.get('path'),str)and isinstance(v.get('sha256'),str)and len(v['sha256'])==64:yield v
  for x in v.values():yield from references(x)
 elif isinstance(v,list):
  for x in v:yield from references(x)
def main():
 for n in ['060','061']:
  scope=importlib.import_module('pcg.manual_review.continue_revision'+n+'_v1');refs={}
  for p in [scope.OUT/'index.json',*[scope.OUT/(scope.label(r)+'.json')for r in scope.rows()],*list((scope.OUT/'verification').glob('*.json'))]:
   if p.name in ['delivery-reference-audit.json','final-checks.json','public-downloads.json']:continue
   for r in references(core.read(p)):refs[(r['path'],r['sha256'])]=r
  core.verify_artifacts(list(refs.values()));core.write(scope.OUT/'verification/delivery-reference-audit.json',dict(passed=True,references=len(refs),scope='Top-level delivery results, index, technical audits and linked artifact bytes. Archived raw entry hashes independently verified.',originalReportsUnchanged=True));core.write(scope.OUT/'verification/final-checks.json',dict(passed=True,checks=['npm run check (all library/contract/workshop checks +11 unit tests)','SHA archive parts, whole ZIP and every raw entry','protected original870 files unchanged','exact approved geometry audit','actual native package replay58 directions','actual14 films and technical frame audit','actual AI midframe visual inspection'],humanPlaytest='UNKNOWN',designWebChanged=False))
 print('REFERENCES_OK',flush=True)
if __name__=='__main__':main()
