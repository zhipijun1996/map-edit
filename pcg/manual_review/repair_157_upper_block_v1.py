"""User-authorized top expansion of 157; original world geometry is unchanged."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,copy,inspect,shutil
from pcg.migration import core,physics,corners,godot_package,holdout_guard,pool_protocols
from pcg.prototype.workshop.rules import cmd,settle
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .prepare_review_refresh_v1 import at,end,leap
from . import finalize_first40_v1 as shared
ROOT=core.REPO/'feedback/manual-review/implementation-results/157-upper-block-v1'
AUTH=ROOT/'authorization'
WORK=core.REPO/'pcg/manual_review/implementation/157-upper-block-work-v1/game-plains-twin-gears'
FINAL=core.REPO/'pcg/manual_review/implementation/157-upper-block-final-v1'
OLD=core.REPO/'pcg/manual_review/implementation/review-refresh-final-v1/game-plains-twin-gears'
PREFIX='approved-u157-'
def row():return core.read(AUTH/'handoff.json')['rows'][0]
def folder():return FINAL/'game-plains-twin-gears'
def programs(c):
    choices=[]
    for first in ([.05,.2],[.1,.25],[.12,.24]):
        for second in ([.8,.15],[.7,.1]):
            p=at(70,282)+[dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id=c['saws'][0]['source_id'],window=first),timeout=1800),requires_saw_phase=dict(kind='saw_phase',id=c['saws'][1]['source_id'],window=second))]+at(170,282)+leap(350,282)+at(420,282)+[settle(690),cmd('jump'),dict(op='shoot',height_threshold=170,direction=[-1,0],trigger=dict(state='height_at_most',timeout=100))]+at(690,282)+[cmd('jump_release')]+end(752,282)
            choices.append(dict(first=first,second=second,control_plan=p))
    return choices

def prepare():
    if AUTH.exists():raise ValueError('authorization_already_frozen')
    AUTH.mkdir(parents=True);r=next(r for r in core.read('feedback/manual-review/implementation-handoff-v1.json')['rows']if r['reviewId']=='157');original=core.read(core.REPO/r['designFile']);target=copy.deepcopy(original);target.pop('designVersion');target['bounds'].update(y=76,h=256);target['id']+='-user-top-plus-one-block';target['designNotes']=target.get('designNotes',[])+['用户指定上方增加 1 Block；其余地貌、机关、侧口位置不变。'];target['humanFeedback']='157上高度+1block。是否可以。是否还有其它失败？';target['approvalMeaning']='User-approved chat geometry delta; original published design is preserved.';target['designVersion']='sha256:'+digest(target);core.write(AUTH/'target-design.json',target)
    core.write(AUTH/'request.json',dict(verbatim='157上高度+1block。是否可以。是否还有其它失败？',startingCommit=__import__('subprocess').check_output(['git','rev-parse','HEAD'],text=True).strip(),baseMain='f11b77564776a37fae577d02de18ea684e3d1a87',baseDesign=physics.artifact(core.REPO/r['designFile']),baseDesignVersion=r['designVersion'],authorizedChange=dict(face='TOP',blocks=1,pixels=128,before=original['bounds'],after=target['bounds']),preserved=['all terrain objects','both gears and their tracks, radii and periods','both side Ports and staging coordinates','original physics, resources and quality gates'],pendingNewApprovals=['161','162','163','165'],scope=['157'],noPublishedDesignOrWebEdits=True,diagnosticBudget=dict(candidates=6,clean=3,mild=3,moderate=3,maximumAttempts=54,selection='first candidate with all 9 trials passing, else best observed candidate for repair only; formal holdout not used'),formalBudget=dict(maximumSelectedCandidates=1,protocol=physics.artifact(physics.FULL_PROTOCOL))))
    r.update(designFile=core.relative(AUTH/'target-design.json'),designFileSha256=core.sha(AUTH/'target-design.json'),designVersion=target['designVersion'],outputDirectory=core.relative(WORK),designFileKind='user_approved_chat_delta');core.write(AUTH/'handoff.json',dict(rows=[r]));WORK.mkdir(parents=True)
    doc=core.read(OLD/'module.mapnote.json');c=core.read(OLD/'physics-input-cases.json')['cases'][0];g=doc['generationContract'];g['space']['bounds']=copy.deepcopy(target['bounds']);g['foundation'].update(heightBlocks=2,widthBlocks=6);g['validations']=[];g['staticChecks']['result']='UNKNOWN';g['space']['actionClearance'].update(status='UNKNOWN',regions=[])
    c['approved_implementation'].update(designVersion=target['designVersion'],rectangle=copy.deepcopy(target['bounds']));c['id']='approved-upper-block-157-entry-to-exit';c['max_frames']=3000
    for k in ('recorded_frames','module_sha256','noise','factory_evidence'):c.pop(k,None)
    c['control_plan']=programs(c)[0]['control_plan'];g['generation']['approvedImplementation'].update(authorization=physics.artifact(AUTH/'request.json'),designFile=physics.artifact(AUTH/'target-design.json'),designVersion=target['designVersion'],designFileKind='user_approved_chat_delta',repairSource=physics.artifact(__file__),geometryDelta=dict(topAddedPixels=128,objectsUnchanged=True,portsUnchanged=True))
    corners.annotate(doc);doc=godot_package.bind_case_behavior(doc,[c]);core.write(WORK/'module.mapnote.json',doc);core.write(WORK/'cases.json',dict(cases=[c]));core.contract(WORK/'module.mapnote.json',refresh=True);meta=core.read(OLD/'migration.json');meta.update(designVersion=target['designVersion'],humanReview='chat_top_plus_one_block',status='prepared_unverified');core.write(WORK/'migration.json',meta);core.write(WORK/'parameters.json',dict(authorization=physics.artifact(AUTH/'request.json'),bounds=target['bounds'],controls=c['control_plan'],terrainAndHazardsUnchanged=True));print('PREPARED_6x2',flush=True)

def search():
    eng,cases,authors=physics._engine(WORK,PREFIX+'control-search-v1',physics.FULL_PROTOCOL);base=cases[0];choices=programs(base);core.write(eng.out/'search-protocol.json',dict(choices=choices,calibrationSeed=271029157,maximumAttempts=54,selection='first all-pass index',newIndependentHoldout=False));inputs=[];labels={};counts={i:0 for i in range(len(choices))};checks=[]
    for i,p in enumerate(choices):
        for level in ('clean','mild','moderate'):
            for j in range(3):
                c=copy.deepcopy(base);c['id']+='-candidate-'+str(i);c['control_plan']=p['control_plan'];c=instantiate(c,271029157,level,j);inputs.append(c);labels[c['id']]=(i,level)
    for c,r,e in eng.run(inputs,'bounded-six-controls'):
        q=checked_purpose(authors[0],c,r);i,level=labels[c['id']];counts[i]+=q['ok'];checks.append(dict(candidate=i,level=level,check=q,evidence=e))
    selected=next((i for i in counts if counts[i]==9),None);core.write(eng.out/'search.json',dict(counts=counts,selected=selected,rows=checks));print('SEARCH',counts,'selected',selected,flush=True)
    if selected is None:return
    doc=core.read(WORK/'module.mapnote.json');base['control_plan']=choices[selected]['control_plan'];doc['generationContract']['generation']['approvedImplementation']['controlProgramsSha256']=digest([base['control_plan']]);doc=godot_package.bind_case_behavior(doc,[base]);core.write(WORK/'module.mapnote.json',doc);core.write(WORK/'cases.json',dict(cases=[base]));core.contract(WORK/'module.mapnote.json',refresh=True);p=core.read(WORK/'parameters.json');p.update(controls=base['control_plan'],selection=physics.artifact(eng.out/'search.json'));core.write(WORK/'parameters.json',p)

def screen():
    from . import screen_review_refresh_v1 as shared_screen
    code=inspect.getsource(shared_screen.run).replace("'approved-r024-'","'approved-u157-'")
    scope=shared_screen.__dict__.copy();exec(compile(code,__file__,'exec'),scope);scope['run'](row(),'screen-v1')

def freeze():
    code=inspect.getsource(shared.freeze).replace('approved-first40-final-v1-','approved-u157-final-v1-');scope=shared.__dict__|dict(AUTH=AUTH,ROOT=FINAL,folder_for=lambda r:folder());exec(compile(code,__file__,'exec'),scope);scope['freeze'](row());doc=core.read(folder()/'module.mapnote.json');assert doc['generationContract']['space']['bounds']==dict(x=0,y=76,w=768,h=256)

def qualify():
    f=folder();core.verify_artifacts(list(core.read(f/'frozen.json').values()));screen_path=core.REPO/'pcg/results/approved-u157-157-control-screen-screen-v1/screen.json';s=core.read(screen_path);assert s['passed']and s['sourceCases']['sha256']==core.sha(WORK/'cases.json');protocol=physics.FULL_PROTOCOL;reg=None
    try:guard=holdout_guard.check(f,protocol_path=protocol)
    except holdout_guard.HoldoutConflict:reg=holdout_guard.register_pool(f,'approved-157-top-plus-one-v1');protocol=pool_protocols.runtime_protocol(f,new_run=True);guard=holdout_guard.check(f,protocol_path=protocol)
    c=core.read(f/'physics-input-cases.json')['cases'];doc=core.read(f/'module.mapnote.json');probes=physics.seam_cases(c[0],doc)+[physics.continuous_exit(v,doc)for v in c]+[physics.continuous_entry(v,doc)for v in c];assert all(v['max_frames']<=3600 for v in c+probes);maximum=72+len(probes)+sum(len(physics.counter_cases(v))for v in c);assert maximum<=core.read(protocol)['maximumAttemptsPerModule'];core.write(f/'preflight.json',dict(protocol=physics.artifact(protocol),guard=guard,registration=reg,maximumAttempts=maximum,selection=physics.artifact(screen_path),stopping='single frozen formal run; calibration gate controls holdout; no reroll'))
    r=physics.run(f,PREFIX+'qualified-final-v1',protocol_path=protocol);core.write(f/'qualification.json',dict(passed=r['passed'],report=physics.artifact(core.REPO/'pcg/results/approved-u157-qualified-final-v1/migration-physics.json'),actualAttempts=r['actualAttempts']));print('QUALIFIED',r['passed'],r['actualAttempts'],flush=True)

def deliver():
    f=folder();protocol=pool_protocols.runtime_protocol(f)if core.read(f/'migration.json').get('holdoutPool')else physics.FULL_PROTOCOL;eng,cases,authors=physics._engine(f,PREFIX+'delivery-final-v1',protocol);items=[];checks=[]
    for c,r,e in eng.run([physics.fresh(c,'delivery')for c in cases],'native-delivery'):
        q=checked_purpose(authors[0],c,r);checks.append(dict(case=c,check=q,evidence=e));assert q['ok'],q;items.append(physics._recording(c,r))
    core.write(eng.out/'canonical.json',dict(rows=checks,passed=True));core.write(f/'playback-cases.json',dict(cases=items));godot_package.compile_package(f/'module.mapnote.json',f/'playback-cases.json',f/'playable',stable_id='game-plains-twin-gears');r=godot_package.run_package_validation(f/'playable');core.write(f/'package-result.json',r);print('NATIVE',r['passed'],flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['prepare','search','screen','freeze','qualify','deliver']);a=p.parse_args();globals()[a.action]()
