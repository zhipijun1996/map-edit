"""Aggregate the bounded repair continuation without changing round063 limits."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics
from . import audit_revision063_v1 as original
from .continue_revision063_v1 import OUT,rows,label
from .record_revision063_native_v1 import folder_for
def main():
 original.main();p=OUT/'verification/geometry-source-budget.json';a=core.read(p)
 extra=list((core.REPO/'pcg/results').glob('approved-r064-*/physics/*.input.json'))
 count=sum(len(core.read(p).get('cases',[]))for p in extra)
 a['continuationRawCases']=count;a['totalCaseConservativeUpperBound']+=count
 assert a['totalCaseConservativeUpperBound']<a['maximumCases']
 for row in a['rows']:
  more=list((core.REPO/'pcg/results').glob('approved-r064-'+row['name']+'-*/input-binding.json'))
  row['continuationSelectedFormalCandidates']=len({core.read(p)['cases']['sha256']for p in more})
  row['selectedFormalCandidatesAcrossTask']=row['selectedFormalCandidates']+row['continuationSelectedFormalCandidates']
  assert row['selectedFormalCandidatesAcrossTask']<=2
 assert sum(r['qualified']for r in a['rows'])==11
 assert a['nativeDirections']==23
 core.write(p,a)
 verified=[]
 for r in rows():
  n=label(r);f=folder_for(r);q=core.read(f/'qualification.json')
  if not q['passed']:assert n=='lift';continue
  v=OUT/('verification/rederived-'+n+'.json') if n not in ['hq07','s09']else core.REPO/'feedback/manual-review/implementation-results/revision-064-v1/verification'/('rederived-'+n+'.json')
  d=core.read(v);assert d['passed']and d['report']==q['report'];verified.append(physics.artifact(v))
 core.write(OUT/'verification/full-report-rederivation.json',dict(passed=True,rows=verified,fullReports=11,physicsRerun=False,source=physics.artifact(__file__)))
 print('R063_064_AGGREGATE_AUDIT_PASS',a['totalCaseConservativeUpperBound'],flush=True)
if __name__=='__main__':main()
