"""User-authorized latest approved designs plus explicit42 geometry adjustment."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,hashlib,json,subprocess
from pcg.migration import core,physics
OUT=core.REPO/'feedback/manual-review/implementation-results/revision-058-v1'
AUTH=OUT/'authorization'
ROOT=core.REPO/'pcg/manual_review/implementation/revision-058-drafts-v1'
def label(r):
 n=r['reviewId']
 if n=='42':return n
 if '-left-'in n:return n.split('-left-')[1].replace('top','lt').replace('bottom','lb')
 return n.split('-')[2]
def rows():return core.read(AUTH/'handoff.json')['rows']
def main():
 assert not AUTH.exists();h=core.read('feedback/manual-review/implementation-handoff-v1.json');selected=copy.deepcopy([r for r in h['rows']if r['reviewId']=='42'or r['reviewId'].startswith('idea-31639')or r['reviewId']in ['idea-interface-s02-001','idea-interface-s07-001','idea-interface-s09-001','idea-interface-s11-001','idea-interface-s12-001','idea-interface-s15-001']]);assert len(selected)==13
 core.write(AUTH/'request.json',dict(verbatim='再更新继续实现新的模块。42可以进行调整',main=subprocess.check_output(['git','rev-parse','origin/main'],text=True).strip(),startCommit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),scope=[r['reviewId']for r in selected],excluded='unapproved HQ01-HQ05; discarded S01/S13; previous lift candidate unchanged',noDesignWebEdits=True,originalPhysics=True,budget=dict(maximumExecutedSemanticVersionsPerSpecification=12,diagnosticsPerRouteVersion=18,screen=dict(clean=1,mild=6,moderate=6,minimumModeratePasses=5,seed=271028029),nativePreflightPerRouteVersion=1,selectedFormalVersionsPerSpecification=1,additionalFixturesPerSpecification=32,protocol=physics.artifact(physics.FULL_PROTOCOL)),selection='first unchanged all-clean, all-screen and native-preflight passing candidate; never tune holdout',geometry42='extend right shore32px to x304,width208; gap80->48; keep top support, hook, OR reward and all Port positions. Change short gap jump hold8->12. Only42 geometry permitted.',parameterChoices='real24x36 body standing height=supportTop-18; platform tops not diagram staging; original native bell28x34 and reward36x36 glyph normalized about original centers only; S07 missing timer=3seconds; S11 three sensors same atomic complementary pair'))
 for r in selected:
  assert core.sha(core.REPO/r['designFile'])==r['designFileSha256'];r['baseDesignSource']={k:r[k]for k in ['designFile','designVersion','designFileSha256']}
  if r['reviewId']=='42':
   d=core.read(r['designFile']);o=next(o for o in d['visualObjects']if o['id'].endswith('/platform-4'));assert[o[k]for k in ['x','y','w']]==[336,0,176];o.update(x=304,w=208);d.pop('designVersion');d['implementationRevision']=dict(authorization=physics.artifact(AUTH/'request.json'),base=r['baseDesignSource']);d['designVersion']='sha256:'+hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest();p=AUTH/'revised-42.json';core.write(p,d);r.update(designFile=core.relative(p),designVersion=d['designVersion'],designFileSha256=core.sha(p))
  r['outputDirectory']=core.relative(ROOT/r['moduleId']);core.write(AUTH/'designs'/(label(r)+'.json'),core.read(r['designFile']))
 core.write(AUTH/'handoff.json',dict(rows=selected));print('FROZEN_SCOPE',[(label(r),r['designVersion'][:20])for r in selected])
if __name__=='__main__':main()
