import sys
from pcg.migration import core,physics,holdout_guard,pool_protocols
from .continue_revision064_repairs_v1 import AUTH,OUT
def run(v):
 n=v['name'];f=core.REPO/v['folder'];core.verify_artifacts([v[k]for k in ['module','cases','parameters']]);q=core.read(f/'qualification.json');assert not q['passed'];registration=holdout_guard.register_pool(f,'approved-revision064-v1-'+n);protocol=pool_protocols.runtime_protocol(f,new_run=True);assert core.read(protocol)['schema']=='pcg/module-migration-protocol/v2';guard=holdout_guard.check(f,protocol_path=protocol)
 cs=core.read(f/'physics-input-cases.json')['cases'];doc=core.read(f/'module.mapnote.json');costs=dict(routes=sum(72 if c.get('enemies')or c.get('saws')or c.get('moving_platforms')else 50 for c in cs),boundaries=len(physics.seam_cases(cs[0],doc))+2*len(cs),counters=sum(len(physics.counter_cases(c))for c in cs));assert sum(costs.values())<=core.read(protocol)['maximumAttemptsPerModule']
 core.write(f/'preflight-r064.json',dict(authorization=physics.artifact(AUTH/'request.json'),formalSelection=physics.artifact(f/'selection-r064.json'),protocol=physics.artifact(protocol),registration=registration,guard=guard,costs=costs))
 name='approved-r064-'+n+'-qualified-final-v1';report=physics.run(f,name,protocol_path=protocol);core.write(f/'qualification-before-r064.json',q);core.write(f/'qualification.json',dict(passed=report['passed'],actualAttempts=report['actualAttempts'],report=physics.artifact(core.REPO/'pcg/results'/name/'migration-physics.json'),formalSelection=physics.artifact(f/'selection-r064.json'),priorFailedQualification=q.get('priorFailedQualification'),priorCalibrationRepair=q['knownCalibrationFailuresRepaired'],round='064',genuinelyRevisedProgram=True,originalRound063EvidenceRetained=True));print(n,'R064_FULL',report['passed'],report['actualAttempts'],flush=True)
if __name__=='__main__':
 for row in core.read(AUTH/'frozen-repairs.json')['rows']:
  if row['name']in sys.argv[1:]:run(row)
