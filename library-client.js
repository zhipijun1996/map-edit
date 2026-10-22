import {validateRequirements} from './capabilities.js';
// Public reads only. A GitHub Pages page never contains a GitHub write token.
export const GAME_REPO='zhipijun1996/gunman-rush';
export const EDITOR_REPO='zhipijun1996/map-edit';
export const SYNC_WORKFLOW='https://github.com/'+EDITOR_REPO+'/actions/workflows/sync-library.yml';
const SHA=/^[a-f0-9]{40}$/;
export function validateCatalog(data){
  if(!data||![1,2].includes(data.schema)||!SHA.test(data.sourceCommit)||!Array.isArray(data.modules)||data.modules.length>10000)throw Error('模块库格式不兼容，保留当前库');
  const ids=new Set();
  for(const m of data.modules){
    if(!m||typeof m.id!=='string'||ids.has(m.id)||typeof m.title!=='string'||typeof m.category!=='string'||!/^\.\/library\/modules\/[a-zA-Z0-9_-]+\.json$/.test(m.file)||!/^\.\/library\/thumbnails\/[a-zA-Z0-9_-]+\.svg$/.test(m.thumbnail)||!/^[a-f0-9]{64}$/.test(m.contentSha256))throw Error('模块目录校验失败，保留当前库');
    validateRequirements(m.capabilityRequirements);
    ids.add(m.id);
  }
  return data;
}
export class LibraryClient{
  constructor(baseURL,fetcher=globalThis.fetch.bind(globalThis)){
    this.baseURL=new URL('.',baseURL).href;this.fetcher=fetcher;this.catalog=null;
  }
  async json(url){
    const r=await this.fetcher(url,{cache:'no-store',signal:AbortSignal.timeout(20000)});
    if(!r.ok)throw Error(r.status===403||r.status===429?'GitHub 请求限额已到，请稍后重试':`读取失败（HTTP ${r.status}）`);
    return r.json();
  }
  async load(){
    if(!this.catalog)this.catalog=validateCatalog(await this.json(new URL('library/catalog.json',this.baseURL).href));
    return this.catalog;
  }
  url(relative){return new URL(relative,this.baseURL).href;}
  async module(entry){
    const r=await this.fetcher(this.url(entry.file),{cache:'no-store',signal:AbortSignal.timeout(20000)});
    if(!r.ok)throw Error('模块文件暂时无法读取，请重试');
    const bytes=await r.arrayBuffer();
    const digest=await crypto.subtle.digest('SHA-256',bytes);
    const hash=Array.from(new Uint8Array(digest),b=>b.toString(16).padStart(2,'0')).join('');
    if(hash!==entry.contentSha256)throw Error('模块版本与目录不一致，请先更新模块库');
    return JSON.parse(new TextDecoder().decode(bytes));
  }
  async checkUpdate(){
    await this.load();
    const [game,editor]=await Promise.all([
      this.json(`https://api.github.com/repos/${GAME_REPO}/commits/main`),
      this.json(`https://api.github.com/repos/${EDITOR_REPO}/commits/main`)
    ]);
    if(!SHA.test(game.sha)||!SHA.test(editor.sha))throw Error('GitHub 版本信息无效');
    // Pin both catalog and module reads to one editor commit, never mixed main files.
    const base=`https://raw.githubusercontent.com/${EDITOR_REPO}/${editor.sha}/`;
    const candidate=validateCatalog(await this.json(base+'library/catalog.json'));
    const previous=this.catalog.sourceCommit;
    this.catalog=candidate;this.baseURL=base;
    return {current:candidate.sourceCommit,latest:game.sha,isLatest:candidate.sourceCommit===game.sha,changed:previous!==candidate.sourceCommit,editorCommit:editor.sha};
  }
  async syncRun(){
    const data=await this.json(`https://api.github.com/repos/${EDITOR_REPO}/actions/workflows/sync-library.yml/runs?per_page=1`);
    const r=data.workflow_runs?.[0];return r?{status:r.status,conclusion:r.conclusion,url:r.html_url}:null;
  }
}
