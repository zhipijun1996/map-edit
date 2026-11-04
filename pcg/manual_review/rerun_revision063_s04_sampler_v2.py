"""Continue after source snapshot setup rejection; no physics ran in v1."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import shutil
from pcg.migration import core,physics
from .continue_revision063_v1 import rows,label,AUTH,OUT
from .finalize_revision063_v1 import folder_for
def main():
 row=next(r for r in rows()if label(r)=='s04');f=folder_for(row);old=core.read(f/'qualification.json');a=AUTH/'s04-native-group-sampling-correction.json';local=f/'sampling-correction-authorization.json';assert not local.exists();shutil.copy2(a,local);assert core.sha(a)==core.sha(local)
 failed=core.REPO/'pcg/results/approved-r063-s04-native-group-sampler-correction-v1';assert not list((failed/'physics').glob('*.input.json'))
 core.write(OUT/'verification/s04-sampler-setup-rejection.json',dict(passed=True,actualGodotCases=0,reason='Source snapshot root is pcg; the authorization file outside that root was rejected before engine execution.',continuedWithByteIdenticalAuthorizationCopy=physics.artifact(local),originalAuthorization=physics.artifact(a),candidateAndSeedsChanged=False))
 run='approved-r063-s04-native-group-sampler-correction-v2';report=physics.run(f,run,protocol_path=physics.FULL_PROTOCOL,sampling_correction=physics.artifact(local));core.write(f/'qualification-before-sampler-correction.json',old);core.write(f/'qualification.json',dict(passed=report['passed'],actualAttempts=report['actualAttempts'],report=physics.artifact(core.REPO/'pcg/results'/run/'migration-physics.json'),originalInvalidSamplingReport=old,sameFrozenSelectedCandidate=True,sameSeedsAndNoise=True))
 if report['passed']:
  p=OUT/'delivery-selection.json';mapping=core.read(p);mapping['overrides'].pop('s04',None);core.write(p,mapping)
 print('S04_SAME_CANDIDATE_NATIVE_GROUP_SAMPLER',report['passed'],report['actualAttempts'],flush=True)
if __name__=='__main__':main()
