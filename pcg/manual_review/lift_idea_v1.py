"""Separate exact-version round for the lift approval discovered after v1 froze."""
import inspect,copy,subprocess
from pcg.migration import core,physics
from . import prepare_ideas_v1 as previous
from .prepare_review045_v1 import at,end,axis
from pcg.prototype.workshop.rules import cmd
OUT=core.REPO/'feedback/manual-review/implementation-results/lift-idea-v1'
AUTH=OUT/'authorization'
ID='idea-96ba6bf1-9b60-470a-9128-54ae7ea44af3'
def rows():return core.read(AUTH/'handoff.json')['rows']
def label(row):return 'lift'
def freeze_scope():
    handoff=core.read('feedback/manual-review/implementation-handoff-v1.json');selected=[r for r in handoff['rows']if r['reviewId']==ID];assert len(selected)==1
    row=selected[0];assert core.sha(core.REPO/row['designFile'])==row['designFileSha256']
    core.write(AUTH/'handoff.json',dict(rows=selected))
    core.write(AUTH/'decision.json',core.read(row['designDecisionSource']))
    core.write(AUTH/'request.json',dict(verbatim='更新，拿到新的创意实现，然后进行具体实现',main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),separateRound=True,geometryFrozen=True,originalPhysics=True,budget=dict(maximumExecutedSemanticVersions=12,maximumDiagnosticTrialsPerRoutePerVersion=18,screen=dict(clean=1,mild=6,moderate=6,moderatePassMinimum=5,seed=271028029),selectedFormalVersions=1,protocol=physics.artifact(physics.FULL_PROTOCOL),additionalFixtures=48),selection='first unchanged all-clean, all-screen and native-preflight passing candidate; no holdout tuning'))
def consumer_document(doc):
    from .ideas_content_v1 import reward_consumer_document
    result=reward_consumer_document(doc);objects={o['id']:o for o in result['objects']}
    for o in result['objects']:
        if not o.get('trackId'):continue
        motion=objects[o['trackId']]['designMotion']
        if o['type']=='hazard' and o.get('shape')=='gears':o['type']='gear'
        parameters={k:v for k,v in motion.items()if k!='nativeCell'}
        o.setdefault('mechanics',{})['runtimeParameters']=parameters
    return result
def decode(doc):
    from pcg.migration.godot_package import content_from_objects
    return content_from_objects(consumer_document(doc))
def dock(port):
    d=core.read(rows()[0]['designFile']);support=next(o for o in d['visualObjects']if o['id']==port['supportObjectId']);return[port['position'][0],support['y']-18]
def wait_lift(kind,identifier,**extra):
    return dict(op='wait',lift_window=dict(id=identifier,**extra),trigger=dict(after=1,state=kind,timeout=2200))
def plan_for(n,target,source,design):
    if target['from']=='B':
        plan=[axis(0),cmd('drop_through',1),dict(op='shoot',direction=[.85,.527],height_threshold=170,trigger=dict(after=4,state='descending_height',timeout=240)),previous.settle(20),dict(op='wait',height_threshold=790,trigger=dict(after=1,state='descending_height',timeout=600))]+end(192,846)
    elif target['to']=='A':
        plan=[axis(0),cmd('jump'),cmd('jump_release',4),cmd('wait',30)]+end(192,846)
    else:
        plan=[axis(0),wait_lift('lift_board','L1'),previous.settle(104),cmd('jump'),cmd('jump_release',24),wait_lift('lift_supported','L1'),wait_lift('lift_transfer','L1',next_id='L2'),previous.settle(192),cmd('jump'),cmd('jump_release',8),cmd('shoot',4,direction=[0,1]),cmd('wait',12),previous.settle(104),wait_lift('lift_supported','L2'),wait_lift('lift_finish','L2'),previous.settle(192),cmd('jump'),cmd('jump_release',8),cmd('shoot',4,direction=[0,1])]+end(192,14)
    return plan,source[0]
def prepare(row):
    source=inspect.getsource(previous.prepare).replace("registration_source='pcg/manual_review/ideas_author_v1.py'","registration_source='pcg/manual_review/lift_author_v1.py'").replace("'pcg/manual_review/ideas_author_v1.py'","'pcg/manual_review/lift_author_v1.py'")
    namespace={**previous.__dict__,'AUTH':AUTH,'label':label,'decode':decode,'dock':dock,'plan_for':plan_for}
    exec(compile(source,__file__,'exec'),namespace);namespace['prepare'](row)
if __name__=='__main__':
    freeze_scope()
    for row in rows():prepare(row)
