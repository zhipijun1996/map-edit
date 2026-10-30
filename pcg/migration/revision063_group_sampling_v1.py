"""Preserve authored native-controlled group poses; keep every RNG draw/noise.

The existing sampler already preserves latches.ferry_id parked poses. This
versioned extension handles the exact reviewed S04 group_motion Cell, without
changing historical reports or any other module's sampling policy.
"""
import copy,inspect
from . import core
from .revision063_boundary_v1 import VERSIONS
from pcg.prototype.workshop import evaluate as previous
POLICY='revision063_native_group_initialization/v1'
def instantiate(case,seed,level,trial):
 value=previous.instantiate(case,seed,level,trial);s=case.get('approved_implementation',{})
 if s.get('reviewId')!='idea-spec02-s04-001' or s.get('designVersion')!=VERSIONS['idea-spec02-s04-001']:raise ValueError('native_group_sampling_not_authorized_for_this_design')
 targets={target for spec in case.get('approved_hq_cells',[]) if spec.get('kind')=='group_motion' for target in spec['targets']};assert targets=={'P','Q'}
 authored={p['platform_id']:p['initial_phase']for p in case['moving_platforms']}
 for platform in value['moving_platforms']:
  if platform['platform_id']in targets:platform['initial_phase']=authored[platform['platform_id']]
 return value
namespace={**previous.__dict__,'instantiate':instantiate};exec(compile(inspect.getsource(previous.evaluate),__file__,'exec'),namespace)
evaluate=namespace['evaluate']
def validate(folder,reference):
 from . import physics,holdout_guard
 core.verify_artifacts([reference]);record=core.read(core.resolve_artifact(reference['path']));assert record['policy']==POLICY
 core.verify_artifacts([record[k]for k in ['taskAuthorization','originalFormalReport','module','canonicalCases','sampler','diagnosis','protocol']])
 assert record['module']==physics.artifact(folder/'module.mapnote.json') and record['canonicalCases']==physics.artifact(folder/'physics-input-cases.json')
 assert record['sampler']==physics.artifact(__file__) and record['protocol']==physics.artifact(physics.FULL_PROTOCOL)
 old=core.read(core.resolve_artifact(record['originalFormalReport']['path']));assert all(not isinstance(r['holdout'],dict)for r in old['routes'])
 assert core.read(core.resolve_artifact(record['diagnosis']['path']))['passed'] and record['newSeedAllocated']is False and record['sameFrozenSelectedCandidate']is True
 assert not [o for o in holdout_guard._state()['observations']if o['source']['key']==holdout_guard._identity(folder)['key']]
 return dict(policy=POLICY,authorization=reference,sourceReport=record['originalFormalReport'],sameCandidate=True,sameSeedsAndNoise=True,changedOnlyControlledParkedPhaseSampling=True)
def validate_report(folder,report):
 from . import physics
 correction=report['samplingCorrection'];assert correction['policy']==POLICY and correction['sameCandidate'] and correction['sameSeedsAndNoise']
 core.verify_artifacts([correction['authorization'],correction['sourceReport']]);record=core.read(core.resolve_artifact(correction['authorization']['path']))
 core.verify_artifacts([record[k]for k in ['module','canonicalCases','sampler','protocol','diagnosis']]);assert record['module']==physics.artifact(folder/'module.mapnote.json') and record['canonicalCases']==physics.artifact(folder/'physics-input-cases.json')
 assert record['sampler']==physics.artifact(__file__) and record['protocol']['sha256']==core.sha(physics.FULL_PROTOCOL)
 old=core.read(core.resolve_artifact(correction['sourceReport']['path']));assert old['contentVersion']==report['contentVersion'] and all(not isinstance(r['holdout'],dict)for r in old['routes'])
 assert core.read(core.resolve_artifact(old['protocol']['path']))==core.read(core.resolve_artifact(report['protocol']['path']))
 return True
