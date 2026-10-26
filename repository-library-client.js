import {validateRequirements} from './capabilities.js';
import {validateDifficulty} from './difficulty.js';
import {LibraryClient,EDITOR_REPO} from './library-client.js';
import {validateDocument} from './model.js';
import {validateGenerationContract} from './module-contract.js';
import {renderContractSvg} from './module-contract-render.js';

export const REPOSITORY_MODULES_REF='content/task-a-workshop';
const HASH=/^[a-f0-9]{64}$/,SHA=/^[a-f0-9]{40}$/;
const ROOT='pcg/map_directed/library/candidates/';
export const SCOPE_NAMES={plains:'反冲平原候选',advanced:'后续能力储备',held:'节奏暂扣',unclassified:'待整理'};
export function repositoryEntry(record,doc,row={},previous={}){
  const version=record.contentVersion,hex=version?.replace(/^sha256:/,'');
  if(!HASH.test(hex)||doc.id!==record.id||doc.generationContract?.contentVersion!==version)throw Error('仓库模块身份与版本不一致');
  const requirements=doc.capabilityRequirements;
  const caps=[...(requirements?.allOf??[]),...(requirements?.anyOfGroups??[]).flat()];
  const advanced=caps.some(c=>['grapple','wall_climb','double_jump'].includes(c));
  const scope=row.selected_for_plains_candidates?'plains':row.selection_reason==='reserved_for_later_abilities'?'advanced':row.selection_reason==='pacing_held'?'held':advanced?'advanced':'unclassified';
  return {id:'repo-'+hex,moduleId:doc.id,contentVersion:version,title:previous.title??row.title??doc.title,portCount:doc.generationContract.ports.length,category:doc.source?.category??'平原',collection:'本仓库内容',file:`./library/workshop/modules/${hex}.json`,thumbnail:`./library/workshop/thumbnails/${hex}.svg`,sourcePath:ROOT+hex+'/module.mapnote.json',recordPath:ROOT+hex+'/record.json',contentSha256:record.document_sha256,objectCount:doc.objects.length,capabilityRequirements:requirements,difficulty:doc.difficulty,integration:doc.source?.integration,scope,contentRole:row.content_role??'UNKNOWN',tags:[doc.generationContract.kind,row.family??doc.generationContract.generation?.parameters?.family??'',SCOPE_NAMES[scope]]};
}
export function validateRepositoryCatalog(data){
  if(data?.schema!=='map-notes/repository-module-library/v1'||data.repository!==EDITOR_REPO||!SHA.test(data.sourceCommit)||typeof data.updateRef!=='string'||!data.updateRef||data.updateRef.length>200||!Array.isArray(data.modules)||data.modules.length>10000)throw Error('本仓库模块目录格式无效，保留现有库');
  const ids=new Set();
  for(const m of data.modules){
    const hex=m.contentVersion?.replace(/^sha256:/,'');
    if(!HASH.test(hex)||m.id!=='repo-'+hex||ids.has(m.id)||typeof m.moduleId!=='string'||typeof m.title!=='string'||!HASH.test(m.contentSha256)||m.file!==`./library/workshop/modules/${hex}.json`||m.thumbnail!==`./library/workshop/thumbnails/${hex}.svg`||m.sourcePath!==ROOT+hex+'/module.mapnote.json'||m.recordPath!==ROOT+hex+'/record.json'||!Object.hasOwn(SCOPE_NAMES,m.scope))throw Error('本仓库模块条目校验失败，保留现有库');
    if(m.portCount!==undefined&&(!Number.isInteger(m.portCount)||m.portCount<2))throw Error('模块端口数量无效');
    if(typeof m.category!=='string')throw Error('模块分类无效');
    validateRequirements(m.capabilityRequirements);validateDifficulty(m.difficulty);
    ids.add(m.id);
  }
  return data;
}
async function sha(bytes){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),b=>b.toString(16).padStart(2,'0')).join('');}
function checkedDocument(doc,entry){
  const value=validateDocument(doc);
  if(value.id!==entry.moduleId||value.generationContract?.contentVersion!==entry.contentVersion||!validateGenerationContract(value).versionMatches)throw Error('模块内容与版本不一致，保留现有库');
  return value;
}
async function concurrent(items,fn){
  let index=0;const result=new Array(items.length);
  await Promise.all(Array.from({length:Math.min(6,items.length)},async()=>{while(index<items.length){const i=index++;result[i]=await fn(items[i],i);}}));
  return result;
}
export class RepositoryLibraryClient extends LibraryClient{
  constructor(baseURL,fetcher=globalThis.fetch.bind(globalThis)){
    super(baseURL,fetcher);this.documents=new Map();this.thumbnailURLs=new Map();this.updatePromise=null;
  }
  async load(){
    if(!this.catalog)this.catalog=validateRepositoryCatalog(await this.json(this.url('library/workshop/catalog.json')));
    return this.catalog;
  }
  async module(entry){
    const cached=this.documents.get(entry.contentVersion);
    if(cached?.hash===entry.contentSha256)return structuredClone(cached.doc);
    const value=checkedDocument(await super.module(entry),entry);
    this.documents.set(entry.contentVersion,{doc:value,hash:entry.contentSha256});return structuredClone(value);
  }
  thumbnail(entry){
    const cached=this.documents.get(entry.contentVersion);
    if(!cached)return this.url(entry.thumbnail);
    if(!this.thumbnailURLs.has(entry.contentVersion))this.thumbnailURLs.set(entry.contentVersion,URL.createObjectURL(new Blob([renderContractSvg(cached.doc)],{type:'image/svg+xml'})));
    return this.thumbnailURLs.get(entry.contentVersion);
  }
  async responseJSON(url,optional=false){
    const r=await this.fetcher(url,{cache:'no-store',signal:AbortSignal.timeout(20000)});
    if(optional&&r.status===404)return null;
    if(!r.ok)throw Error(r.status===403||r.status===429?'GitHub 请求限额已到，请稍后重试':`读取失败（HTTP ${r.status}）`);
    return r.json();
  }
  checkUpdate(progress=()=>{}){
    if(!this.updatePromise)this.updatePromise=this.refresh(progress).finally(()=>{this.updatePromise=null;});
    return this.updatePromise;
  }
  async refresh(progress){
    const previous=this.catalog;
    const ref=previous?.updateRef??REPOSITORY_MODULES_REF;
    let tip=await this.responseJSON(`https://api.github.com/repos/${EDITOR_REPO}/commits/${encodeURIComponent(ref)}`,true);
    let activeRef=ref;
    if(!tip&&ref!=='main'){activeRef='main';tip=await this.responseJSON(`https://api.github.com/repos/${EDITOR_REPO}/commits/main`);}
    if(!SHA.test(tip?.sha))throw Error('无法确认仓库版本，保留现有库');
    const base=`https://raw.githubusercontent.com/${EDITOR_REPO}/${tip.sha}/`;
    const tree=await this.json(`https://api.github.com/repos/${EDITOR_REPO}/git/trees/${tip.sha}?recursive=1`);
    if(tree.truncated||!Array.isArray(tree.tree))throw Error('仓库目录不完整，保留现有库');
    const sources=tree.tree.filter(x=>x.type==='blob'&&/^pcg\/map_directed\/library\/candidates\/[a-f0-9]{64}\/record\.json$/.test(x.path));
    if(!sources.length&&previous?.modules.length)throw Error('该版本尚未发布仓库模块，保留现有库');
    if(sources.length>10000)throw Error('仓库模块数量超过支持范围');
    const notices=await concurrent(tree.tree.filter(x=>x.type==='blob'&&/^pcg\/feedback\/content-withdrawals\/[a-zA-Z0-9_-]+\.json$/.test(x.path)),x=>this.json(base+x.path));
    const withdrawn=new Set();
    for(const n of notices){if(n.schema!=='pcg/content-technical-withdrawal/v1'||!Array.isArray(n.contentVersions))throw Error('撤回记录格式无效，保留现有库');for(const v of n.contentVersions)withdrawn.add(v);}
    const view=await this.responseJSON(base+'generation/workshop/plains-recoil-current/catalog.json',true)
      ?? await this.responseJSON(base+'generation/workshop/plains-recoil-v1/catalog.json',true);
    const curated=new Map((view?.rows??[]).map(x=>[x.contentVersion,x]));
    const old=new Map((previous?.modules??[]).map(x=>[x.contentVersion,x]));const docs=new Map();let completed=0,active=true;
    let entries;
    try{entries=await concurrent(sources,async source=>{
      const record=await this.json(base+source.path),hex=source.path.split('/').at(-2),version='sha256:'+hex;
      if(record.contentVersion!==version||!HASH.test(record.document_sha256))throw Error('仓库模块索引与版本不一致');
      if(withdrawn.has(version))return null;
      const prior=old.get(version);let doc;const cached=this.documents.get(version);
      if(cached?.hash===record.document_sha256)doc=cached.doc;
      else{
        const response=await this.fetcher(base+ROOT+hex+'/module.mapnote.json',{cache:'no-store',signal:AbortSignal.timeout(20000)});
        if(!response.ok)throw Error(`模块下载失败（HTTP ${response.status}）`);
        const bytes=await response.arrayBuffer();if(await sha(bytes)!==record.document_sha256)throw Error('模块文件校验失败，保留现有库');
        doc=JSON.parse(new TextDecoder().decode(bytes));
      }
      const entry=repositoryEntry(record,doc,curated.get(version),prior);
      doc=checkedDocument(doc,entry);docs.set(version,{doc,hash:entry.contentSha256});
      if(active)progress(++completed,sources.length);return entry;
    });}catch(e){active=false;throw e;}
    const next=validateRepositoryCatalog({schema:'map-notes/repository-module-library/v1',repository:EDITOR_REPO,updateRef:activeRef,sourceCommit:tip.sha,modules:entries.filter(Boolean).sort((a,b)=>a.title.localeCompare(b.title,'zh-CN')||a.id.localeCompare(b.id))});
    const versions=new Set(next.modules.map(x=>x.contentVersion));
    if(activeRef!==ref&&previous?.modules.some(x=>!versions.has(x.contentVersion)&&!withdrawn.has(x.contentVersion)))throw Error('主分支尚未包含完整仓库模块，保留现有库');
    const added=next.modules.filter(x=>!old.has(x.contentVersion)).length,removed=[...old.keys()].filter(x=>!versions.has(x)).length;
    // Publish all files and the pinned URL together, only after validation.
    for(const [version,url]of this.thumbnailURLs)if(!versions.has(version)){URL.revokeObjectURL(url);this.thumbnailURLs.delete(version);}
    this.documents=docs;this.baseURL=base;this.catalog=next;
    return {added,removed,total:next.modules.length,editorCommit:tip.sha};
  }
}
