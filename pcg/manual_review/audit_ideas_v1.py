"""Exact design, native loading, immutable source, protocol and revision audit."""
import collections
import gzip
import hashlib
import json
import subprocess
from pcg.migration import core, physics
from .new_ideas_v1 import rows, label, OUT, AUTH
from .finalize_ideas_v1 import folder_for

def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()

def main():
    checks=[];versions=[];proofs=[]
    for row in rows():
        name=label(row);f=folder_for(row)
        doc=core.read(f/'module.mapnote.json');design=core.read(row['designFile'])
        assert core.sha(core.REPO/row['designFile'])==row['designFileSha256']
        objects={o['id']:o for o in doc['objects']}
        for visual in design['visualObjects']:
            if visual['type']=='route':continue
            actual=objects[visual['id']]
            assert all(actual[k]==visual[k] for k in ['type','x','y','w','h']), (name,visual['id'])
            for k in ['points','duration','dwell','initialPhase','wallClimbable']:
                if k in visual:assert actual[k]==visual[k],(name,visual['id'],k)
        assert doc['generationContract']['space']['bounds']==design['bounds']
        for original,port in zip(design['ports'],doc['generationContract']['ports']):
            assert all(original[k]==port[k]for k in ['id','position','normal','surface'])
            assert {'IN':'INPUT','OUT':'OUTPUT'}.get(original['permission'],original['permission'])==port['permission']
        core.verify_artifacts(list(core.read(f/'frozen.json').values()))
        if name != 'enemies-3':
            q=core.read(f/('qualification-reanalyzed.json' if name=='orbit' else 'qualification.json'))
            report=physics.verify_report(f,q['report'],deep=True)
            assert report['passed']
            proofs.append(dict(name=name,report=q['report'],passed=True,actualAttempts=report['actualAttempts']))
        else:
            assert not (f/'qualification.json').exists()
            assert not core.read(f/'qualification-not-run.json')['independentHoldoutUsed']
        package=core.read(f/'package-result.json');assert package['passed']
        source=core.REPO/('pcg/results/approved-ideas-'+name+'-delivery-final-v1')
        examples=[]
        for item in core.read(source/'canonical.json')['rows']:
            assert item['check']['ok']
            ev=item['evidence'];raw=json.loads(gzip.decompress((source/ev['output']).read_bytes()))['results'][ev['index']]
            assert raw['hp']==5 and not raw['returns']
            examples.append(dict(route=item['case']['route_spec']['id'],hp=raw['hp'],ticks=raw['ticks'],shots=raw['shots'],actualAirEnemyHits=item['check']['causal']['airborneEnemyHits']))
        programs={};trials=0;diagnostic_records=[]
        for run in sorted((core.REPO/'pcg/results').glob('approved-ideas-'+name+'-canonical-*')):
            if not (run/'canonical.json').exists():
                diagnostic_records.append(dict(run=core.relative(run), setupFailure=True, reason='No canonical result; preserve execution logs and input in raw archive.'))
                continue
            canonical=core.read(run/'canonical.json')
            cases=[item['case']for item in canonical['rows']]
            semantic=[dict(plan=c['control_plan'],author=c['generation_rule']['registration_source'])for c in cases]
            fingerprint=digest(semantic)
            programs.setdefault(fingerprint,[]).append(core.relative(run/'canonical.json'))
            trials+=len(cases)
            diagnostic_records.append(dict(run=core.relative(run),semantic=fingerprint,actualAttempts=len(cases)))
        maximum=core.read(AUTH/'request.json')['budget']['maximumProgramVersionsPerSpecification']
        assert len(programs)<=maximum,(name,len(programs))
        versions.append(dict(name=name,executedSemanticVersions=len(programs),maximum=maximum,diagnosticTrials=trials,versions=programs,records=diagnostic_records,unexecutedDraftsAreNotTrials=True,duplicateAliasesCountedOnceButEveryRunRetained=True,formalSelectedVersions=0 if name=='enemies-3' else 1))
        checks.append(dict(name=name,reviewId=row['reviewId'],designVersion=row['designVersion'],exactGeometry=True,exactPorts=True,qualified=name!='enemies-3',nativePackage=physics.artifact(f/'playable/godot-package.json'),nativeResult=physics.artifact(f/'package-result.json'),examples=examples))
    core.write(OUT/'verification/geometry-native-proofs.json',dict(passed=True,rows=checks,proofs=proofs))
    core.write(OUT/'verification/revision-budget.json',dict(passed=True,rows=versions))
    provenance=core.read('pcg/prototype/godot/source_provenance.json')
    assert all(core.sha(core.REPO/'pcg/prototype/godot'/p)==sha for p,sha in provenance['files'].items())
    diff=subprocess.check_output(['git','diff','--name-only','origin/main','--','generation/manual-review','generation/module-workshop'],text=True).splitlines()
    assert not diff, diff
    core.write(OUT/'verification/source-audit.json',dict(passed=True,protectedFiles=len(provenance['files']),protectedMismatches=[],designWebEdits=diff,engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),gameSourceCommit='12f6cb006d7119598e3235f4ca4f7323e4c9d092'))
    core.write(OUT/'verification/latest-main.json',dict(main=core.read(AUTH/'request.json')['main'],mergedAt=core.read(AUTH/'request.json')['startingCommit'],approvedSpecifications=85,newInRound=3,unchangedOldQualified=76,oldTotal=82,nowQualified=78,nowTotal=85,oldUnresolved=['42','50','51','52','196','220'],newUnqualified=['enemies-3']))
    print('IDEAS_GEOMETRY_NATIVE_PROOFS_SOURCE_BUDGET_PASS',[(v['name'],v['executedSemanticVersions'])for v in versions],flush=True)
if __name__=='__main__':main()
