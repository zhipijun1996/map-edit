import {LibraryClient,EDITOR_REPO} from './library-client.js';
import {validateRequirements} from './capabilities.js';
import {validateDifficulty} from './difficulty.js';
import {validateDocument} from './model.js';
import {validateGenerationContract,canonical} from './module-contract.js';
import {renderContractSvg} from './module-contract-render.js';

export const CURRENT_MODULES_REF='main';
export const CURRENT_CATALOG_PATH='modules/catalog.json';
export const CORNER_ASSESSMENT_PATH='pcg/migration/foundation-v1/corner-port-inventory-v1.json';
const SHA=/^[a-f0-9]{40}$/,HASH=/^[a-f0-9]{64}$/,ID=/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,159}$/;

export function validateCurrentModuleCatalog(data){
  if(data?.schema!=='map-notes/module-archive/v1'||data.foundationVersion!=='1.0'||data.updateRef!=='main'||!Array.isArray(data.modules)||data.modules.length>10000)throw Error('当前 Module 目录格式不兼容，保留现有库');
  if(data.sourceCommit!==undefined&&!SHA.test(data.sourceCommit))throw Error('当前 Module 目录来源版本无效');
  const ids=new Set(),moduleIds=new Set();
  for(const m of data.modules){
    if(!m||typeof m.id!=='string'||!ID.test(m.id)||ids.has(m.id)||typeof m.moduleId!=='string'||!m.moduleId||moduleIds.has(m.moduleId)||typeof m.title!=='string'||typeof m.category!=='string'||!/^sha256:[a-f0-9]{64}$/.test(m.contentVersion)||!HASH.test(m.contentSha256)||m.file!==`./modules/${m.id}/module.mapnote.json`||m.thumbnail!==`./modules/${m.id}/thumbnail.svg`||!Number.isInteger(m.portCount)||m.portCount<1||typeof m.humanReview!=='string'||!['passed_scoped','needs_validation'].includes(m.technicalStatus)||typeof m.mapReady!=='boolean')throw Error('当前 Module 条目校验失败，保留现有库');
    validateRequirements(m.capabilityRequirements);validateDifficulty(m.difficulty);
    if(m.cornerConfigurationReceipts!==undefined&&(!Array.isArray(m.cornerConfigurationReceipts)||m.cornerConfigurationReceipts.some(a=>!a||!HASH.test(a.sha256)||typeof a.path!=='string'||!a.path.replace(/^\.\//,'').startsWith(`modules/${m.id}/port-configurations/`)||a.path.replace(/^\.\//,'').split('/').some(p=>!p||p==='.'||p==='..')||/[?#\\]/.test(a.path))))throw Error('当前 Module 换边配置引用无效');
    ids.add(m.id);moduleIds.add(m.moduleId);
  }
  return data;
}
async function digest(bytes,algorithm='SHA-256'){
  return Array.from(new Uint8Array(await crypto.subtle.digest(algorithm,bytes)),b=>b.toString(16).padStart(2,'0')).join('');
}
export async function gitBlobSha(bytes){
  const data=new Uint8Array(bytes),header=new TextEncoder().encode(`blob ${data.length}\0`),blob=new Uint8Array(header.length+data.length);
  blob.set(header);blob.set(data,header.length);return digest(blob,'SHA-1');
}
function checkedDocument(raw,entry){
  const doc=validateDocument(raw),contract=doc.generationContract;
  if(doc.id!==entry.moduleId||contract?.version!==2||contract.contentVersion!==entry.contentVersion||!validateGenerationContract(doc).versionMatches||contract.ports.length!==entry.portCount)throw Error('当前 Module 内容与新地基目录不一致，保留现有库');
  if(canonical(doc.capabilityRequirements)!==canonical(entry.capabilityRequirements)||canonical(doc.difficulty)!==canonical(entry.difficulty))throw Error('当前 Module 能力或难度与目录不一致');
  return doc;
}
export class CurrentModuleLibraryClient extends LibraryClient{
  constructor(baseURL,fetcher=globalThis.fetch.bind(globalThis)){
    super(baseURL,fetcher);this.documents=new Map();this.snapshotCommit=null;this.updatePromise=null;this.cornerInventory=null;this.reviewPreviews=new Map();
  }
  async response(url,optional=false){
    const response=await this.fetcher(url,{cache:'no-store',signal:AbortSignal.timeout(20000)});
    if(optional&&response.status===404)return null;
    if(!response.ok)throw Error(response.status===403||response.status===429?'GitHub 请求限额已到，请稍后重试':`读取失败（HTTP ${response.status}）`);
    return response;
  }
  async load(){
    if(!this.catalog){
      const response=await this.response(this.url(CURRENT_CATALOG_PATH),true);
      if(!response){const error=Error('当前新地基 Module 目录尚未发布；请从仓库更新新版，已有草稿保留');error.code='CURRENT_CATALOG_MISSING';throw error;}
      this.catalog=validateCurrentModuleCatalog(await response.json());
    }
    return this.catalog;
  }
  async readDocument(entry,baseURL=this.baseURL){
    const cached=this.documents.get(entry.contentVersion);
    if(cached?.hash===entry.contentSha256)return checkedDocument(cached.doc,entry);
    const response=await this.response(new URL(entry.file,baseURL).href),bytes=await response.arrayBuffer();
    if(await digest(bytes)!==entry.contentSha256)throw Error('当前 Module 文件 SHA256 不一致，保留现有库');
    return checkedDocument(JSON.parse(new TextDecoder().decode(bytes)),entry);
  }
  async module(entry){
    const doc=await this.readDocument(entry);this.documents.set(entry.contentVersion,{doc,hash:entry.contentSha256});return structuredClone(doc);
  }
  thumbnail(entry){return this.url(entry.thumbnail);}
  reviewThumbnail(entry){
    const key=entry.contentVersion+':'+entry.contentSha256;
    if(!this.reviewPreviews.has(key)){
      const pending=this.module(entry).then(doc=>URL.createObjectURL(new Blob([renderContractSvg(doc,{review:true})],{type:'image/svg+xml'})));
      this.reviewPreviews.set(key,pending);pending.catch(()=>this.reviewPreviews.delete(key));
    }
    return this.reviewPreviews.get(key);
  }
  displayCategory(entry){
    const source=this.documents.get(entry.contentVersion)?.doc?.source;
    if(typeof source?.category==='string'&&source.category.trim())return source.category;
    if(source?.kind==='forest')return '森林';
    if(source?.kind==='foundry')return '工坊组合';
    return entry.category;
  }
  async cornerAssessment(entry){
    // Alternative interfaces are read from the current document/configuration receipts only.
    return null;
  }
  configurationPath(path,entry){
    const clean=typeof path==='string'?path.replace(/^\.\//,''):'';
    if(!clean.startsWith(`modules/${entry.id}/port-configurations/`)||clean.split('/').some(p=>!p||p==='.'||p==='..')||/[%?#\\]/.test(clean))throw Error('角落 Port 配置路径无效');
    return clean;
  }
  async configurationArtifact(artifact,entry){
    if(!artifact||!HASH.test(artifact.sha256))throw Error('角落 Port 配置缺少文件校验');
    const response=await this.response(this.url(this.configurationPath(artifact.path,entry))),bytes=await response.arrayBuffer();
    if(await digest(bytes)!==artifact.sha256)throw Error('角落 Port 配置 SHA256 不一致');
    return JSON.parse(new TextDecoder().decode(bytes));
  }
  async cornerConfigurations(entry){
    // Only catalog-listed receipts are considered; never discover candidates.
    const receipts=[];
    for(const ref of entry.cornerConfigurationReceipts??[]){
      try{
        const receipt=await this.configurationArtifact(ref,entry);
        if(!['pcg/corner-port-configuration/v1','pcg/corner-port-configuration/v2'].includes(receipt.schema)||receipt.moduleId!==entry.id||receipt.baseContentVersion!==entry.contentVersion||receipt.baseDocumentSha256!==entry.contentSha256||receipt.allowed!==true||receipt.technicalStatus!=='verified'||!Array.isArray(receipt.relocations)||!receipt.relocations.length)continue;
        const selected=new Set();
        let valid=true;
        for(const r of receipt.relocations){
          if(!r||typeof r.portId!=='string'||!r.portId||selected.has(r.portId)||!['TOP_LEFT','TOP_RIGHT','BOTTOM_LEFT','BOTTOM_RIGHT'].includes(r.corner)){valid=false;break;}
          selected.add(r.portId);
        }
        if(!valid)continue;
        this.configurationPath(receipt.configuration?.path,entry);this.configurationPath(receipt.package?.path,entry);
        if(!HASH.test(receipt.configuration?.sha256)||!HASH.test(receipt.package?.sha256)||!HASH.test(receipt.physicsReport?.sha256))continue;
        if(receipt.schema==='pcg/corner-port-configuration/v2'){
          if(receipt.retiredSidePolicy!=='preserve_geometry_no_extra_closure'||receipt.retiredOpeningReport!==undefined||!HASH.test(receipt.adaptation?.sha256))continue;
          this.configurationPath(receipt.adaptation?.path,entry);
        }
        receipts.push(receipt);
      }catch{/* A failed optional configuration never replaces the valid base. */}
    }
    return receipts;
  }
  async cornerModule(entry,receipt){
    if(receipt.baseContentVersion!==entry.contentVersion||receipt.baseDocumentSha256!==entry.contentSha256)throw Error('角落 Port 配置来源版本已变化');
    const doc=await this.configurationArtifact(receipt.configuration,entry);
    const checked=checkedDocument(doc,{...entry,contentSha256:receipt.configuration.sha256,contentVersion:receipt.configuration.contentVersion});
    const manifest=await this.configurationArtifact(receipt.package,entry);
    if(manifest.schema!=='pcg/godot-module-package/v1'||manifest.stable_id!==entry.id||manifest.source?.module_sha256!==receipt.configuration.sha256)throw Error('角落 Port 编译包与配置内容不一致');
    if(receipt.schema==='pcg/corner-port-configuration/v2'){
      const adaptation=await this.configurationArtifact(receipt.adaptation,entry);
      if(adaptation.schema!=='pcg/corner-interface-adaptation/v2'||adaptation.retiredSidePolicy!=='preserve_geometry_no_extra_closure'||adaptation.baseDocumentSha256!==entry.contentSha256||adaptation.targetDocumentSha256!==receipt.configuration.sha256)throw Error('角落 Port 适配证据与配置内容不一致');
    }
    return structuredClone(checked);
  }
  checkUpdate(progress=()=>{}){
    if(!this.updatePromise)this.updatePromise=this.refresh(progress).finally(()=>{this.updatePromise=null;});
    return this.updatePromise;
  }
  async refresh(progress){
    // The directory is authoritative. Never discover formal modules by scanning historical candidates.
    const tip=await this.json(`https://api.github.com/repos/${EDITOR_REPO}/commits/${encodeURIComponent(CURRENT_MODULES_REF)}`);
    if(!SHA.test(tip?.sha))throw Error('无法确认当前 Module 仓库版本');
    const base=`https://raw.githubusercontent.com/${EDITOR_REPO}/${tip.sha}/`;
    const infoResponse=await this.response(`https://api.github.com/repos/${EDITOR_REPO}/contents/${CURRENT_CATALOG_PATH}?ref=${tip.sha}`,true);
    if(!infoResponse)throw Error('该仓库版本尚无当前新地基目录；保留现有库，旧候选不会自动转为当前库');
    const info=await infoResponse.json();
    if(info.type!=='file'||info.path!==CURRENT_CATALOG_PATH||!SHA.test(info.sha))throw Error('当前 Module 目录的 Git 身份无效');
    const response=await this.response(base+CURRENT_CATALOG_PATH),bytes=await response.arrayBuffer();
    if(await gitBlobSha(bytes)!==info.sha)throw Error('当前 Module 目录 Git SHA 校验失败，保留现有库');
    const next=validateCurrentModuleCatalog(JSON.parse(new TextDecoder().decode(bytes))),documents=new Map();
    let cursor=0,completed=0,active=true;
    try{
      await Promise.all(Array.from({length:Math.min(6,next.modules.length)},async()=>{
        while(active&&cursor<next.modules.length){const entry=next.modules[cursor++],doc=await this.readDocument(entry,base);documents.set(entry.contentVersion,{doc,hash:entry.contentSha256});if(active)progress(++completed,next.modules.length);}
      }));
    }catch(error){active=false;throw error;}
    const old=new Map((this.catalog?.modules??[]).map(m=>[m.id,m.contentVersion])),ids=new Set(next.modules.map(m=>m.id));
    const added=next.modules.filter(m=>!old.has(m.id)).length,changed=next.modules.filter(m=>old.has(m.id)&&old.get(m.id)!==m.contentVersion).length,removed=[...old.keys()].filter(id=>!ids.has(id)).length;
    // Install the complete verified snapshot atomically; a failed refresh never replaces the old catalog/cache.
    for(const pending of this.reviewPreviews.values())pending.then(url=>URL.revokeObjectURL(url)).catch(()=>{});
    this.reviewPreviews.clear();this.documents=documents;this.catalog=next;this.baseURL=base;this.snapshotCommit=tip.sha;this.cornerInventory=null;
    return {added,changed,removed,total:next.modules.length,editorCommit:tip.sha,catalogGitSha:info.sha};
  }
}
