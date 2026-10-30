"""One-time review migration discovery; production never scans experiments."""
import collections,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def read(p):return json.loads(Path(p).read_text())
def priority(name):
 m=re.match(r'(?:revision|review)-(\d+)',name)
 if m:return int(m.group(1))
 return {'batch-001':0,'first-30-v2':10,'first-40-v1':20,'review-refresh-v1':25,'157-upper-block-v1':27,'clarified-three-v1':30,'new-ideas-v1':46,'lift-idea-v1':47}.get(name,-1)
def discover():
 handoff=read(ROOT/'feedback/manual-review/implementation-handoff-v1.json');candidates=collections.defaultdict(list)
 for p in sorted((ROOT/'feedback/manual-review/implementation-results').glob('*/*.json')):
  d=read(p)
  if not isinstance(d,dict)or not d.get('moduleId'):continue
  reference=d.get('module')or d.get('sourceModule')
  if not isinstance(reference,dict)or not(reference.get('path')or reference.get('file')):continue
  source=ROOT/(reference.get('path')or reference['file']);source=source.resolve()
  if source.name!='module.mapnote.json'or not source.exists():continue
  candidates[d['moduleId']].append((priority(p.parent.name),p,d,source))
 rows=[]
 for h in handoff['rows']:
  choices=sorted(candidates[h['moduleId']],key=lambda v:(v[0],str(v[1])));chosen=choices[-1]if choices else None
  row=dict(id=h['moduleId'],reviewId=h['reviewId'],approvedDesign=h['designFile'],approvedVersion=h['designVersion'],candidateCount=len(choices),state='approved_pending_implementation')
  if chosen:
   _,receipt,d,p=chosen;doc=read(p);folder=p.parent;qref=d.get('qualification');qpath=ROOT/qref['path']if isinstance(qref,dict)and qref.get('path')else folder/'qualification.json';q=read(qpath)if qpath.exists()else{}
   declared=d.get('qualified',d.get('localTechnicalQualification',d.get('status')));passed=q.get('passed')is True or declared in ['PASS','FULL_V2_VALIDATED_CANDIDATE']
   version=d.get('designVersion')or doc['generationContract']['generation'].get('approvedImplementation',{}).get('designVersion');aligned=version==h['designVersion'];design=read(ROOT/h['designFile'])
   if not aligned and design.get('schema')=='pcg/module-design/v1':
    actual={o['id']:o for o in doc['objects']}
    objects_match=all(v['id']in actual and all(actual[v['id']].get(k)==v[k]for k in ['x','y','w','h','trackId','designMotion','definition']if k in v)for v in design['visualObjects']if v['type']!='route')
    ports_match=len(design['ports'])==len(doc['generationContract']['ports'])and all(all(a[k]==b[k]for k in ['id','position','face','normal','surface','permission'])for a,b in zip(design['ports'],doc['generationContract']['ports']))
    routes_match=all(any(v['id']==r['id']and v['from']==r['from']and v['to']==r['to']for v in doc['generationContract']['routes'])for r in design['intendedRoutes'])
    aligned=objects_match and ports_match and routes_match and design['bounds']==doc['generationContract']['space']['bounds']
    row['alignmentProof']='exact approved objects, ports, route goals and bounds'if aligned else'physical/interface mismatch'
   native_ref=d.get('nativePlayable',{}).get('manifest',{}).get('path')
   native=(ROOT/native_ref).parent if native_ref else folder/'playable'
   if not(native/'godot-package.json').exists():native=folder
   native_exists=(native/'godot-package.json').exists();state='verified_scoped'if passed and aligned and native_exists else'implementation_needs_alignment'if not aligned else'implementation_needs_validation'
   row.update(state=state,module=p.relative_to(ROOT).as_posix(),receipt=receipt.relative_to(ROOT).as_posix(),qualification=qpath.relative_to(ROOT).as_posix()if qpath.exists()else None,declared=declared,qualificationPassed=q.get('passed'),aligned=aligned,sourceDesignVersion=version,native=native.relative_to(ROOT).as_posix()if native_exists else None,documentId=doc['id'])
  elif h.get('designFileKind')=='source_module_reference':row.update(state='approved_reference_pending_inspection',module=h['designFile'])
  rows.append(row)
 return dict(rows=rows,counts=dict(collections.Counter(r['state']for r in rows)))
if __name__=='__main__':
 result=discover();p=ROOT/'build/module-production-inventory.json';p.parent.mkdir(exist_ok=True);p.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result['counts'],ensure_ascii=False))
 for r in result['rows']:
  if r['state']!='verified_scoped':print(r['reviewId'],r['state'],r.get('aligned'),r.get('declared'),r.get('module'))
