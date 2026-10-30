"""One setup-corrected rerun of the SAME selected S04 candidate and seeds."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics
from pcg.migration import revision063_group_sampling_v1 as sampling
from .continue_revision063_v1 import rows,label,AUTH,OUT
from .finalize_revision063_v1 import folder_for
def main():
 row=next(r for r in rows()if label(r)=='s04');f=folder_for(row);old=core.read(f/'qualification.json');assert not old['passed'];a=AUTH/'s04-native-group-sampling-correction.json';assert not a.exists()
 core.write(a,dict(policy=sampling.POLICY,taskAuthorization=physics.artifact(AUTH/'request.json'),originalFormalReport=old['report'],module=physics.artifact(f/'module.mapnote.json'),canonicalCases=physics.artifact(f/'physics-input-cases.json'),sampler=physics.artifact(sampling.__file__),diagnosis=physics.artifact(core.REPO/'pcg/results/approved-r063-s04-native-group-sampler-diagnostic-v1/diagnosis.json'),protocol=physics.artifact(physics.FULL_PROTOCOL),newSeedAllocated=False,sameFrozenSelectedCandidate=True,scope='Match the existing native ferry sampler rule for group_motion controlled platforms. Enemy cooldown RNG draws, all aim/timing noise, seeds, saw phases and thresholds stay identical. No independent holdout was started in the defective run.'))
 run='approved-r063-s04-native-group-sampler-correction-v1';report=physics.run(f,run,protocol_path=physics.FULL_PROTOCOL,sampling_correction=physics.artifact(a));core.write(f/'qualification-before-sampler-correction.json',old);core.write(f/'qualification.json',dict(passed=report['passed'],actualAttempts=report['actualAttempts'],report=physics.artifact(core.REPO/'pcg/results'/run/'migration-physics.json'),originalInvalidSamplingReport=old,sameFrozenSelectedCandidate=True,sameSeedsAndNoise=True))
 if report['passed']:
  p=OUT/'delivery-selection.json';mapping=core.read(p);mapping['overrides'].pop('s04',None);core.write(p,mapping)
 print('S04_SAME_CANDIDATE_NATIVE_GROUP_SAMPLER',report['passed'],report['actualAttempts'],flush=True)
if __name__=='__main__':main()
