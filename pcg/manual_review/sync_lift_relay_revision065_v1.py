"""Apply the user's approved single-relay design delta in a main worktree."""
import copy,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(sys.argv[1]);ID='idea-96ba6bf1-9b60-470a-9128-54ae7ea44af3'
RECEIPT='feedback/manual-review/lift-relay-r065-receipt.json'
def read(p):return json.loads((ROOT/p).read_text())
def write(p,v):
 p=ROOT/p;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
def sha(p):return hashlib.sha256((ROOT/p).read_bytes()).hexdigest()
h=read('feedback/manual-review/implementation-handoff-v1.json');row=next(r for r in h['rows']if r['reviewId']==ID);old=copy.deepcopy(row);d=read(row['designFile'])
assert d['designVersion']=='sha256:b1c25284b6c9691744e2069c655ca4c4470e295f9849528d8992459e331944d6'
relay=dict(id='relay-dock',type='platform',x=0,y=544,w=64,h=12,label='中继台：落稳 / 观察 / 换乘重试')
assert not any(o['id']==relay['id']for o in d['visualObjects']);d['visualObjects'].append(relay)
d['summary']='四台三锯保留；左侧新增64px中继台，先落稳再等上层换乘，顶口初始OUTPUT、射铃出井。'
d.setdefault('designNotes',[]).append('用户确认增加中继台：x0,y544,w64,h12。其余物件、轨道、周期、相位、停留、敌人、宝箱与接口不变。')
d['userRevision']=dict(receipt=RECEIPT,verbatim='好的，加一个中继台',acceptedProposal='中层左侧64px等候台，台面y544；不延长停留。',implementationAuthorized=True,technicalValidation='UNKNOWN_FOR_NEW_GEOMETRY')
d.pop('designVersion');d['designVersion']='sha256:'+hashlib.sha256(json.dumps(d,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest();version=d['designVersion'];folder=f'generation/module-workshop/ideas/{ID}/{version[7:19]}';file=folder+'/design.json';write(file,d)
row.update(designFile=file,designVersion=version,designFileSha256=sha(file),authorizationReceipt=RECEIPT,designDecisionSource=RECEIPT)
row.setdefault('specificationHistory',[]).append({k:old[k]for k in ['designFile','designVersion','designFileSha256']})
write(RECEIPT,dict(schema='pcg/human-specification-sync/v1',sourceType='human_feedback',decision='KEEP',verbatim='好的，加一个中继台',acceptedProposal='中层左侧增加一块64px宽、台面约y544的安全中继台。先验证中继台，不改端点停留。',rows=[dict(reviewId=ID,moduleId=ID,version=version,decision='KEEP',file=file,sha256=sha(file),addedObject=relay)],previous={k:old[k]for k in ['designFile','designVersion','designFileSha256']},implementationAuthorized=True,mainSpecSyncAuthorized=True,technicalApproval=False))
ideas=read('feedback/module-workshop/ideas-v1.json');idea=next(i for i in ideas['rows']if i['id']==ID);options=idea.get('designVariants',[])or[idea['design']];option=next(o for o in options if o['version']==old['designVersion']);idea.setdefault('designHistory',[]).append(copy.deepcopy(option));option.update(file=file,version=version,sha256=sha(file),diagram=f'ideas/{ID}/{version[7:19]}/images/{d["reviewId"]}.png')
ref=dict(path=RECEIPT,sha256=sha(RECEIPT))
if idea.get('designApprovals'):
 prior=idea['designApprovals'].pop(old['designVersion']);idea.setdefault('approvalHistory',[]).append(dict(version=old['designVersion'],receipt=prior.get('receipt')));prior['receipt']=ref;idea['designApprovals'][version]=prior
else:
 idea.setdefault('approvalHistory',[]).append(dict(version=old['designVersion'],receipt=idea.get('decisionReceipt')));idea['decisionReceipt']=ref
h['revision']='lift-relay-r065';write('feedback/manual-review/implementation-handoff-v1.json',h);write('feedback/module-workshop/ideas-v1.json',ideas)
manifest=dict(rows=[dict(reviewId=d['reviewId'],moduleId=ID,title=d['title'],summary=d['summary'],source=file,sourceSha256=sha(file),instructions=['仅新增左侧中继台；四台三锯运动参数保持。','新几何技术结果待真实验证。'])]);write(folder+'/diagram-batch.json',manifest)
subprocess.run(['python3',str(ROOT/'generation/manual-review/batch-001/render_diagrams.py'),'--manifest',str(ROOT/folder/'diagram-batch.json'),'--out',str(ROOT/folder/'images'),'--draft'],check=True,cwd=ROOT)
subprocess.run(['node','tools/build_module_workshop.mjs'],check=True,cwd=ROOT)
print('R065_SINGLE_RELAY_SPEC',version,file,flush=True)
