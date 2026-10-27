"""Reclassify the three disputed counters under the unchanged original policy.

Read existing raw only. This audit never grants admission, filters a trace,
changes a causal checker, or equates an extra button press with resource cost.
"""
import gzip
import hashlib
import json

from . import core, physics
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose, counter_classification


def _spans(values):
    result=[]
    for n in values:
        if result and n==result[-1][1]+1:result[-1][1]=n
        else:result.append([n,n])
    return result


def _raw(root,batches,evidence):
    b=batches[evidence['batch']];packed=root/b['gzip_path']
    if core.sha(packed)!=b['gzip_sha256']:raise ValueError('audit_compressed_evidence_changed')
    data=gzip.decompress(packed.read_bytes())
    if hashlib.sha256(data).hexdigest()!=b['raw_output_sha256']:raise ValueError('audit_raw_evidence_changed')
    inputs=root/'physics'/(b['batch']+'.input.json');execution=core.read(root/b['execution'])
    if execution['exit_code']or core.sha(inputs)!=execution['input_sha256']:raise ValueError('audit_execution_changed')
    c=core.read(inputs)['cases'][evidence['index']];r=json.loads(data)['results'][evidence['index']]
    if c['id']!=r['id']:raise ValueError('audit_case_identity_changed')
    return c,r,dict(input=dict(path=core.relative(inputs),sha256=core.sha(inputs)),
        compressed=dict(path=core.relative(packed),sha256=core.sha(packed)),index=evidence['index'])


def _facts(case,raw):
    fs=raw['frames'];shots=[];refills=[]
    for i,f in enumerate(fs):
        before=fs[i-1]if i else None
        if before and f['shot_charges']>before['shot_charges']:
            refills.append(dict(frame=f['frame'],before=before['shot_charges'],after=f['shot_charges'],grounded=f['grounded'],support=f['support_id']))
        if any(e['type']=='shot'for e in f.get('accepted',[])):
            shots.append({k:f.get(k)for k in ('frame','x','y','grounded','shot_charges','shot_cooldown','energy','hp')})
            shots[-1]['before']=None if before is None else{k:before.get(k)for k in ('frame','grounded','shot_charges','shot_cooldown','energy')}
            shots[-1]['minimumLaterY']=min((z['y']for z in fs[i+1:]),default=None)
    events=raw.get('plains',{}).get('events',[])
    opened={l['id']:_spans([f['frame']for f in fs if any(b['id']==l['id']and b['open']for b in f.get('plains',{}).get('bells',[]))])for l in case['latches']}
    return dict(ok=raw['ok'],shots=raw['shots'],jumps=raw['jumps'],ticks=raw['ticks'],hp=raw['hp'],returns=raw.get('returns'),
        energyRange=[min(f['energy']for f in fs),max(f['energy']for f in fs)],shotFrames=shots,chargeRefills=refills,
        events=events,actualBellOpenFrameSpans=opened,initialSnapshotCharge=fs[0]['shot_charges'],finalCharge=fs[-1]['shot_charges'])


