"""Prospective scope for the user's twelve requested completions."""
import copy, subprocess
from pcg.migration import core, physics
OUT=core.REPO/'feedback/manual-review/implementation-results/revision-063-v1'
AUTH=OUT/'authorization'
ROOT=core.REPO/'pcg/manual_review/implementation/revision-063-drafts-v1'
FINAL=core.REPO/'pcg/manual_review/implementation/revision-063-final-v1'
LIFT='idea-96ba6bf1-9b60-470a-9128-54ae7ea44af3'
def label(r):
 n=r['reviewId']
 if '-left-' in n:return n.split('-left-')[1].replace('top','lt').replace('bottom','lb')
 if n==LIFT:return 'lift'
 return n.replace('idea-plains-','').replace('idea-spec02-','').replace('-001','')
def rows():return core.read(AUTH/'handoff.json')['rows']
def main():
 assert not AUTH.exists()
 ids=['idea-plains-hq09-001','idea-plains-hq07-001',LIFT,*['idea-spec02-'+n+'-001' for n in ['s04','s06','s09']]]
 rs=copy.deepcopy([r for r in core.read('feedback/manual-review/implementation-handoff-v1.json')['rows'] if r['reviewId'] in ids or r['reviewId'].startswith('idea-31639')]);assert len(rs)==12
 core.write(AUTH/'request.json',dict(verbatim='h09初始态上方只出不进\n第二轮s09可以地刺间加宽一点点。\n另外4个按照你的建议修复\n6个双平台继续完成\n规格不一致修改main的规格为最新实现',main='c04fca59',startCommit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),scope=[r['reviewId'] for r in rs],specReceipt=physics.artifact('feedback/manual-review/spec-sync-r063-receipt.json'),geometry=dict(hq09='TOP initial OUTPUT; only initial L ingress',s09='lower wall and its upper thorn down16px, wall bottom unchanged',others='approved geometry unchanged'),budget=dict(maximumSemanticVersionsPerSpec=12,diagnosticsPerRouteVersion=18,screen=dict(clean=1,mild=6,moderate=6,minimumModeratePasses=5,seed=271028029),nativePreflightPerRouteVersion=1,selectedFormalVersionsPerSpec=1,additionalFixturesPerSpec=32,maximumNewGodotCases=30000,protocol=physics.artifact(physics.FULL_PROTOCOL)),selection='First unchanged all-clean, screen and native passing candidate. No tuning from holdout, no lucky reseed; all prior evidence retained.',originalPhysics=True,excluded='Three newly pending large-room proposals; all other modules'))
 for r in rs:
  assert core.sha(r['designFile'])==r['designFileSha256'];r['outputDirectory']=core.relative(ROOT/r['moduleId']);core.write(AUTH/'designs'/(label(r)+'.json'),core.read(r['designFile']))
 core.write(AUTH/'handoff.json',dict(rows=rs));print('R063_SCOPE_FROZEN',[(label(r),r['designVersion'][:19]) for r in rs])
if __name__=='__main__':main()
