"""Bind narrow strict counter re-analysis to already recorded real Godot bytes."""
import gzip
import hashlib
import json
from pathlib import Path
from . import core,physics,causal_observer
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import counter_classification

PREFIXES=('8c90c97e8fc1','490a5f1478c3','12ca61f568f3')


def run():
    rows=[]
    for prefix in PREFIXES:
        root=core.REPO/'pcg/results'/('foundation-migration-full-quality-v1-'+prefix)
        counters_path=root/'counterexamples.json';report_path=root/'migration-physics.json'
        row=next(c for c in core.read(counters_path)if'ground-preopen'in c['id'])
        evidence=row['evidence'];batch=next(b for b in core.read(root/'batches.json')if b['batch']==evidence['batch'])
        packed=root/batch['gzip_path'];data=gzip.decompress(packed.read_bytes())
        if core.sha(packed)!=batch['gzip_sha256']or hashlib.sha256(data).hexdigest()!=batch['raw_output_sha256']:
            raise ValueError('actual_counter_raw_hash_mismatch')
        inp=root/'physics'/(batch['batch']+'.input.json');execution=root/batch['execution'];receipt=core.read(execution)
        if receipt['exit_code']or core.sha(inp)!=receipt['input_sha256']:raise ValueError('actual_counter_execution_input_mismatch')
        case=core.read(inp)['cases'][evidence['index']];raw=json.loads(data)['results'][evidence['index']]
        if case['id']!=raw['id']or raw['id']!=row['id']:raise ValueError('actual_counter_identity_mismatch')
        author=physics.author_for(case);binding=core.read(root/'source_binding.json')
        author_relative=Path(author.__file__).resolve().relative_to(core.REPO/'pcg').as_posix()
        if core.sha(author.__file__)!=binding['source_files'].get(author_relative):raise ValueError('original_causal_checker_drift')
        original=physics.checked_purpose(author,case,raw);corrected=causal_observer.correct(case,raw,original)
        outcome=physics._same_outcome(case,raw)
        before=counter_classification(case,raw,original,outcome)
        after=counter_classification(case,raw,corrected,outcome)
        rows.append(dict(counterId=case['id'],sourceReport=physics.artifact(report_path),
            originalCounterReport=physics.artifact(counters_path),actualInput=physics.artifact(inp),
            actualExecution=physics.artifact(execution),rawGzip=physics.artifact(packed),
            rawOutputSha256=batch['raw_output_sha256'],rawResultIndex=evidence['index'],
            sourceBinding=physics.artifact(root/'source_binding.json'),
            originalCheck=original,originalClassifierBeforeAttribution=before,
            causalEpisodeCheck=corrected,strictOriginalClassifierAfterAttribution=after,
            sameExternalOutcome=outcome,costBasedExceptionUsed=False,
            passed=corrected['ok']and not after['invalidates_design']))
    result=dict(schema='pcg/strict-causal-observer-audit/v1',rows=rows,
        observerSource=physics.artifact(Path(causal_observer.__file__)),auditSource=physics.artifact(Path(__file__)),
        originalClassifierSource=physics.artifact(core.REPO/'pcg/prototype/creative_batches/batch30_runtime/produce_v1.py'),
        allStrictChecksPass=all(row['passed']for row in rows),newPhysicsAttempts=0,
        historicalRawOrReportsRewritten=False,humanApproval='UNKNOWN',productionApproval=False,
        scope='Re-analysis of three actual saved counters. No generic extra-action permission; original world goals and classifier retained.')
    target=core.STATE/'counter-causal-observer-strict-audit-v1.json'
    if target.exists()and core.read(target)!=result:raise ValueError('immutable_strict_audit_changed')
    core.write(target,result)
    return dict(path=core.relative(target),sha256=core.sha(target),allStrictChecksPass=result['allStrictChecksPass'])


if __name__=='__main__':print(json.dumps(run(),ensure_ascii=False))