def run():
    review=core.read(core.STATE/'counter-policy-review-v1.json');rows=[]
    for item in review['rows']:
        core.verify_artifacts([item['physicsReport']])
        report_path=core.REPO/item['physicsReport']['path'];root=report_path.parent;report=core.read(report_path)
        batches={b['batch']:b for b in core.read(root/'batches.json')}
        evaluation=core.read(core.REPO/report['routes'][0]['calibration']['path'])
        nominal_row=next(r for r in evaluation['rows']if r['level']=='clean')
        counter_row=next(r for r in core.read(core.REPO/report['counterexamples']['path'])if r['id']==item['counters'][0]['id'])
        nominal_case,nominal,nominal_evidence=_raw(root,batches,nominal_row['evidence'])
        case,raw,evidence=_raw(root,batches,counter_row['evidence'])
        author=physics.author_for(case);check=checked_purpose(author,case,raw);outcome=physics._same_outcome(case,raw)
        strict=counter_classification(case,raw,check,outcome,baseline=nominal)
        facts=_facts(case,raw)
        if case['family']=='timed-cache':
            critical=facts['shotFrames'][-1];opens=[e for e in facts['events']if e['type']=='bell_open'];last=opens[-1]
            clear=check['causal']['body_clear_frame']
            causal=dict(preliminaryOpeningFrame=opens[0]['frame'],criticalShotFrame=critical['frame'],criticalShotSnapshotGrounded=critical['grounded'],
                criticalOpeningFrame=last['frame'],bodyDoorFrames=check['causal']['body_door_frames'],completeBodyClearFrame=clear,
                criticalOpenToClearTicks=clear-last['frame'],allowedWindowTicks=case['latches'][0]['open_seconds']*60,
                firstOpeningAlreadyClosedBeforeCriticalShot=not any(b['open']for f in raw['frames']if f['frame']==critical['frame']-1 for b in f['plains']['bells']),
                finding='The preliminary ground-open window expires. The later airborne shot reopens the door and its own window carries the actual complete-body crossing.')
        else:
            critical=facts['shotFrames'][-1];lip=case['platforms'][0][1]+case['platforms'][0][3]
            causal=dict(firstProjectileImpactFrame=next(e['frame']for e in facts['events']if e['type']=='projectile_impact'),
                criticalShotFrame=critical['frame'],criticalShotBodyTop=critical['y']-18,originalEntryLipBottom=lip,
                criticalShotBelowLip=critical['y']-18>lip,criticalShotMinimumLaterY=critical['minimumLaterY'],
                criticalShotRecoveryRise=critical['y']-critical['minimumLaterY'],
                actualBellOpeningFrames=[e['frame']for e in facts['events']if e['type']=='bell_open'],
                finding='The preliminary projectile hits the supporting floor without opening the bell. After a real landing/refill, the later below-lip shot opens the pocket and raises the player to recover it.')
        rows.append(dict(moduleId=item['moduleId'],physicsReport=item['physicsReport'],nominalEvidence=nominal_evidence,counterEvidence=evidence,
            originalAuthor=dict(path=core.relative(author.__file__),sha256=core.sha(author.__file__)),
            originalStrictClassification=strict,unmodifiedOriginalPurpose=check,previousGenericAdjudication=counter_row['adjudication'],
            nominalFacts=_facts(nominal_case,nominal),counterFacts=facts,actualCausalEvidence=causal,
            actualObservedSameGoal=True,observedOmissionOfIntendedCriticalShot=False,
            extraButtonCountEstablishesResourceOrRiskCost=False,
            admission='HOLD_UNTIL_SCOPED_OBSERVER_REVIEW_AND_EVIDENCE_REBIND',
            nextStep='Remove generic override. Bind observer to actual bell-opening projectile and active crossing window; run original strict classification and explicit omit-critical-shot controls under that narrowly scoped source-bound observer. No geometry change justified by these three raw traces alone.'))
    result=dict(schema='pcg/migration-original-counter-policy-audit/v1',rows=rows,
        originalPolicy=dict(path='pcg/prototype/creative_batches/batch30_runtime/produce_v1.py',sha256=core.sha(core.REPO/'pcg/prototype/creative_batches/batch30_runtime/produce_v1.py')),
        originalStrictInvalidations=sum(r['originalStrictClassification']['invalidates_design']for r in rows),
        currentGenericOverrideIsValidEvidence=False,newGodotCalls=0,automaticAdmission=False,
        note='All three are first-shot observer mismatches on the recorded trace. This audit neither grants pass nor invents an original family exception.')
    core.write(core.STATE/'counter-original-policy-raw-audit-v1.json',result)
    print(json.dumps({k:v for k,v in result.items()if k!='rows'},ensure_ascii=False))
    return result


if __name__=='__main__':run()
