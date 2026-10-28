import {validateDocument} from './model.js';
import {validateGenerationContract} from './module-contract.js';

export const CORNER_BATCH_PATH='modules/corner-batch-status.json';
const HASH=/^[a-f0-9]{64}$/;
export const CORNER_STAGE_LABELS={
  not_started:'待适配',prepared:'已适配 · 待实测',tooling_gap:'适配待修',
  preflight_passed:'预检通过 · 待质量验证',preflight_failed:'预检失败',
  quality_failed:'质量验证未通过',holdout_pool_locked:'留出条件待处理',
  native_failed:'原生加载未通过',verified:'已认证',
  verified_pending_index:'验证通过 · 待更新目录',verification_pending:'认证回执待核对',quality_passed:'质量通过 · 待原生加载',
};
export function stageLabel(status){return CORNER_STAGE_LABELS[status]??'待核对';}
function matches(entry,row){return entry.id===row.moduleId&&entry.contentVersion===row.baseContentVersion&&entry.contentSha256===row.baseDocumentSha256;}
export function checkedCornerBatch(data,catalog){
  if(data?.schema!=='map-notes/corner-batch-status/v1'||!Array.isArray(data.rows)||!Array.isArray(data.modules)||data.rows.length>10000)throw Error('换边进度格式不兼容');
  const entries=new Map(catalog.modules.map(e=>[e.id,e]));
  for(const row of data.rows){
    if(!row||typeof row.key!=='string'||typeof row.moduleId!=='string'||typeof row.portId!=='string'||!['TOP_LEFT','TOP_RIGHT','BOTTOM_LEFT','BOTTOM_RIGHT'].includes(row.corner)||typeof row.status!=='string'||!HASH.test(row.baseDocumentSha256))throw Error('换边进度条目无效');
    if(row.preview&&(!HASH.test(row.preview.sha256)||row.preview.certified!==false||!/^generation\/module-review\/corner-batches\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+\.mapnote\.json$/.test(row.preview.path)))throw Error('换边审阅文件路径无效');
  }
  // An old batch cannot describe a revised current Module.
  const rows=data.rows.filter(row=>entries.has(row.moduleId)&&matches(entries.get(row.moduleId),row));
  const counts=rows.reduce((result,r)=>(result[r.status]=(result[r.status]??0)+1,result),Object.create(null));
  return {...data,rows,counts,currentOptions:rows.length,modules:data.modules.filter(m=>{const e=entries.get(m.id);return e&&m.contentVersion===e.contentVersion&&m.documentSha256===e.contentSha256;}),staleOptionsOmitted:(data.staleOptionsOmitted??0)+data.rows.length-rows.length};
}
async function sha(bytes){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');}
export async function loadCornerBatch(baseURL,catalog,fetcher=globalThis.fetch.bind(globalThis)){
  const response=await fetcher(new URL(CORNER_BATCH_PATH,baseURL),{cache:'no-store',signal:AbortSignal.timeout(15000)});
  if(response.status===404)return null;
  if(!response.ok)throw Error('换边进度暂时无法读取');
  return checkedCornerBatch(await response.json(),catalog);
}
export function moduleCornerProgress(data,entry){
  const rows=(data?.rows??[]).filter(row=>matches(entry,row));
  return {rows,counts:rows.reduce((counts,r)=>(counts[r.status]=(counts[r.status]??0)+1,counts),Object.create(null)),
    certified:entry.cornerConfigurationReceipts?.length??0,
    mirrorStatus:data?.modules.find(m=>m.id===entry.id)?.mirrorStatus??'UNKNOWN'};
}
export async function loadCornerPreview(row,entry,baseURL,fetcher=globalThis.fetch.bind(globalThis)){
  if(!matches(entry,row)||!row.preview||row.preview.certified!==false)throw Error('此版本没有可审阅的冻结换边草案');
  const artifact=row.preview;
  if(!/^generation\/module-review\/corner-batches\/[a-zA-Z0-9_-]+\/[a-zA-Z0-9_-]+\.mapnote\.json$/.test(artifact.path))throw Error('换边审阅文件路径无效');
  const response=await fetcher(new URL(artifact.path,baseURL),{cache:'no-store',signal:AbortSignal.timeout(20000)});
  if(!response.ok)throw Error('换边审阅文件暂未发布');
  const bytes=await response.arrayBuffer();if(await sha(bytes)!==artifact.sha256)throw Error('冻结换边草案SHA不匹配');
  const doc=validateDocument(JSON.parse(new TextDecoder().decode(bytes)));
  if(doc.id!==entry.moduleId||doc.generationContract?.contentVersion!==artifact.contentVersion||!validateGenerationContract(doc).versionMatches)throw Error('冻结换边草案版本不匹配');
  return doc;
}
