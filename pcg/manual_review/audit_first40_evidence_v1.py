"""Read-only real-proof validation and tamper rejection; never allocate pools."""
import copy,json,shutil
from pathlib import Path
from pcg.migration import core,physics,holdout_guard,review_metadata_bindings_v1 as labels,review_boundary_repair_v2 as boundary2,review_boundary_repair_v3 as boundary3
from .first40_author_v2 import purpose
ROOT=core.REPO/'feedback/manual-review/implementation-results/first-40-v1'
def main():
    results=[]
    def reject(name,fn):
        try:fn()
        except (ValueError,KeyError)as e:results.append(dict(name=name,passed=True,rejection=str(e)));return
        raise AssertionError('tamper accepted: '+name)
    bound=core.REPO/'pcg/manual_review/implementation/first-40-bound-v1'
    for folder in sorted(bound.iterdir()):
        proof=core.read(folder/'qualification-corrected.json')['report'];report=core.read(core.resolve_artifact(proof['path']));labels.validate_lineage(report,core.resolve_artifact(proof['path']));results.append(dict(name=folder.name+' exact metadata lineage',passed=True))
        bad=copy.deepcopy(report);bad['routes'][0]['passed']=False;reject(folder.name+' cannot alter route result',lambda:labels.validate_lineage(bad,None))
    for helper,path in ((boundary2,'approved-b040-34-evidence-repaired-v1/migration-physics.json'),(boundary3,'approved-b040-17-qualified-first40-repair17-v2/migration-physics-exit-repair-v1.json')):
        report=core.read(core.REPO/'pcg/results'/path);helper.validate_lineage(report,None);results.append(dict(name=path+' exact boundary lineage',passed=True))
        bad=copy.deepcopy(report);bad['routes'][0]['passed']=False;reject(path+' cannot replace held-out routes',lambda:helper.validate_lineage(bad,None))
        bad=copy.deepcopy(report);bad['boundaryRepair']['newIndependentHoldout']=True;reject(path+' cannot create independent holdout',lambda:helper.validate_lineage(bad,None))
    ref=physics.artifact(ROOT/'authorization/continuation-verification-budget.json');budget=core.read(core.resolve_artifact(ref['path']))
    auth=core.read(ROOT/'authorization/handoff.json')['rows']
    for row in budget['rows']:
        identity=next(r for r in auth if r['reviewId']==row['reviewId']);folder=core.REPO/'pcg/manual_review/implementation/first-30-v4'/identity['moduleId'];registered=[dict(id=s)for s in row['priorPoolIds']]
        assert holdout_guard._continuation_allowance(folder,ref,registered)[0]==1
        reject(row['reviewId']+' continuation cannot be reused',lambda:holdout_guard._continuation_allowance(folder,ref,registered+[dict(id='already-used-extra-pool')]))
        reject(row['reviewId']+' continuation cannot hide prior pool',lambda:holdout_guard._continuation_allowance(folder,ref,registered[:1]))
    case=core.read('pcg/manual_review/implementation/first-40-final-v1/game-challenge-ferry-ascent/cases.json')['cases'][0]
    result=purpose(case,dict(reason='rejected_frame_budget',frames=[]));assert result['reasons']==['rejected_frame_budget']and result['causal']['actualPlayerHarm']is False;results.append(dict(name='zero-frame rejection cannot become player harm',passed=True))
    provenance=core.read('pcg/prototype/godot/source_provenance.json');project=core.REPO/'pcg/prototype/godot';bad=[p for p,h in provenance['files'].items()if core.sha(project/p)!=h];assert not bad
    core.write(ROOT/'verification/evidence-audit.json',dict(passed=True,checks=results,protectedFiles=len(provenance['files']),protectedMismatches=bad,readOnlyProofAudit=True,newPhysicsAttempts=0,newIndependentHoldout=False))
    history=ROOT/'source-history';history.mkdir(exist_ok=True)
    for name in ('first40-metadata-rebind.log','first40-metadata-resume32.log','first40-metadata-rebind-rest.log','first40-35-native.log','first40-movies-v1.log'):
        p=Path('/tmp')/name
        if p.exists():shutil.copy2(p,history/name)
    old=(core.REPO/'pcg/migration/review_metadata_bindings_v1.py').read_text().replace("if protected!={k:v for k,v in previous.items()if k!='contentVersion'}:","if protected!=previous:")
    (history/'metadata-comparison-before-content-version-fix.py.txt').write_text(old)
    print('AUDIT_PASS',len(results),'protected',len(provenance['files']))
if __name__=='__main__':main()
