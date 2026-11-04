"""User-authorized, isolated revision of eight unresolved specifications."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,hashlib,json,subprocess
from pcg.migration import core,physics
OUT=core.REPO/'feedback/manual-review/implementation-results/revision-053-v1'
AUTH=OUT/'authorization'
ROOT=core.REPO/'pcg/manual_review/implementation/revision-053-drafts-v1'
IDS={'196','51','52','42','50','220','idea-0363f85c-16c0-4b5f-b3b0-461335608db7-enemies-3','idea-96ba6bf1-9b60-470a-9128-54ae7ea44af3'}
def label(row):
    return 'three' if row['reviewId'].endswith('enemies-3') else 'lift' if row['reviewId'].startswith('idea-96ba') else row['reviewId']
def rows():return core.read(AUTH/'handoff.json')['rows']
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def main():
    assert not AUTH.exists()
    handoff=core.read('feedback/manual-review/implementation-handoff-v1.json');selected=copy.deepcopy([r for r in handoff['rows'] if r['reviewId'] in IDS]);assert len(selected)==8
    request=dict(verbatim='196下改可穿越平台，51，52增加净空。42，50，220继续实现。三怪和升降井都是偏难的，上方有宝箱，上方口增加风铃机关开门往上出。也就是上方port初始态是只出不进。',main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),startCommit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),scope=sorted(IDS),newContinuationRound=True,priorFailureAndHoldoutPreserved=True,noDesignWebEdits=True,originalPhysicsFrozen=True,budget=dict(maximumExecutedSemanticVersionsPerSpecification=12,maximumDiagnosticsPerRouteVersion=18,screen=dict(clean=1,mild=6,moderate=6,minimumModeratePasses=5,seed=271028029),nativePreflightPerRouteVersion=1,selectedFormalVersionsPerSpecification=1,additionalFixturesPerSpecification=32,protocol=physics.artifact(physics.FULL_PROTOCOL)),selection='first unchanged all-clean / screen / native-preflight passing candidate; no holdout selection',geometryChoices=dict(clearance='51/52: top roof and its hazards up128, central lower bodies/hazards down64, bounds top-128 and bottom+128; hooks and side Ports unchanged',bottom196='real64x12 one-way support at y786, original bottom Port unchanged; standard jump explicitly required for below-platform ingress',upperExit='three/lift: support down32 to y64, chest down32; bell at Port x,y24; real timed gate64x12 at boundary y0,4seconds; initial logical OUTPUT; B-to-A not requested; explicit compatible upper neighbor at y-32 for actual exit proof',difficulty='retain original enemy and lift/saw timing, motion and health; no simplification'))
    core.write(AUTH/'request.json',request)
    for row in selected:
        n=label(row);original=core.read(row['designFile']);assert core.sha(core.REPO/row['designFile'])==row['designFileSha256'];design=copy.deepcopy(original)
        row['baseDesignSource']={k:row[k]for k in ['designFile','designVersion','designFileSha256']}
        objects=design['visualObjects']
        if n in ['51','52']:
            design['bounds']['y']-=128;design['bounds']['h']+=256
            for o in objects:
                short=o['id'].split('/')[-1]
                if o['type']=='terrain' and short not in ['replay-independent-dock-entry','replay-independent-dock-exit']:
                    o['y'] += -128 if o['y']<-400 else 64
                elif o['type']=='hazard':o['y'] += -128 if short in ['hazard-0','hazard-3'] else 64
        elif n=='196':
            ident='revision053-bottom-support';objects.append(dict(id=ident,type='platform',x=78,y=786,w=64,h=12,label='底口真实可穿接岸'))
            p=next(p for p in design['ports']if p['id']=='bottom');p.update(surface='ONE_WAY_PLATFORM',supportObjectId=ident,stagingPosition=[110,768]);design['capabilityRequirements']=dict(version=1,status='defined',allOf=['jump','wall_climb'],anyOfGroups=[])
        elif n in ['three','lift']:
            p=next(p for p in design['ports']if p['id']=='B');x=p['position'][0];p.update(permission='OUTPUT',stagingPosition=[x,46])
            support=next(o for o in objects if o['id']==p['supportObjectId']);support['y']+=32
            for o in objects:
                if o['type']=='reward':o['y']+=32
            objects.extend([dict(id='revision053-top-gate',type='gate',x=x-32,y=0,w=64,h=12,mechanics=dict(kind='timed_gate',openSeconds=4)),dict(id='revision053-top-bell',type='bell',x=x-14,y=7,w=28,h=34,sourceId='top-exit-bell',targetId='revision053-top-gate',mechanics=dict(service='ShotLatch'))])
            design['intendedRoutes']=[r for r in design['intendedRoutes']if r['from']!='B']
        design['implementationRevision']=dict(authorization=physics.artifact(AUTH/'request.json'),base=row['baseDesignSource'],userAuthorized=True)
        design.pop('designVersion',None);design['designVersion']='sha256:'+digest(design)
        path=AUTH/'revised-designs'/(n+'.json');core.write(path,design)
        row.update(designFile=core.relative(path),designVersion=design['designVersion'],designFileSha256=core.sha(path),outputDirectory=core.relative(ROOT/row['moduleId']))
        if n in ['42','50','220']:
            row.update(row['baseDesignSource'])
            core.write(path,original)
    core.write(AUTH/'handoff.json',dict(rows=selected));print('REVISION053_AUTHORIZED',[(label(r),r['designVersion'][:19])for r in selected])
if __name__=='__main__':main()
