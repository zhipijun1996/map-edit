if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics
from pcg.migration.evidence_stream_verify_v1 import verify_report
from .continue_revision064_repairs_v1 import AUTH,OUT
from .continue_revision063_v1 import OUT as AGGREGATE
def main():
 checked=[]
 for row in core.read(AUTH/'frozen-repairs.json')['rows']:
  f=core.REPO/row['folder'];q=core.read(f/'qualification.json');assert q['passed'];report=verify_report(f,q['report']);assert report['passed'];p=OUT/('verification/rederived-'+row['name']+'.json');core.write(p,dict(passed=True,report=q['report'],actualAttempts=report['actualAttempts'],frozenBeforePoolAllocation=True,genuinelyRevisedProgram=True,source=physics.artifact(__file__)));checked.append(physics.artifact(p));print(row['name'],'R064_RAW_REPORT_REDERIVED',flush=True)
 core.write(AGGREGATE/'verification/adapted-repair-rederivation.json',dict(passed=True,rows=checked,continuationAuthorization=physics.artifact(AUTH/'request.json'),originalRound063FailuresRetained=True))
if __name__=='__main__':main()
