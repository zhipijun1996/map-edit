import copy,subprocess
from pcg.migration import core,physics
OUT=core.REPO/'feedback/manual-review/implementation-results/revision-061-v1';AUTH=OUT/'authorization';ROOT=core.REPO/'pcg/manual_review/implementation/revision-061-drafts-v1';FINAL=core.REPO/'pcg/manual_review/implementation/revision-061-final-v1'
def label(r):return r['reviewId'].replace('idea-spec02-','').replace('-001','')
def rows():return core.read(AUTH/'handoff.json')['rows']
def main():
 assert not AUTH.exists();h=core.read('feedback/manual-review/implementation-handoff-v1.json');rs=copy.deepcopy([r for r in h['rows']if r['reviewId'].startswith('idea-spec02-')]);assert len(rs)==7
 core.write(AUTH/'request.json',dict(verbatim='根据修改建议修改。并再次更新继续实现',main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),scope=[r['reviewId']for r in rs],exclusions='S04/S06/S09 revised pending; design webpage unchanged',budget=dict(maximumSemanticVersionsPerSpec=12,diagnosticsPerRouteVersion=18,screen=dict(clean=1,mild=6,moderate=6,minimumModeratePasses=5,seed=271028029),nativePreflightPerRouteVersion=1,selectedFormalVersionsPerSpec=1,additionalFixturesPerSpec=32,maximumNewGodotCases=30000,protocol=physics.artifact(physics.FULL_PROTOCOL)),selection='first unchanged clean+screen+native passing candidate; no holdout tuning',ellipse=dict(center=[320,256],radii=[160,144],period=8,initial_phase=0,direction='CLOCKWISE',start='leftmost; exact ellipse, not line/polyline'),noOriginalPhysicsEdits=True))
 for r in rs:
  assert core.sha(r['designFile'])==r['designFileSha256'];r['outputDirectory']=core.relative(ROOT/r['moduleId']);core.write(AUTH/'designs'/(label(r)+'.json'),core.read(r['designFile']))
 core.write(AUTH/'handoff.json',dict(rows=rs))
if __name__=='__main__':main()
