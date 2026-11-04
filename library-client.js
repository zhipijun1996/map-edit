// Shared public fetch helpers. The only production library is modules/catalog.json.
export const EDITOR_REPO='zhipijun1996/map-edit';
export class LibraryClient{
  constructor(baseURL,fetcher=globalThis.fetch.bind(globalThis)){
    this.baseURL=new URL('.',baseURL).href;this.fetcher=fetcher;this.catalog=null;
  }
  async json(url){
    const r=await this.fetcher(url,{cache:'no-store',signal:AbortSignal.timeout(20000)});
    if(!r.ok)throw Error(r.status===403||r.status===429?'GitHub 请求限额已到，请稍后重试':`读取失败（HTTP ${r.status}）`);
    return r.json();
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
}
