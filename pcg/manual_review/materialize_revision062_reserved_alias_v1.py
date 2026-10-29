"""Keep strict original reserved experiment identity for same-input continuation.
Only missing artifact paths become read-only symlinks to archived actual outputs.
No original bytes, source, candidate, seeds or registry reservation are changed.
"""
import os
from pcg.migration import core,physics
from .continue_revision062_v1 import OUT

def main():
 base=core.REPO/'pcg/results';old=base/'approved-r062-rs12-qualified-final-v1';continued=base/'approved-r062-rs12-qualified-final-v1-same-input-resume-v1';before={p.name:core.sha(p)for p in(old/'physics').iterdir()if p.is_file()};links=[]
 for source in sorted((continued/'physics').iterdir()):
  if not source.is_file():continue
  target=old/'physics'/source.name
  if target.exists():assert core.sha(target)==core.sha(source);continue
  target.symlink_to(os.path.relpath(source,target.parent));links.append(dict(aliasPath=target.relative_to(core.REPO).as_posix(),symlink=os.readlink(target),source=physics.artifact(source)))
 assert all(core.sha(old/'physics'/n)==h for n,h in before.items());manifest=OUT/'verification/rs12-same-reserved-execution-alias.json';core.write(manifest,dict(passed=True,originalReservedExperiment=old.name,continuedExperiment=continued.name,sameCandidate=True,sameProtocolPoolSeeds=True,newPhysicsAttempts=0,originalFilesUnchanged=before,links=links,continuation=physics.artifact(continued/'continuation-audit.json'),source=physics.artifact(__file__)))
 source=continued/'migration-physics-reobserved-v1.json';report=core.read(source);report['boundaryObservationCorrection']['reservedExecutionAlias']=physics.artifact(manifest);target=old/'migration-physics-reobserved-v1.json';assert not target.exists();core.write(target,report);folder=core.REPO/'pcg/manual_review/implementation/revision-062-final-v1/idea-spec02-s12-001';q=core.read(folder/'qualification.json');core.write(folder/'qualification-reobserved-location-rejected-v1.json',q);q['report']=physics.artifact(target);q['sameReservedExecutionAlias']=physics.artifact(manifest);core.write(folder/'qualification.json',q);print('RS12_ORIGINAL_RESERVED_IDENTITY_RESTORED',len(links),flush=True)
if __name__=='__main__':main()
