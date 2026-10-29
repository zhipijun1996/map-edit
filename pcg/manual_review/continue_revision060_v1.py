import copy,subprocess
from pcg.migration import core,physics
from .continue_revision059_v1 import label
OUT=core.REPO/'feedback/manual-review/implementation-results/revision-060-v1'
AUTH=OUT/'authorization'
ROOT=core.REPO/'pcg/manual_review/implementation/revision-060-drafts-v1'
FINAL=core.REPO/'pcg/manual_review/implementation/revision-060-final-v1'
def rows():return core.read(AUTH/'handoff.json')['rows']
def main():
 assert not AUTH.exists();h=core.read('feedback/manual-review/implementation-handoff-v1.json');ids=['idea-plains-hq01-001','idea-plains-hq02-001','idea-interface-s12-001','idea-plains-hq03-001','idea-plains-hq07-001','idea-plains-hq08-001','idea-plains-hq09-001'];rs=copy.deepcopy([r for r in h['rows']if r['reviewId']in ids]);assert len(rs)==7
 core.write(AUTH/'request.json',dict(verbatim='根据修改建议修改。并再次更新继续实现',main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),startCommit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),mode='approved latest designs plus user-authorized prior recommendation repairs',scope=ids,exclusions='HQ06/HQ10 discarded; spec02 pending; no design webpage edits or main merge',priorRecommendations=physics.artifact(core.REPO/'feedback/manual-review/implementation-results/revision-059-v1/README.md'),authorizedRepairs=dict(hq01='State-driven group start/board/park/transfer; no geometry change.',hq02='Extend middle platform right edge128 to176 (width64 to112), allowing full supported x144 within original180px activation range; preserve original enemy/projectile; actual already-fired projectile collision proof required.',s12='Set both original moving carrier collision shapes to native one-way support, using original Godot collision and velocities. Keep tracks/phases/enemy/ports; repair actual support/takeoff/braking controls.'),noOriginalPhysicsEdits=True,noDesignWebEdits=True,budget=dict(maximumSemanticVersionsPerSpec=12,diagnosticsPerRouteVersion=18,screen=dict(clean=1,mild=6,moderate=6,minimumModeratePasses=5,seed=271028029),nativePreflightPerRouteVersion=1,selectedFormalVersionsPerSpec=1,additionalFixturesPerSpec=32,maximumNewGodotCases=30000,protocol=physics.artifact(physics.FULL_PROTOCOL)),selection='First unchanged clean+screen+native passing candidate; no holdout tuning; preserve all failures.',parameters=dict(hq09Gate='retract thorns permanently after actual bell hit; keep platform',hq09ProjectileSpeed=720,hq09ProjectileLifetime=1,hq09Cooldown=.6,hq09Delay=.05)))
 for r in rs:
  assert core.sha(core.REPO/r['designFile'])==r['designFileSha256'];r['baseDesignSource']={k:r[k]for k in ['designFile','designVersion','designFileSha256']};r['outputDirectory']=core.relative(ROOT/r['moduleId']);core.write(AUTH/'designs'/(label(r)+'.json'),core.read(r['designFile']))
 core.write(AUTH/'handoff.json',dict(rows=rs));print('ROUND060_SCOPE',[(label(r),r['designVersion'][:22])for r in rs])
if __name__=='__main__':main()
