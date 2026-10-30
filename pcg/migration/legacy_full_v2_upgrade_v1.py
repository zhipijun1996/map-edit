"""One prospective FULL v2 upgrade for six already passing legacy connectors.

This is not permission to retry failed holdouts. Exact old programs, all old
route gates, the passing coverage supplement and current task authorization
are required. Normal unchanged-program pool rejection remains the default.
"""
from pathlib import Path
from . import core
PREFIX='idea-31639e2c-1a4a-487c-b1ea-c52522549fa8-left-'
ALLOWED={PREFIX+side+'-'+size for side in ['top','bottom'] for size in ['1x2','2x1','2x2']}
def validate(folder,reference,state,guard):
 if reference is None:return None
 core.verify_artifacts([reference]);record=core.read(core.resolve_artifact(reference['path']))
 if record.get('schema')!='pcg/legacy-passing-program-full-v2-upgrade/v1' or record.get('maximumPoolsPerSource')!=1 or record.get('seedsAllocated')is not False:raise ValueError('invalid_full_v2_upgrade_declaration')
 core.verify_artifacts([record['taskAuthorization']]);auth=core.read(core.resolve_artifact(record['taskAuthorization']['path']))
 if '6个双平台继续完成' not in auth.get('verbatim',''):raise ValueError('full_v2_upgrade_requires_explicit_six_connector_task')
 folder=Path(folder);identity=guard._identity(folder);canonical,cases=guard._cases(folder);doc=core.read(folder/'module.mapnote.json')
 implementation=doc['generationContract']['generation']['approvedImplementation']
 row=next((r for r in record['rows'] if r['source']==identity and r['documentSha256']==core.sha(folder/'module.mapnote.json') and r['canonicalCasesSha256']==core.sha(canonical)),None)
 if row is None or row.get('reviewId')not in ALLOWED or row['reviewId']not in auth['scope']:raise ValueError('full_v2_upgrade_not_bound_to_authorized_frozen_connector')
 if implementation['designVersion']!=row['designVersion']:raise ValueError('full_v2_upgrade_design_changed')
 core.verify_artifacts([row['legacyCases'],row['passingSupplement']]);old=core.read(core.resolve_artifact(row['legacyCases']['path']))['cases'];report=core.read(core.resolve_artifact(row['passingSupplement']['path']))
 if guard._program_signature(old)!=guard._program_signature(cases):raise ValueError('full_v2_upgrade_cannot_change_physics_program')
 completion=report.get('protocolCompletion',{})
 if report.get('passed')is not True or completion.get('fullV2Qualification')is not False or completion.get('newIndependentHoldout')is not False:raise ValueError('full_v2_upgrade_requires_passing_legacy_supplement')
 core.verify_artifacts([report['protocol']]);protocol=core.read(core.resolve_artifact(report['protocol']['path']))
 if protocol.get('schema')!='pcg/module-migration-protocol/v1':raise ValueError('full_v2_upgrade_only_from_legacy_v1')
 if len(report.get('routes',[]))!=len(cases):raise ValueError('full_v2_upgrade_missing_legacy_route')
 for route in report['routes']:
  if route.get('passed')is not True:raise ValueError('full_v2_upgrade_cannot_retry_failed_legacy_route')
  for kind in ['calibration','holdout']:
   core.verify_artifacts([route[kind]]);evaluation=core.read(core.resolve_artifact(route[kind]['path']))
   if evaluation.get('quality_gate',{}).get('status')!='awaiting_human_review' or evaluation.get('quality_gate',{}).get('reasons'):raise ValueError('full_v2_upgrade_legacy_quality_failed')
 registered=[p for p in state['independentPools'] if p['source']['key']==identity['key']]
 if registered:raise ValueError('full_v2_upgrade_already_allocated_no_reroll')
 # The existing report verifier has already bound every supplement raw batch;
 # retain its entire lineage and require the current artifact hash here.
 return dict(authorization=reference,passingLegacySupplement=row['passingSupplement'],kind='one_prospective_protocol_upgrade_of_unchanged_passing_legacy_program',newProtocolMustBeFullV2=True,notRetryOfFailedQuality=True)
