// Static first-open/offline view of this repository's immutable candidate store.
// This does not generate geometry, run physics, or promote assembly/integration.
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {execFileSync} from 'node:child_process';
import {validateDocument} from '../model.js';
import {validateGenerationContract} from '../module-contract.js';
import {renderContractSvg} from '../module-contract-render.js';
import {repositoryEntry,validateRepositoryCatalog,SCOPE_NAMES} from '../repository-library-client.js';

const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const output=path.join(root,'library/workshop');
const candidateRoot=path.join(root,'pcg/module_library/store/candidates');
const args=process.argv.slice(2),check=args.includes('--check');
if(args.some(a=>a!=='--check'))throw Error('Usage: node tools/build-repository-library.mjs [--check]');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
const hash=b=>createHash('sha256').update(b).digest('hex');
const json=value=>Buffer.from(JSON.stringify(value,null,2)+'\n');
const familyNames={
  'thorn-slot':'尖刺空槽反冲',
  'chase-landing':'击铃追赶移动载台',
  'timed-cache':'反冲穿越短时门',
  'brake-under-ledge':'岩沿下反冲入槽',
  'one-shot-two-routes':'单发弹药高低路线',
  'air-refund':'命中回充两枪上岸',
};
function names(){
  const result=new Map();
  // Historical interface labels are stable in the published twelve-module set.
  const counters=new Map();
  for(const m of read('generation/workshop/v2/modules/manifest.json').modules){
    const i=(counters.get(m.family)??0)+1;counters.set(m.family,i);
    result.set(m.contentVersion,`${familyNames[m.family]??m.family} · 接口 ${i}`);
  }
  for(const m of read('generation/workshop/map-demand-rework-v3/modules/manifest.json').modules)
    result.set(m.contentVersion,'击铃追赶移动载台 · Map 适配');
  // Retain a readable name for the held record without counting it in main20.
  for(const item of read('pcg/creative-production/novelty-review/selected20.json').selected)
    if(item.relation_id==='machinery/carrier-rendezvous')result.set(item.version,item.name);
  // Current public names take priority over all historical display labels.
  for(const clip of read('generation/workshop/creative20-v1/manifest.json').clips)
    result.set(clip.contentVersion,clip.name);
  if(fs.existsSync(path.join(root,'generation/workshop/plains50-v1/manifest.json')))
    for(const module of read('generation/workshop/plains50-v1/manifest.json').modules)
      result.set(module.contentVersion,module.name);
  return result;
}
function withdrawnVersions(){
  const result=new Set(),directory=path.join(root,'pcg/feedback/content-withdrawals');
  for(const name of fs.readdirSync(directory).filter(n=>n.endsWith('.json')).sort()){
    const notice=JSON.parse(fs.readFileSync(path.join(directory,name),'utf8'));
    if(notice.schema!=='pcg/content-technical-withdrawal/v1'||!Array.isArray(notice.contentVersions))throw Error('Invalid withdrawal notice: '+name);
    for(const version of notice.contentVersions){
      if(!/^sha256:[a-f0-9]{64}$/.test(version))throw Error('Invalid withdrawn version: '+name);
      result.add(version);
    }
  }
  return result;
}
function scope(row){
  return row?.selected_for_plains_candidates?'plains':row?.selection_reason==='reserved_for_later_abilities'?'advanced':row?.selection_reason==='pacing_held'?'held':'unclassified';
}
function managedFiles(directory,extension){
  if(!fs.existsSync(directory))return [];
  return fs.readdirSync(directory).filter(n=>n.endsWith(extension)).sort();
}
function main(){
  const old=check?read('library/workshop/catalog.json'):null;
  if(old)validateRepositoryCatalog(old);
  // A check compares artifacts with their sources. A later commit alone does
  // not invalidate the original build stamp, and --check never invokes git.
  const sourceCommit=old?.sourceCommit??execFileSync('git',['rev-parse','HEAD'],{cwd:root,encoding:'utf8'}).trim();
  const view=read(fs.existsSync(path.join(root,'generation/workshop/plains-recoil-current/catalog.json'))?'generation/workshop/plains-recoil-current/catalog.json':'generation/workshop/plains-recoil-v1/catalog.json');
  const curated=new Map(view.rows.map(row=>[row.contentVersion,row]));
  if(curated.size!==view.rows.length)throw Error('Duplicate plains curation version');
  const titles=names(),withdrawn=withdrawnVersions(),modules=[],files=new Map();
  const adaptationNumbers=new Map();let caseHashesChecked=0,withdrawnSkipped=0;
  // Validate every source before any generated output is changed.
  for(const hex of fs.readdirSync(candidateRoot).filter(n=>/^[a-f0-9]{64}$/.test(n)).sort()){
    const directory=path.join(candidateRoot,hex),recordBytes=fs.readFileSync(path.join(directory,'record.json'));
    const record=JSON.parse(recordBytes.toString('utf8')),version='sha256:'+hex;
    if(record.contentVersion!==version)throw Error('Record/directory identity mismatch: '+hex);
    if(withdrawn.has(version)){withdrawnSkipped++;continue;}
    const bytes=fs.readFileSync(path.join(directory,'module.mapnote.json'));
    if(!/^[a-f0-9]{64}$/.test(record.document_sha256)||hash(bytes)!==record.document_sha256)throw Error('Document byte hash mismatch: '+hex);
    const doc=JSON.parse(bytes.toString('utf8'));
    validateDocument(doc);
    if(!validateGenerationContract(doc).versionMatches)throw Error('Stale document contentVersion: '+hex);
    if(record.id!==doc.id||doc.generationContract.contentVersion!==version)throw Error('Record/document identity mismatch: '+hex);
    const caseName=record.cases_sha256?'cases.json':'case.json',caseHash=record.cases_sha256??record.case_sha256;
    const casePath=path.join(directory,caseName);let cases=[];
    // Only the persisted case is optional here; raw experiment evidence is not
    // read. This static exporter adds no new physics or admission claim.
    if(fs.existsSync(casePath)){
      const caseBytes=fs.readFileSync(casePath);
      if(!/^[a-f0-9]{64}$/.test(caseHash)||hash(caseBytes)!==caseHash)throw Error('Persisted case byte hash mismatch: '+hex);
      const payload=JSON.parse(caseBytes.toString('utf8'));cases=caseName==='cases.json'?payload.cases:[payload];caseHashesChecked++;
    }
    const row=curated.get(version),family=row?.family??cases[0]?.family??doc.generationContract.generation.parameters.family??'';
    let title=titles.get(version);
    if(!title&&cases[0]?.production_recipe==='refund-turnback')
      title=`空中回充返身 · 接口 ${(cases[0].rule_parameters?.interface??0)+1}`;
    if(!title&&/[\u3400-\u9fff]/u.test(doc.title))title=doc.title;
    if(!title&&familyNames[family]){
      const n=(adaptationNumbers.get(family)??0)+1;adaptationNumbers.set(family,n);
      title=`${familyNames[family]} · 适配 ${n}`;
    }
    title??=doc.title;
    const entry=repositoryEntry(record,doc,row??{},{title});
    entry.category=doc.source?.category||'平原';entry.scope=scope(row);
    entry.tags=[...new Set([doc.generationContract.kind,family,SCOPE_NAMES[entry.scope]].filter(Boolean))];
    entry.recordSha256=hash(recordBytes);
    modules.push(entry);
    files.set('modules/'+hex+'.json',bytes); // Preserve the exact original bytes.
    files.set('thumbnails/'+hex+'.svg',Buffer.from(renderContractSvg(doc)));
  }
  modules.sort((a,b)=>a.title.localeCompare(b.title,'zh-CN')||a.id.localeCompare(b.id));
  const catalog=validateRepositoryCatalog({schema:'map-notes/repository-module-library/v1',repository:'zhipijun1996/map-edit',updateRef:'content/task-a-workshop',sourceCommit,modules});
  files.set('catalog.json',json(catalog));
  const expectedModules=new Set(modules.map(m=>m.contentVersion.slice(7)+'.json'));
  const expectedThumbnails=new Set(modules.map(m=>m.contentVersion.slice(7)+'.svg'));
  const stale=[...managedFiles(path.join(output,'modules'),'.json').filter(n=>!expectedModules.has(n)).map(n=>'modules/'+n),...managedFiles(path.join(output,'thumbnails'),'.svg').filter(n=>!expectedThumbnails.has(n)).map(n=>'thumbnails/'+n)];
  if(check){
    const conflicts=[];
    for(const [name,bytes]of files){
      const target=path.join(output,name);
      if(!fs.existsSync(target)||!fs.readFileSync(target).equals(bytes))conflicts.push(name);
    }
    conflicts.push(...stale);
    if(conflicts.length)throw Error('Generated repository library differs from sources: '+conflicts.join(', '));
  }else{
    for(const [name,bytes]of files){
      const target=path.join(output,name);fs.mkdirSync(path.dirname(target),{recursive:true});
      if(!fs.existsSync(target)||!fs.readFileSync(target).equals(bytes))fs.writeFileSync(target,bytes);
    }
    for(const name of stale){
      if(!/^(modules\/[a-f0-9]{64}\.json|thumbnails\/[a-f0-9]{64}\.svg)$/.test(name))throw Error('Unexpected unmanaged output file: '+name);
      fs.unlinkSync(path.join(output,name));
    }
  }
  const counts=modules.reduce((out,m)=>(out[m.scope]=(out[m.scope]??0)+1,out),{});
  console.log(JSON.stringify({mode:check?'check':'build',modules:modules.length,scopes:counts,caseHashesChecked,withdrawnSkipped,sourceCommit,output:'library/workshop/catalog.json',sourceFilesChanged:false,newPhysicsCases:0}));
}
try{main();}catch(error){console.error('Repository library '+(check?'check':'build')+' failed: '+error.message);process.exitCode=1;}
