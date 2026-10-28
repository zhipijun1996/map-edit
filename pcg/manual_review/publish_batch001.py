"""Export exact review drafts to the shared gallery; leave modules/catalog.json untouched."""
from pathlib import Path
import shutil
from pcg.migration import core
ROOT=core.REPO;OUT=ROOT/'pcg/manual_review/batch-001/revision-002';WEB=ROOT/'generation/manual-review/revisions/feedback-001'
SUMMARIES={
 '01':'10×6 Block：裁去底部 3 行，移除底台与低阶；中庭上方增加 1 只空中俯冲怪。',
 '02':'12×6 Block：裁去底部 5 行与 5 块低台；最高平台增加 1 只陆上哨兵。',
 '03':'6×4 Block：左岸 1 格＋空隙 4 格＋右岸 1 格；裁去底部 2 行；增加 1 空中、1 陆上怪物。',
 '04':'8×5 Block：保留越铃回身选路，移除底台；裁去底部 2 行和顶部 1 行。',
 '05':'6×5 Block：裁去底部 3 行、左侧 2 列；A 口与实际支撑移到新左边界。'}
STATUS={
 '01':'四条基础动作、端口试件与有限反例首轮通过；完整校准／留出未进行。',
 '02':'回程已有通过记录；新增哨兵后的无伤去程仍待修。',
 '03':'低出口已找到通过走法；高奖励路线仍有身体越出占地的问题。',
 '04':'基础动作、端口试件与有限反例首轮通过；完整校准／留出未进行。',
 '05':'基础动作、端口试件与有限反例首轮通过；完整校准／留出未进行。'}
def publish():
 rows=[]
 for row in core.read(OUT/'feedback.json')['rows']:
  folder=ROOT/row['candidate'];target=WEB/row['moduleId'];target.mkdir(parents=True,exist_ok=True)
  for name in ('module.mapnote.json','review-status.json'):shutil.copy2(folder/name,target/name)
  file=target/'module.mapnote.json';rid=row['reviewId'];rows.append(dict(moduleId=row['moduleId'],reviewId=rid,revision=row.get('revision','batch-001/revision-002'),baseSourceSha256=row['sourceSha256'],file=core.relative(file),sha256=core.sha(file),decisionOnSource=row['decisionOnSource'],verbatim=row['verbatim'],summary=SUMMARIES[rid],physicsSummary=('基础动作、端口试件与有限反例首轮通过；完整校准／留出未进行。' if any(v['reviewId']==rid and v['passed']for v in core.read(OUT/'final-preflight.json')['rows']) else ('高奖励路线仍待修；低出口已有可行走法。' if rid=='03' else STATUS[rid])),candidate=core.relative(folder)))
 from subprocess import run
 titles={r['moduleId']:r['title']for r in core.read(ROOT/'generation/manual-review/batch-001/batch.json')['rows']}
 short=['裁底 3 行；中庭增加空中怪。','裁底 5 行；最高平台增加陆上怪。','左 1 格＋空隙 4 格＋右 1 格；增加空中怪与陆上怪。','保留玩法；裁底 2 行、裁顶 1 行，移除底台。','裁底 3 行、裁左 2 列，A 口跟随新边界。']
 diagram_manifest=WEB/'diagram-batch.json'
 core.write(diagram_manifest,dict(rows=[dict(reviewId=r['reviewId'],moduleId=r['moduleId'],title=titles[r['moduleId']],source=r['file'],sourceSha256=r['sha256'],summary=note)for r,note in zip(rows,short)]))
 run(['python3',str(ROOT/'generation/manual-review/batch-001/render_diagrams.py'),'--manifest',str(diagram_manifest),'--out',str(WEB/'images'),'--draft'],check=True)
 for row in rows:
  image=WEB/'images'/(row['reviewId']+'.png');row['diagram']=image.relative_to(ROOT/'generation/manual-review').as_posix();row['diagramSha256']=core.sha(image)
 core.write(ROOT/'generation/manual-review/revisions/latest.json',dict(schema='pcg/manual-review-revisions/v1',rows=rows,formalLibraryChanged=False))
 core.write(WEB/'feedback.json',core.read(ROOT/'feedback/manual-review/batch-001/human-feedback-001.json'))
 core.write(WEB/'preflight.json',core.read(OUT/'final-preflight.json'))
 from pcg.migration import godot_package
 native=[]
 for row in core.read(OUT/'feedback.json')['rows']:
  package=ROOT/row['candidate']/'playable-final';item=dict(reviewId=row['reviewId'],package=core.relative(package),contentVersion=row['contentVersion'],physicsAdmission=False)
  try:item.update(nativeReplayPassed=True,proof=godot_package.verify_package(package,require_loaded=True))
  except Exception as error:item.update(nativeReplayPassed=False,conflict=str(error))
  native.append(item)
 core.write(WEB/'native-samples.json',dict(rows=native,productionAdmitted=False))
 preflight=core.read(OUT/'final-preflight.json')['rows']
 core.write(WEB/'outcome.json',dict(schema='pcg/human-review-outcome/v1',sourceFeedback='feedback/manual-review/batch-001/human-feedback-001.json',appliedEdits=5,firstPreflightPassed=[r['reviewId']for r in preflight if r['passed']],pendingRepair=['03/high-investment'],calibration='NOT_RUN',holdout='NOT_RUN',productionAdmitted=False,revisions={r['reviewId']:dict(candidate=r['candidate'],contentVersion=r['contentVersion'])for r in core.read(OUT/'feedback.json')['rows']}))
 print('Published 5 revision drafts; source library unchanged.')
if __name__=='__main__':publish()
