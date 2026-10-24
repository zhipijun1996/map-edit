import {validateGenerationContract} from './module-contract.js';
import {DIFFICULTY_LEVELS,validateDifficulty,difficultySummary,difficultyChanges} from './difficulty.js';
import {ABILITIES,abilityName,emptyRequirements,requirementSummary} from './capabilities.js';
import {TYPES,SCHEMA,uid,clone,createObject,blankDocument,exampleDocument,validateDocument,pathPoint,progressAt,translateObject,objectBounds,makeRevision,objectChanges,changeRequest} from './model.js';
import {LibraryClient,SYNC_WORKFLOW} from './library-client.js';
const $=s=>document.querySelector(s), svg=$('#canvas'), NS='http://www.w3.org/2000/svg';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>Math.round(n*100)/100;
const STORE='map-notes-v1';
let saved={documents:[],activeId:null};
try{const raw=JSON.parse(localStorage.getItem(STORE));if(raw&&Array.isArray(raw.documents)){saved.documents=raw.documents.flatMap(d=>{try{return [validateDocument(d)];}catch{return [];}});saved.activeId=raw.activeId;}}catch{ /* A malformed draft must not prevent opening the editor. */ }
let doc=clone(saved.documents.find(d=>d.id===saved.activeId)??saved.documents[0]??exampleDocument());
let selected=null,tool='select',undo=[],redo=[],gesture=null,pointers=new Map(),drawing=null,playing=false,time=0,lastFrame=0,saveTimer=null,toastTimer;
let camera={x:0,y:0,w:1600,h:900},lastPanTool='select',libraryData=null,routeView='all';
const libraryClient=new LibraryClient(location.href);
let lastLibraryCheck=null;
function toast(message){$('#toast').textContent=message;$('#toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('#toast').hidden=true,3200);}
function snapshot(){undo.push(clone(doc));if(undo.length>80)undo.shift();redo=[];updateHistory();}
function persist(){
  doc.updatedAt=new Date().toISOString();saved.activeId=doc.id;
  const safe=clone(doc);safe.objects=safe.objects.filter(o=>!o.points||o.points.length>=2);
  const i=saved.documents.findIndex(d=>d.id===doc.id);if(i<0)saved.documents.push(safe);else saved.documents[i]=safe;
  try{localStorage.setItem(STORE,JSON.stringify(saved));$('#save-status').textContent='已自动保存到本机';}catch{$('#save-status').textContent='本机保存空间不足，请保存工程';}
}
function changed({inspector=false}={}){clearTimeout(saveTimer);$('#save-status').textContent='正在保存…';saveTimer=setTimeout(persist,250);render();if(inspector)renderInspector();renderRevisionInfo();updateHistory();}
function current(){return doc.objects.find(o=>o.id===selected);}
function updateHistory(){$('#undo').disabled=!undo.length;$('#redo').disabled=!redo.length;$('#delete').disabled=!selected;$('#duplicate').disabled=!selected;}
function loadDocument(d){if(drawing)finishDrawing();persist();doc=clone(d);selected=null;undo=[];redo=[];time=0;playing=false;$('#time').value=0;$('#play').textContent='▶ 演示';syncFields();setTool('select');fit();persist();}
function syncFields(){$('#title').value=doc.title;$('#description').value=doc.description;$('#constraints').value=doc.constraints;routeView=doc.objects.find(o=>o.type==='route'&&o.sourceRoute==='main')?.id??doc.objects.find(o=>o.type==='route')?.id??'all';renderInspector();renderRevisionInfo();renderCapabilities();renderDifficulty();updateHistory();updateRouteOptions();}
function integrationBadge(status){return `<span class="integration-badge ${esc(status?.usage??'unverified')}">${esc(status?.label??'接入状态待核实')}</span>`;}
function renderRevisionInfo(){
  const s=doc.source,op=doc.intent?.operation??(s?'modify_existing':'new_module'),changes=objectChanges(doc);
  let html=`<div class="revision-card"><label class="field">本次用途<select id="revision-operation">${s?option('modify_existing','修改原模块',op)+option('new_variant','基于它新增变体',op):option('new_module','新增模块',op)}</select></label>`;
  if(s){
    const latest=libraryClient.catalog?.modules.find(m=>m.id===s.moduleId)?.integration;
    const status=s.integration??(latest?.checkedCommit===s.commit?latest:null);
    html+=`<div class="revision-source">原模块：<b>${esc(s.moduleId)}</b><br>${integrationBadge(status)}<p>${esc(status?.reason??'此旧草稿尚无接入审查信息，可从模块库查看最新版。')}</p><span>来源版本 ${esc(s.commit?.slice(0,8))}</span></div>`;
    const latestCommit=libraryClient.catalog?.sourceCommit;
    if(latestCommit&&latestCommit!==s.commit)html+='<p class="revision-warning">参考库已有新版本。本草稿保留旧基线，应用前需对比最新源码。</p>';
    if(status?.evidence?.length)html+=`<details class="integration-evidence"><summary>查看接入依据</summary>${status.evidence.map(e=>`<a href="${esc('https://github.com/zhipijun1996/gunman-rush/blob/'+status.checkedCommit+'/'+e.path+'#L'+e.line)}" target="_blank" rel="noopener">${esc(e.path.split('/').at(-1))} ↗</a>`).join('')}<p>依据是来源版本的游戏入口调用链；不表示此修改稿已应用或通过物理验证。</p></details>`;
  }
  if(op==='new_variant')html+=field('新变体建议名称（可留空）','suggestedModuleId',doc.intent?.suggestedModuleId??'');
  html+=`<p class="revision-state">${op==='modify_existing'?'保留原模块身份与引用。':op==='new_variant'?'保留原版，创建独立变体。':'创建新模块。'}本稿尚未写回游戏。</p>`;
  if(changes)html+=`<div class="change-count">新增 ${changes.added.length} · 调整 ${changes.modified.length} · 删除 ${changes.removed.length}${JSON.stringify(doc.capabilityRequirements??emptyRequirements())!==JSON.stringify(doc.baselineCapabilityRequirements??doc.source?.capabilityRequirements??emptyRequirements())?' · 能力要求已调整':''}</div>`;
  if(difficultyChanges(doc)?.changed)html+='<div class="change-count difficulty-change">难度评分已调整</div>';
  if(doc.generationContract){let current=false;try{current=validateGenerationContract(doc).versionMatches;}catch{}const c=doc.generationContract;html+=`<div class="revision-warning" data-contract-state="${current?'current':'stale'}"><b>生成契约：${current?'当前内容版本':'已变更 / 证据不可沿用'}</b><br>${esc(c.contentVersion)}<p>静态检查、物理见证与正式接入分别记录。UNKNOWN 接口不可自动拼装；编辑后需重新导出和验证。</p><p>端口 ${c.ports?.length??0} · 有向关系 ${c.relations?.length??0} · 物理记录 ${c.validations?.filter(v=>v.kind==='physics').length??0}</p></div>`;}
  html+='</div>';$('#revision-info').innerHTML=html;
  $('#revision-operation').onchange=e=>{snapshot();doc.intent={...doc.intent,operation:e.target.value};changed();};
  const input=$('#revision-info [data-prop="suggestedModuleId"]');if(input)input.onchange=()=>{snapshot();doc.intent={...doc.intent,suggestedModuleId:input.value.slice(0,100)};changed();};
}
function renderCapabilities(){
  const panel=$('#capability-panel'),wasOpen=panel.querySelector('details')?.open??false,r=doc.capabilityRequirements??emptyRequirements();
  const ids=[...new Set([...Object.keys(ABILITIES),...r.allOf,...r.anyOfGroups.flat()])];
  const choices=(selected,group)=>`<div class="ability-choices">${ids.map(id=>`<label><input type="checkbox" data-ability="${esc(id)}" data-ability-group="${group}" ${selected.includes(id)?'checked':''}>${esc(abilityName(id))}</label>`).join('')}</div>`;
  panel.innerHTML=`<details class="capability-card" ${wasOpen?'open':''}><summary>能力要求 · ${esc(requirementSummary(r))}</summary><p>全部必需的能力 + 每组任选一种。多组之间也必须同时满足。仅放置钩点不自动增加能力锁。</p><label class="field">确认状态<select id="capability-status">${option('unspecified','未填写（不等于无能力锁）',r.status)}${option('partial','已有部分要求，尚未确认完整',r.status)}${option('defined','已确认完整（全空表示无能力锁）',r.status)}</select></label><b>必须全部拥有</b>${choices(r.allOf,'all')}<div class="ability-groups">${r.anyOfGroups.map((g,i)=>`<div class="ability-group"><b>第 ${i+1} 组：任选一种</b><button data-remove-ability-group="${i}" aria-label="删除第 ${i+1} 组">删除组</button>${choices(g,i)}</div>`).join('')}</div><button id="add-ability-group">＋ 添加任选组</button><div class="custom-ability"><input id="custom-ability" aria-label="自定义能力名称" placeholder="自定义能力名称" maxlength="80"><button id="add-custom-ability">加入必需</button></div><small>能力名称是设计标签，不表示游戏已实现该能力。</small><label class="field">能力要求补充<textarea id="capability-note" maxlength="4000" rows="2" placeholder="例如只限制主路线；奖励支路另行注明">${esc(r.note)}</textarea></label>${doc.source?`<details class="source-abilities"><summary>查看原模块能力依据</summary><p>${esc(requirementSummary(doc.source.capabilityRequirements))}</p><p>${esc(doc.source.capabilityEvidence?.note??'旧草稿未记录结构化依据，可打开最新版模块查看。')}</p>${doc.source.capabilityEvidence?.tuningConstraints?.length?`<pre>${esc(JSON.stringify(doc.source.capabilityEvidence.tuningConstraints,null,2))}</pre>`:''}</details>`:''}<p>这些条件随草稿保存；应用到游戏时仍需接入生成筛选并验证物理通关。</p></details>`;
  const update=fn=>{snapshot();doc.capabilityRequirements=clone(doc.capabilityRequirements??emptyRequirements());fn(doc.capabilityRequirements);changed();renderCapabilities();};
  $('#capability-status').onchange=e=>{const value=e.target.value;if(value==='unspecified'&&(r.allOf.length||r.anyOfGroups.length)){toast('请先清空条件，再标为未填写');renderCapabilities();return;}update(v=>v.status=value);};
  panel.querySelectorAll('[data-ability]').forEach(el=>el.onchange=()=>{const group=el.dataset.abilityGroup,id=el.dataset.ability;update(v=>{const list=group==='all'?v.allOf:v.anyOfGroups[Number(group)];if(el.checked){if(list.length>=50){toast('每组最多 50 种能力');return;}list.push(id);}else list.splice(list.indexOf(id),1);if(group!=='all'&&!list.length)v.anyOfGroups.splice(Number(group),1);if(v.status==='unspecified')v.status='partial';});});
  $('#add-ability-group').onclick=()=>{if(r.anyOfGroups.length>=20){toast('最多 20 组');return;}update(v=>{v.anyOfGroups.push(['double_jump','wall_climb']);if(v.status==='unspecified')v.status='partial';});};
  panel.querySelectorAll('[data-remove-ability-group]').forEach(el=>el.onclick=()=>update(v=>v.anyOfGroups.splice(Number(el.dataset.removeAbilityGroup),1)));
  $('#add-custom-ability').onclick=()=>{const id=$('#custom-ability').value.trim();if(!id||r.allOf.includes(id))return;if(r.allOf.length>=50){toast('最多 50 种必需能力');return;}update(v=>{v.allOf.push(id);if(v.status==='unspecified')v.status='partial';});};
  $('#capability-note').onchange=e=>update(v=>v.note=e.target.value);
}
function renderDifficulty(){
  const d=validateDifficulty(doc.difficulty),panel=$('#difficulty-panel');
  const guideOpen=panel.querySelector('details')?.open??false;
  panel.innerHTML=`<section class="difficulty-card"><div class="section-heading">模块难度 <span>统一 1～10 分</span></div><label class="field">主路线评分<select id="difficulty-score">${option('','未评分',d.score===null?'':String(d.score))}${DIFFICULTY_LEVELS.map(level=>option(String(level.score),`${level.score} · ${level.name}`,String(d.score))).join('')}</select></label><p id="difficulty-description">${esc(d.score===null?'还没有评估；未评分不会当成 1 分。':DIFFICULTY_LEVELS[d.score-1].guide)}</p><label class="field">评分依据<textarea id="difficulty-note" rows="2" maxlength="4000" placeholder="例如：连续三次精确落点，但下方有失败回收平台">${esc(d.note)}</textarea></label><details ${guideOpen?'open':''}><summary>查看统一评分标准</summary><p>假定玩家已拥有所需能力，以必经主路线为准，不计额外强化。综合操作精度、时机、连续动作、失败容错和战斗压力；以最难必经段为主，长时间连续压力可上调。可选奖励支路另行注明。能力多不等于难度高。</p><ol>${DIFFICULTY_LEVELS.map(level=>`<li><b>${level.name}</b>：${level.guide}</li>`).join('')}</ol><p>这是设计预估，试玩后校准。后续生成地图时，先筛能力，再按曲线挑选难度；整图额外敌人和接缝压力需另行评估，模块评分不能直接相加。</p></details></section>`;
  const update=fn=>{snapshot();doc.difficulty=validateDifficulty(doc.difficulty);fn(doc.difficulty);changed();renderDifficulty();};
  $('#difficulty-score').onchange=e=>update(v=>v.score=e.target.value===''?null:Number(e.target.value));
  $('#difficulty-note').onchange=e=>update(v=>v.note=e.target.value);
}
function updateRouteOptions(){const routes=doc.objects.filter(o=>o.type==='route');if(routeView!=='all'&&routeView!=='none'&&!routes.some(o=>o.id===routeView))routeView='all';$('#route-view').innerHTML=option('all','全部路线',routeView)+option('none','隐藏路线',routeView)+routes.map((o,i)=>option(o.id,o.label||`人物路线 ${i+1}`,routeView)).join('');}
function setTool(next){if(drawing&&next!==tool)finishDrawing();tool=next;document.querySelectorAll('[data-tool]').forEach(b=>b.classList.toggle('active',b.dataset.tool===tool));svg.style.cursor=tool==='pan'?'grab':tool==='select'?'default':'crosshair';const hints={select:'点选物体调整 · 拖动移动 · 双指缩放',pan:'拖动画布移动 · 双指缩放',terrain:'在画布拖出地块 · 完成后继续绘制',route:'依次点击添加动作节点，点「完成绘制」结束',trackLine:'依次点击画轨道，点「完成绘制」结束',trackArc:'拖出弧形轨道，再拖中间控制点调整弧度'};$('#canvas-hint').textContent=hints[tool]??'';}
function defs(){return `<defs><pattern id="grid" width="24" height="24" patternUnits="userSpaceOnUse"><path d="M24 0H0V24" fill="none" stroke="#c8cfbc" stroke-width=".65" opacity=".55"/></pattern><pattern id="soil" width="16" height="16" patternUnits="userSpaceOnUse"><path d="M2 5l3-2m5 8l3-2" stroke="#a7af94" stroke-width="1" opacity=".5"/></pattern><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="none" stroke="#7395a4" stroke-width="1.2"/></marker><marker id="rail-arrow" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto"><path d="M0 0L5 3L0 6" fill="none" stroke="#b49a66" stroke-width="1.2"/></marker></defs>`;}
function gearPath(w,h){const cx=w/2,cy=h/2,r=Math.min(w,h)/2;let pts=[];for(let i=0;i<48;i++){const a=i/48*Math.PI*2,rr=r*([0,1].includes(i%4)?1:.79);pts.push(`${cx+Math.cos(a)*rr},${cy+Math.sin(a)*rr}`);}return pts.join(' ');}
function shape(o){
  const {w,h,type}=o,mid=w/2;
  if(type==='terrain')return `<rect x="0" y="0" width="${w}" height="${h}" rx="3" fill="#c9cfb5" stroke="#8f9c7d" stroke-width="1.5"/><rect x="1" y="1" width="${Math.max(0,w-2)}" height="${Math.max(0,h-2)}" rx="3" fill="url(#soil)"/><path d="M1 3H${w-1}" stroke="#7c916a" stroke-width="5"/>`;
  if(type==='platform')return `<rect width="${w}" height="${h}" rx="3" fill="#c6b492" stroke="#9e8f73" stroke-width="1.5"/><path d="M4 4H${w-4}" stroke="#f3e5c8" stroke-width="2"/><path d="M${w*.2} ${h}v7m${w*.6} -7v7" stroke="#b2a282" stroke-width="2"/>`;
  if(type==='anchor')return `<circle cx="${mid}" cy="${h/2}" r="${Math.max(2,Math.min(w,h)/2)}" fill="#94aa87" opacity=".6"/><circle cx="${mid}" cy="${h/2}" r="2" fill="#f7f9ec"/>`;
  if(type==='hazard')return `<rect width="${w}" height="${h}" fill="#d78b7940" stroke="#c7806b" stroke-width="1.2" stroke-dasharray="5 4"/>`;
  if(type==='gate')return `<rect width="${w}" height="${h}" rx="2" fill="#d1c6a9" stroke="#9a8960" stroke-width="1.7"/><path d="M${w/2} 4V${h-4}" stroke="#9a8960" stroke-width="2" stroke-dasharray="6 7"/>`;
  if(type==='reward')return `<rect x="1" y="5" width="${w-2}" height="${h-6}" rx="3" fill="#e2c987" stroke="#a78c4e" stroke-width="1.5"/><path d="M2 ${h*.5}H${w-2}M${mid} 8v${h-12}" stroke="#b19657" stroke-width="2"/><rect x="${mid-4}" y="${h*.5-3}" width="8" height="8" fill="#fff1c8" stroke="#a78c4e"/>`;
  if(type==='gear')return `<g transform="rotate(${time*45} ${mid} ${h/2})"><polygon points="${gearPath(w,h)}" fill="#e9c5ad" stroke="#c5775e" stroke-width="1.8"/><circle cx="${mid}" cy="${h/2}" r="${Math.min(w,h)*.22}" fill="#f8eee1" stroke="#c5775e" stroke-width="1.6"/><circle cx="${mid}" cy="${h/2}" r="3" fill="#c5775e"/></g>`;
  if(type==='spike'||type==='wallSpike'){
    const wall=type==='wallSpike',len=wall?h:w,depth=wall?w:h,n=Math.max(1,Math.round(len/21));let path='';
    for(let i=0;i<n;i++){const a=i*len/n,b=(i+.5)*len/n,c=(i+1)*len/n;path+=wall?`M0 ${a}L${depth} ${b}L0 ${c}Z `:`M${a} ${depth}L${b} 0L${c} ${depth}Z `;}
    return `<path d="${path}" fill="#db9b83" stroke="#bd745b" stroke-width="1.2"/>`;
  }
  if(type==='bell')return `<path d="M${mid} 0V12M${mid-13} 34Q${mid-11} 10 ${mid} 12Q${mid+11} 10 ${mid+13} 34Z" fill="#e5c77c" stroke="#a78b4d" stroke-width="1.7"/><path d="M${mid} 34v10m-4 1h8m-4 0v7" stroke="#a78b4d" stroke-width="2"/><circle cx="${mid}" cy="25" r="3" fill="#f9ebbf"/>`;
  if(type==='switch')return `<rect x="3" y="${h*.45}" width="${w-6}" height="${h*.5}" rx="4" fill="#c8bba0" stroke="#a2916f" stroke-width="1.5"/><path d="M${mid} ${h*.65}L${w*.75} ${h*.15}" stroke="#9e8657" stroke-width="4"/><circle cx="${w*.75}" cy="${h*.15}" r="5" fill="#c6a96d"/>`;
  if(type==='hookBounce'||type==='hookHang')return `<circle cx="${mid}" cy="${h/2}" r="${Math.min(w,h)*.39}" fill="${type==='hookHang'?'#e0ece0':'#f3e6c4'}" stroke="${type==='hookHang'?'#769a81':'#b39a60'}" stroke-width="2.5"/><circle cx="${mid}" cy="${h/2}" r="${Math.min(w,h)*.19}" fill="none" stroke="#b3a679" stroke-width="1.5"/>${type==='hookHang'?`<path d="M${mid-9} -5v-5h18v5" fill="none" stroke="#769a81" stroke-width="2.5"/>`:`<path d="M${mid-6} ${h+3}l6-7 6 7" fill="none" stroke="#b39a60" stroke-width="2"/>`}`;
  if(type==='mushroom')return `<path d="M${mid-7} ${h*.4}v${h*.52}h14V${h*.4}" fill="#e6d6b6" stroke="#a8906d" stroke-width="1.5"/><path d="M2 ${h*.52}Q5 -7 ${mid} 3Q${w-5} -7 ${w-2} ${h*.52}Z" fill="#d89a84" stroke="#b87864" stroke-width="1.5"/><circle cx="${w*.3}" cy="${h*.28}" r="4" fill="#f6e2c4"/><circle cx="${w*.63}" cy="${h*.23}" r="5" fill="#f6e2c4"/>`;
  if(type==='enemy')return `<path d="M4 ${h*.65}Q0 ${h*.1} ${mid} 5Q${w} ${h*.1} ${w-4} ${h*.65}L${w-2} ${h-3}L${mid} ${h-8}L2 ${h-3}Z" fill="#aca7bd" stroke="#81778e" stroke-width="1.5"/><path d="M${w*.28} ${h*.42}h4m${w*.28} 0h4" stroke="#fffdf2" stroke-width="4"/><path d="M${w*.3} 4L${w*.2} -3m${w*.5} 7l5-7" stroke="#81778e" stroke-width="2"/>`;
  if(type==='entry'||type==='exit')return `<path d="M5 ${h}V${w/2}Q5 0 ${mid} 0Q${w-5} 0 ${w-5} ${w/2}V${h}Z" fill="${type==='entry'?'#dbe5d2':'#e7dfc5'}" stroke="${type==='entry'?'#7d9775':'#b4a16d'}" stroke-width="2"/><path d="M${mid-8} ${h*.6}h16m-6-6 6 6-6 6" fill="none" stroke="${type==='entry'?'#7d9775':'#aa955b'}" stroke-width="2"/>`;
  if(type==='note')return `<rect width="${w}" height="${h}" rx="4" fill="#faf3d8" stroke="#d6c794" stroke-width="1"/><path d="M0 0v${h}" stroke="#d6bc76" stroke-width="4"/><text x="12" y="${h/2+5}" font-size="14" fill="#99824d">${esc(o.label||'双击或在右侧编辑文字')}</text>`;
  return '';
}
function pathD(o){if(o.type==='trackArc'){const a=o.points[0],b=o.points.at(-1),c=o.control;return `M${a.x},${a.y} Q${c.x},${c.y} ${b.x},${b.y}`;}return o.points.map((p,i)=>`${i?'L':'M'}${p.x},${p.y}`).join(' ');}
function routeMarkup(o,interactive=true){
  const route=o.type==='route',color=route?'#7395a4':'#b49a66';
  let s=`<path d="${pathD(o)}" fill="none" stroke="${color}" stroke-width="${route?2:1.8}" stroke-dasharray="${route?'7 6':'5 5'}" marker-end="url(#${route?'arrow':'rail-arrow'})"/>`;
  if(interactive)s+=`<path d="${pathD(o)}" fill="none" stroke="transparent" stroke-width="18"/>`;
  if(route)s+=o.points.map((p,i)=>`<g><circle cx="${p.x}" cy="${p.y}" r="11" fill="#fafbf5" stroke="${color}" stroke-width="1.5"/><text x="${p.x}" y="${p.y+4}" text-anchor="middle" font-size="11" fill="${color}">${i+1}</text><text x="${p.x+16}" y="${p.y-12}" font-size="11" fill="#61818f" paint-order="stroke" stroke="#f7f7ee" stroke-width="4">${esc(p.action??'')}</text></g>`).join('');
  else s+=o.points.map(p=>`<circle cx="${p.x}" cy="${p.y}" r="4" fill="#f7f5ea" stroke="${color}" stroke-width="1.5"/>`).join('');
  return s;
}
function objectMarkup(o,interactive=true){
  let x=o.x,y=o.y;
  if(o.trackId){const track=doc.objects.find(t=>t.id===o.trackId);if(track&&time>0){const p=pathPoint(track,progressAt(track,time));const origin=pathPoint(track,progressAt(track,0));x+=p.x-origin.x;y+=p.y-origin.y;}}
  const meta=interactive?`data-id="${esc(o.id)}"`:'';
  if(o.points)return `<g ${meta}>${routeMarkup(o,interactive)}</g>`;
  const label=o.type!=='note'&&o.label?`<text x="${o.w/2}" y="-12" text-anchor="middle" font-size="12" fill="#7e896e" paint-order="stroke" stroke="#f7f7ee" stroke-width="4">${esc(o.label)}</text>`:'';
  return `<g ${meta} transform="translate(${fmt(x)} ${fmt(y)}) rotate(${o.rotation??0} ${o.w/2} ${o.h/2})">${shape(o)}${label}</g>`;
}
function selectionMarkup(o){
  if(!o)return '';
  if(o.points){let h=o.points.map((p,i)=>`<circle data-handle="point:${i}" cx="${p.x}" cy="${p.y}" r="7" fill="#fffdf2" stroke="#52775b" stroke-width="2" style="cursor:move"/>`).join('');
    if(o.control){h+=`<path d="M${o.points[0].x},${o.points[0].y}L${o.control.x},${o.control.y}L${o.points.at(-1).x},${o.points.at(-1).y}" fill="none" stroke="#9eac8f" stroke-dasharray="3 4"/><circle data-handle="control" cx="${o.control.x}" cy="${o.control.y}" r="8" fill="#f2d991" stroke="#9c824c" stroke-width="2"/>`;}
    return `<g data-id="${esc(o.id)}">${h}</g>`;
  }
  return `<g transform="translate(${o.x} ${o.y}) rotate(${o.rotation??0} ${o.w/2} ${o.h/2})"><rect x="-5" y="-5" width="${o.w+10}" height="${o.h+10}" rx="3" fill="none" stroke="#52775b" stroke-width="1.5" stroke-dasharray="5 3" pointer-events="none"/><rect data-id="${esc(o.id)}" data-handle="resize" x="${o.w-4}" y="${o.h-4}" width="10" height="10" rx="2" fill="#fffdf2" stroke="#52775b" stroke-width="1.8" style="cursor:nwse-resize"/></g>`;
}
function contentMarkup(interactive=true){
  const tracks=doc.objects.filter(o=>o.type.startsWith('track')),objects=doc.objects.filter(o=>!o.type.startsWith('track')&&o.type!=='route'),routes=doc.objects.filter(o=>o.type==='route'&&(routeView==='all'||routeView===o.id||o.id===drawing?.id));
  const links=doc.objects.filter(o=>o.targetId).map(o=>{const t=doc.objects.find(t=>t.id===o.targetId);return t?`<path d="M${o.x+o.w/2} ${o.y+o.h/2}L${t.x+t.w/2} ${t.y+t.h/2}" fill="none" stroke="#c1ab70" stroke-width="1" stroke-dasharray="3 6"/>`:'';}).join('');
  let html=links+[...tracks,...objects,...routes].map(o=>objectMarkup(o,interactive)).join('');
  if(time>0){for(const route of routes){const p=pathPoint(route,Math.min(1,time/route.duration));html+=`<g transform="translate(${p.x},${p.y-18})" pointer-events="none"><circle cy="-9" r="7" fill="#46685a"/><path d="M0 -2v14m-9-7L0 0l9 5M0 12l-6 9m6-9 6 9" fill="none" stroke="#46685a" stroke-width="3" stroke-linecap="round"/></g>`;}}
  return html;
}
function render(){
  svg.setAttribute('viewBox',`${camera.x} ${camera.y} ${camera.w} ${camera.h}`);
  svg.innerHTML=defs()+`<rect x="${camera.x}" y="${camera.y}" width="${camera.w}" height="${camera.h}" fill="#f4f5eb"/><rect x="${camera.x}" y="${camera.y}" width="${camera.w}" height="${camera.h}" fill="url(#grid)"/><rect x="0" y="0" width="${doc.canvas.width}" height="${doc.canvas.height}" fill="none" stroke="#c2ccaf" stroke-width="1" stroke-dasharray="6 8"/>`+contentMarkup()+selectionMarkup(current());
  $('#object-count').textContent=`${doc.objects.filter(o=>!o.type.startsWith('track')).length} 个对象`;
  $('#zoom-label').textContent=`${Math.round(1600/camera.w*100)}%`;
  updateRouteOptions();
}
function field(label,key,value,type='text',options={}){
  const attrs=`data-prop="${key}" ${options.min!=null?`min="${options.min}"`:''} ${options.max!=null?`max="${options.max}"`:''} ${type==='number'?'step="any"':''}`;
  return `<label class="field">${esc(label)}<input type="${type}" value="${esc(value)}" ${attrs}></label>`;
}
function option(value,label,active){return `<option value="${esc(value)}" ${value===active?'selected':''}>${esc(label)}</option>`;}
function renderInspector(){
  const o=current();
  if(!o){$('#selection').innerHTML='<div class="empty-selection"><div class="symbol">↖</div><b>把想法摆到画布上</b><p>点击左侧素材添加物体。<br>选中物体后，在这里调整大小、轨道和说明。</p></div>'+(doc.source?`<div class="source-note">来自原项目模块：${esc(doc.source.moduleId)}<br>打开后可自由修改；原版保留在模块库。<br><a href="${esc('https://github.com/zhipijun1996/gunman-rush/blob/'+doc.source.commit+'/'+doc.source.path)}" target="_blank" rel="noopener">查看原模块 ↗</a></div>`:'');return;}
  let html=`<div class="selected-card"><div class="selection-label">${esc(TYPES[o.type].name)}<span class="tag">已选中</span></div>${field('名称 / 标注','label',o.label)}`;
  if(!o.points){html+=`<div class="field-row">${field('宽度','w',fmt(o.w),'number',{min:4})}${field('高度','h',fmt(o.h),'number',{min:4})}</div><div class="field-row">${field('水平位置','x',fmt(o.x),'number')}${field('垂直位置','y',fmt(o.y),'number')}</div>${field('旋转角度','rotation',o.rotation??0,'number')}`;
    if(!['entry','exit','note'].includes(o.type)){
      const tracks=doc.objects.filter(t=>t.type.startsWith('track'));
      html+=`<label class="field">沿轨道运动<select data-prop="trackId">${option('','静止',o.trackId??'')}${tracks.map((t,i)=>option(t.id,t.label||`轨道 ${i+1} · ${TYPES[t.type].name}`,o.trackId)).join('')}</select></label><p class="inline-help">把轨道起点叠在物体中心，会自动绑定。可用下方时间条查看运动。</p>`;
    }
    if(['bell','switch'].includes(o.type))html+=`<label class="field">触发 / 控制目标<select data-prop="targetId">${option('','未指定',o.targetId??'')}${doc.objects.filter(t=>t.id!==o.id).map(t=>option(t.id,t.label||TYPES[t.type].name,o.targetId)).join('')}</select></label>`;
  }else{
    html+=field(o.type==='route'?'演示总时长（秒）':'单程运行时间（秒）','duration',o.duration,'number',{min:.1,max:3600});
    if(o.type!=='route')html+=`<label class="field">运动方式<select data-prop="mode">${[['pingpong','往返'],['loop','循环（回到起点）'],['once','单程'],['sine','正弦往返（原齿轮）']].map(([v,n])=>option(v,n,o.mode)).join('')}</select></label>${field('端点停顿（秒）','dwell',o.dwell??0,'number',{min:0,max:60})}${field('起始相位（0–1）','initialPhase',o.initialPhase??0,'number',{min:0,max:1})}`;
    if(o.type==='route')html+=`<div class="section-heading">预期动作序列</div>${o.points.map((p,i)=>`<div class="step-row"><span>${i+1}.</span><input data-step="${i}" aria-label="第 ${i+1} 步动作" value="${esc(p.action??'')}" placeholder="例如：向下射击反冲"><button data-remove-step="${i}" title="删除动作节点">×</button></div>`).join('')}<button id="extend-route">＋ 继续画动作节点</button>`;
    html+='<p class="inline-help">拖动圆点调整路线。黄色点用于调整弧度。动作描述表达预期，不代表已通过物理验证。</p>';
  }
  html+=`<label class="field">局部说明<textarea data-prop="note" rows="3" placeholder="想保留的关系、等待条件、怪物类型…">${esc(o.note)}</textarea></label></div>`;
  $('#selection').innerHTML=html;
  $('#selection').querySelectorAll('[data-prop]').forEach(input=>input.addEventListener('change',()=>{
    snapshot();const key=input.dataset.prop;
    if(input.type==='number'){const n=Number(input.value);if(!Number.isFinite(n)||Math.abs(n)>1e7){toast('请输入有效数值');renderInspector();return;}o[key]=['w','h'].includes(key)?Math.max(4,n):key==='duration'?Math.max(.1,Math.min(3600,n)):key==='dwell'?Math.max(0,Math.min(60,n)):key==='initialPhase'?Math.max(0,Math.min(1,n)):n;}
    else o[key]=input.value;
    changed();
  }));
  $('#selection').querySelectorAll('[data-step]').forEach(input=>input.addEventListener('change',()=>{snapshot();o.points[Number(input.dataset.step)].action=input.value;changed();}));
  $('#selection').querySelectorAll('[data-remove-step]').forEach(b=>b.onclick=()=>{if(o.points.length<=2){toast('路线至少保留两个节点');return;}snapshot();o.points.splice(Number(b.dataset.removeStep),1);changed({inspector:true});});
  if($('#extend-route'))$('#extend-route').onclick=()=>{setTool('route');drawing=o;selected=o.id;$('#finish-draw').hidden=false;toast('点击画布继续添加动作节点');};
}
function populatePalette(){
  const groups=['地形','危险','机关','角色','标注'];
  $('#palette').innerHTML=groups.map(group=>`<section class="palette-section"><div class="palette-heading">${group}</div><div class="palette-grid">${Object.entries(TYPES).filter(([type,t])=>t.group===group&&!type.startsWith('track')&&type!=='route').map(([type,t])=>{const o=createObject(type,0,0,{w:type==='terrain'?50:type==='platform'?52:type==='spike'?50:type==='wallSpike'?15:Math.min(t.w,38),h:type==='terrain'?25:type==='platform'?8:type==='spike'?13:type==='wallSpike'?30:Math.min(t.h,35),label:type==='note'?'想法':''});return `<button class="asset" data-add="${type}" title="添加${t.name}"><svg viewBox="-5 -12 70 58" aria-hidden="true">${shape(o)}</svg><span>${t.name}</span></button>`;}).join('')}</div></section>`).join('');
  document.querySelectorAll('[data-add]').forEach(b=>b.onclick=()=>addAtCenter(b.dataset.add));
}
function addAtCenter(type){
  finishDrawing();setTool('select');stopPlayback();snapshot();const t=TYPES[type];const o=createObject(type,snap(camera.x+camera.w/2-t.w/2),snap(camera.y+camera.h/2-t.h/2));if(type==='note')o.label='写下你的想法';doc.objects.push(o);selected=o.id;changed({inspector:true});
}
function coords(e){const p=svg.createSVGPoint();p.x=e.clientX;p.y=e.clientY;return p.matrixTransform(svg.getScreenCTM().inverse());}
function snap(n){return $('#snap').checked?Math.round(n/12)*12:n;}
function stopPlayback(){playing=false;$('#play').textContent='▶ 演示';if(time){time=0;$('#time').value=0;$('#time-label').textContent='0.0s';render();}}
function finishDrawing(){if(!drawing)return;const o=drawing;if(o.points.length<2){doc.objects=doc.objects.filter(t=>t.id!==o.id);selected=null;}else{bindNear(o);if(o.type==='route')routeView=o.id;}drawing=null;$('#finish-draw').hidden=true;changed({inspector:true});}
function bindNear(o){
  if(o.type.startsWith('track')){
    const p=pathPoint(o,progressAt(o,0));let candidates=doc.objects.filter(t=>!t.points&&!['note','entry','exit'].includes(t.type));candidates.sort((a,b)=>Math.hypot(a.x+a.w/2-p.x,a.y+a.h/2-p.y)-Math.hypot(b.x+b.w/2-p.x,b.y+b.h/2-p.y));
    const target=candidates[0];if(target&&Math.hypot(target.x+target.w/2-p.x,target.y+target.h/2-p.y)<45){target.trackId=o.id;toast('已绑定到'+(target.label||TYPES[target.type].name));}
  }else if(!o.points&&!['note','entry','exit'].includes(o.type)){
    for(const t of doc.objects.filter(t=>t.type.startsWith('track'))){const p=pathPoint(t,progressAt(t,0));if(Math.hypot(o.x+o.w/2-p.x,o.y+o.h/2-p.y)<30){o.trackId=t.id;toast('已绑定轨道');break;}}
  }
}
svg.addEventListener('pointerdown',e=>{
  if(e.button!==0&&e.button!==1)return;e.preventDefault();svg.focus();pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});svg.setPointerCapture(e.pointerId);
  if(pointers.size===2){const ps=[...pointers.values()];gesture={kind:'pinch',distance:Math.hypot(ps[0].x-ps[1].x,ps[0].y-ps[1].y),camera:clone(camera),mid:{x:(ps[0].x+ps[1].x)/2,y:(ps[0].y+ps[1].y)/2}};return;}
  const p=coords(e);
  if(tool==='pan'||e.button===1){gesture={kind:'pan',start:p,camera:clone(camera),client:{x:e.clientX,y:e.clientY}};return;}
  if(['route','trackLine'].includes(tool)){
    stopPlayback();
    if(!drawing){snapshot();drawing=createObject(tool,p.x,p.y,{points:[]});doc.objects.push(drawing);selected=drawing.id;}
    drawing.points.push({x:snap(p.x),y:snap(p.y),...(tool==='route'?{action:drawing.points.length?'落点 / 动作':'起跳'}:{})});$('#finish-draw').hidden=false;changed({inspector:false});return;
  }
  stopPlayback();
  if(tool==='terrain'||tool==='trackArc'){
    snapshot();const o=createObject(tool,snap(p.x),snap(p.y),tool==='terrain'?{w:12,h:12}:{points:[{x:snap(p.x),y:snap(p.y)},{x:snap(p.x)+12,y:snap(p.y)}],control:{x:p.x,y:p.y-80}});doc.objects.push(o);selected=o.id;gesture={kind:'create',id:o.id,start:{x:snap(p.x),y:snap(p.y)}};render();return;
  }
  const hit=e.target.closest('[data-id]');selected=hit?.dataset.id??null;
  const o=current();if(o){snapshot();gesture={kind:e.target.dataset.handle??'move',id:o.id,start:{x:p.x,y:p.y},original:clone(o)};}
  render();renderInspector();updateHistory();
});
svg.addEventListener('pointermove',e=>{
  if(pointers.has(e.pointerId))pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(!gesture)return;
  if(gesture.kind==='pinch'){
    if(pointers.size<2)return;const ps=[...pointers.values()],distance=Math.hypot(ps[0].x-ps[1].x,ps[0].y-ps[1].y);const factor=gesture.distance/Math.max(10,distance);const c=gesture.camera;
    const w=Math.max(200,Math.min(20000,c.w*factor)),h=w*svg.clientHeight/svg.clientWidth;const rect=svg.getBoundingClientRect();const oldMx=(gesture.mid.x-rect.left)/rect.width,oldMy=(gesture.mid.y-rect.top)/rect.height;const newMx=((ps[0].x+ps[1].x)/2-rect.left)/rect.width,newMy=((ps[0].y+ps[1].y)/2-rect.top)/rect.height;
    camera={x:c.x+oldMx*c.w-newMx*w,y:c.y+oldMy*c.h-newMy*h,w,h};render();return;
  }
  if(gesture.kind==='pan'){camera.x=gesture.camera.x-(e.clientX-gesture.client.x)*camera.w/svg.clientWidth;camera.y=gesture.camera.y-(e.clientY-gesture.client.y)*camera.h/svg.clientHeight;render();return;}
  const o=doc.objects.find(o=>o.id===gesture.id);if(!o)return;const p=coords(e);
  if(gesture.kind==='create'){
    if(o.type==='terrain'){o.x=Math.min(gesture.start.x,snap(p.x));o.y=Math.min(gesture.start.y,snap(p.y));o.w=Math.max(12,Math.abs(snap(p.x)-gesture.start.x));o.h=Math.max(12,Math.abs(snap(p.y)-gesture.start.y));}
    else{o.points[1]={x:snap(p.x),y:snap(p.y)};o.control={x:(o.points[0].x+p.x)/2,y:Math.min(o.points[0].y,p.y)-Math.max(60,Math.abs(p.x-o.points[0].x)*.4)};}
  }else if(gesture.kind==='move'){
    const dx=snap(p.x-gesture.start.x),dy=snap(p.y-gesture.start.y);Object.assign(o,clone(gesture.original));translateObject(o,dx,dy);
  }else if(gesture.kind==='resize'){
    const a=-(o.rotation??0)*Math.PI/180,dx=p.x-gesture.start.x,dy=p.y-gesture.start.y;o.w=Math.max(8,snap(gesture.original.w+dx*Math.cos(a)-dy*Math.sin(a)));o.h=Math.max(8,snap(gesture.original.h+dx*Math.sin(a)+dy*Math.cos(a)));
  }else if(gesture.kind==='control'){o.control={x:snap(p.x),y:snap(p.y)};
  }else if(gesture.kind.startsWith('point:')){Object.assign(o.points[Number(gesture.kind.split(':')[1])],{x:snap(p.x),y:snap(p.y)});}
  render();
});
function endPointer(e){
  pointers.delete(e.pointerId);if(!gesture)return;
  if(gesture.kind==='pinch'){if(!pointers.size)gesture=null;return;}
  const o=doc.objects.find(o=>o.id===gesture.id);if(o)bindNear(o);
  const mutated=!['pan','pinch'].includes(gesture.kind);gesture=null;if(mutated)changed({inspector:true});
}
svg.addEventListener('pointerup',endPointer);svg.addEventListener('pointercancel',endPointer);
svg.addEventListener('dblclick',e=>{if(drawing){e.preventDefault();if(drawing.points.length>2){const ps=drawing.points,a=ps.at(-1),b=ps.at(-2);if(Math.hypot(a.x-b.x,a.y-b.y)<8)ps.pop();}finishDrawing();setTool('select');}});
svg.addEventListener('wheel',e=>{e.preventDefault();zoom(e.deltaY>0?1.12:1/1.12,coords(e));},{passive:false});
function zoom(factor,point={x:camera.x+camera.w/2,y:camera.y+camera.h/2}){const old=clone(camera);camera.w=Math.max(200,Math.min(30000,camera.w*factor));camera.h=camera.w*svg.clientHeight/svg.clientWidth;camera.x=point.x-(point.x-old.x)*camera.w/old.w;camera.y=point.y-(point.y-old.y)*camera.h/old.h;render();}
function fit(){
  const bs=doc.objects.map(objectBounds);let x=0,y=0,right=doc.canvas.width,bottom=doc.canvas.height;
  if(bs.length){x=Math.min(...bs.map(b=>b.x))-100;y=Math.min(...bs.map(b=>b.y))-100;right=Math.max(...bs.map(b=>b.x+b.w))+100;bottom=Math.max(...bs.map(b=>b.y+b.h))+100;}
  const ratio=Math.max(.1,svg.clientWidth/Math.max(1,svg.clientHeight));let w=right-x,h=bottom-y;if(w/h<ratio){const nw=h*ratio;x-=(nw-w)/2;w=nw;}else{const nh=w/ratio;y-=(nh-h)/2;h=nh;}camera={x,y,w,h};render();
}
function removeSelected(){if(!selected)return;snapshot();doc.objects=doc.objects.filter(o=>o.id!==selected);for(const o of doc.objects){if(o.trackId===selected)delete o.trackId;if(o.targetId===selected)delete o.targetId;}selected=null;changed({inspector:true});}
function duplicateSelected(){const o=current();if(!o)return;snapshot();const copy=clone(o);copy.id=uid();translateObject(copy,36,36);if(copy.type.startsWith('track'))delete copy.trackId;copy.label=copy.label?copy.label+' 副本':'';doc.objects.push(copy);selected=copy.id;changed({inspector:true});}
function runUndo(reverse=false){finishDrawing();const source=reverse?redo:undo,target=reverse?undo:redo;if(!source.length)return;target.push(clone(doc));doc=source.pop();selected=null;syncFields();changed();}
function download(blob,name){const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),20000);}
const filename=()=>doc.title.replace(/[<>:"/\\|?*\x00-\x1f]/g,'_').slice(0,80)||'关卡草图';
function saveFile(){finishDrawing();persist();const bundle={...doc,changeRequest:changeRequest(doc)};download(new Blob([JSON.stringify(bundle,null,2)],{type:'application/json'}),filename()+'.mapnote.json');toast(doc.source?'工程已保存，包含修改用途、原模块身份和变更记录':'工程已下载，可随时打开继续修改');}
function wrapText(text,max=58){const result=[];for(const line of text.split('\n')){if(!line){result.push('');continue;}let part='';for(const ch of line){part+=ch;if(part.length>=max){result.push(part);part='';}}if(part)result.push(part);}return result;}
function exportSvg(){
  const bs=doc.objects.map(objectBounds),left=Math.min(0,...bs.map(b=>b.x))-65,top=Math.min(0,...bs.map(b=>b.y))-90,right=Math.max(doc.canvas.width,...bs.map(b=>b.x+b.w))+65,bottom=Math.max(doc.canvas.height,...bs.map(b=>b.y+b.h))+50;
  const request=changeRequest(doc),purpose=doc.source?`${request.operation==='modify_existing'?'修改原模块':'新增变体'}：${doc.source.moduleId} · 基线 ${doc.source.commit.slice(0,8)} · 尚未写回游戏`:'';
  const lines=wrapText([purpose,difficultySummary(doc.difficulty),doc.difficulty?.note?'评分依据：'+doc.difficulty.note:'','能力要求：'+requirementSummary(doc.capabilityRequirements),doc.capabilityRequirements?.note,doc.description,doc.constraints?'制作时请保留：'+doc.constraints:''].filter(Boolean).join('\n'));
  const w=right-left,h=bottom-top+90+lines.length*22;
  const notes=lines.map((line,i)=>`<text x="${left+35}" y="${bottom+45+i*22}" font-size="15" fill="#64725a">${esc(line)}</text>`).join('');
  return {w,h,text:`<svg xmlns="${NS}" width="${w}" height="${h}" viewBox="${left} ${top} ${w} ${h}"><style>text{font-family:Arial,"Microsoft YaHei",sans-serif}</style>${defs()}<rect x="${left}" y="${top}" width="${w}" height="${h}" fill="#f4f5eb"/><text x="${left+35}" y="${top+45}" font-size="25" font-weight="600" fill="#38634c">${esc(doc.title)}</text><text x="${right-35}" y="${top+44}" font-size="12" text-anchor="end" fill="#89967a">MAP NOTES / 设计草图</text>${contentMarkup(false)}<path d="M${left+35} ${bottom+12}H${right-35}" stroke="#cbd3be"/>${notes}<text x="${right-35}" y="${top+h-15}" text-anchor="end" font-size="11" fill="#9ba48d">示意位置 · 预期动作 · 正式制作需验证物理</text><metadata>${esc(JSON.stringify({schema:doc.schema,source:doc.source??null}))}</metadata></svg>`};
}
async function exportImage(){
  finishDrawing();const data=exportSvg();const url=URL.createObjectURL(new Blob([data.text],{type:'image/svg+xml;charset=utf-8'}));
  try{const img=new Image();await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=reject;img.src=url;});const factor=Math.min(2,4096/Math.max(data.w,data.h));const c=document.createElement('canvas');c.width=Math.ceil(data.w*factor);c.height=Math.ceil(data.h*factor);c.getContext('2d').drawImage(img,0,0,c.width,c.height);const blob=await new Promise(resolve=>c.toBlob(resolve,'image/png'));if(!blob)throw new Error('PNG export failed');download(blob,filename()+'.png');toast('草图已导出，包含关卡说明');}catch{download(new Blob([data.text],{type:'image/svg+xml'}),filename()+'.svg');toast('已导出 SVG 图片，可用浏览器打开');}finally{URL.revokeObjectURL(url);}
}
function dialog(title,html){$('#dialog-title').textContent=title;$('#dialog-body').innerHTML=html;if(!$('#dialog').open)$('#dialog').showModal();}
function showProjects(){
  persist();dialog('我的草稿',`<p>草稿保存在当前浏览器。换设备时用「保存工程」和「打开工程」。</p><div class="dialog-actions"><button id="new-doc" class="primary">＋ 空白草图</button><button id="example-doc">打开示例</button></div><div>${[...saved.documents].reverse().map(d=>`<div class="draft-row"><button data-open-draft="${esc(d.id)}">${esc(d.title)}<small>${d.objects.length} 个对象 · ${new Date(d.updatedAt).toLocaleDateString('zh-CN')}</small></button><button data-delete-draft="${esc(d.id)}">删除</button></div>`).join('')}</div>`);
  $('#new-doc').onclick=()=>{$('#dialog').close();loadDocument(blankDocument());};$('#example-doc').onclick=()=>{$('#dialog').close();loadDocument(exampleDocument());};
  document.querySelectorAll('[data-open-draft]').forEach(b=>b.onclick=()=>{const d=saved.documents.find(d=>d.id===b.dataset.openDraft);$('#dialog').close();loadDocument(d);});
  document.querySelectorAll('[data-delete-draft]').forEach(b=>b.onclick=()=>{if(!confirm('删除这份本机草稿？已导出的工程文件不受影响。'))return;const id=b.dataset.deleteDraft;saved.documents=saved.documents.filter(d=>d.id!==id);if(doc.id===id){doc=blankDocument();syncFields();fit();}persist();showProjects();});
}
async function showLibrary(){
  dialog('项目模块库','<p>正在读取原项目模块…</p>');
  try{libraryData=await libraryClient.load();
    const cats=[...new Set(libraryData.modules.map(m=>m.category))];
    dialog('项目模块库',`<div class="library-version"><span>${libraryData.modules.length} 份参考 · 来源 <code>${esc(libraryData.sourceCommit.slice(0,8))}</code></span><button id="update-library">↻ 更新模块库</button></div><p>选「修改原模块」保留原身份；选「新增变体」保留原版。接入状态说明原游戏的使用范围，不代表你的修改已应用。</p><div class="library-filters"><label class="field">搜索模块<input id="library-search" placeholder="中文名称 / 英文 ID / 机关"></label><label class="field">地区<select id="library-category"><option value="">全部地区</option>${cats.map(c=>option(c,c,'')).join('')}</select></label><label class="field">是否接入游戏<select id="library-integration"><option value="">全部状态</option><option value="formal">已接入 · 正式流程</option><option value="development">已接入 · 开发试玩</option><option value="not_integrated">未接入</option><option value="unverified">待核实</option></select></label><label class="field">模块难度<select id="library-difficulty"><option value="">全部难度</option><option value="unrated">未评分</option>${DIFFICULTY_LEVELS.map(level=>option(String(level.score),`${level.score} · ${level.name}`,'')).join('')}</select></label></div><div id="library-results"></div>`);
    const list=()=>{const q=$('#library-search').value.toLowerCase(),cat=$('#library-category').value,usage=$('#library-integration').value,difficulty=$('#library-difficulty').value;const mods=libraryData.modules.filter(m=>(!cat||m.category===cat)&&(!usage||(m.integration?.usage??'unverified')===usage)&&(!difficulty||(difficulty==='unrated'?m.difficulty?.score==null:m.difficulty?.score===Number(difficulty)))&&JSON.stringify([m.title,m.id,m.tags,requirementSummary(m.capabilityRequirements),difficultySummary(m.difficulty)]).toLowerCase().includes(q));$('#library-results').innerHTML=mods.map(m=>`<article class="module-card" data-module="${esc(m.id)}"><img src="${esc(libraryClient.url(m.thumbnail))}" alt="${esc(m.title)}布局预览" loading="lazy"><b>${esc(m.title)}</b><small>${esc(m.id)}</small><small>${esc(m.category)} · ${m.objectCount} 个对象</small>${integrationBadge(m.integration)}<small class="module-difficulty">${esc(difficultySummary(m.difficulty))}</small><small class="module-abilities">${esc(requirementSummary(m.capabilityRequirements))}</small><div class="module-actions"><button data-edit-module="${esc(m.id)}">修改原模块</button><button data-variant-module="${esc(m.id)}">＋ 新增变体</button></div></article>`).join('')||'<p>没有匹配的模块</p>';
      const open=async(id,operation)=>{try{const m=libraryData.modules.find(m=>m.id===id);const reference=validateDocument(await libraryClient.module(m));const d=makeRevision(reference,operation);$('#dialog').close();loadDocument(d);toast(operation==='modify_existing'?'已创建原模块修改稿，保留原身份':'已创建新变体草稿，原版不变');}catch(e){toast('模块打开失败：'+e.message);}};
      document.querySelectorAll('[data-edit-module]').forEach(b=>b.onclick=()=>open(b.dataset.editModule,'modify_existing'));document.querySelectorAll('[data-variant-module]').forEach(b=>b.onclick=()=>open(b.dataset.variantModule,'new_variant'));
    };
    $('#library-search').oninput=list;$('#library-category').onchange=list;$('#library-integration').onchange=list;$('#library-difficulty').onchange=list;$('#update-library').onclick=checkLibraryUpdate;list();
  }catch{dialog('项目模块库','<p>模块库暂时无法加载。请检查网络后重试，你的本机草稿不受影响。</p>');}
}
async function checkLibraryUpdate(){
  persist();dialog('更新模块库','<p id="library-update-status">正在检查游戏 main 与可用模块库…</p>');
  try{
    const result=await libraryClient.checkUpdate();lastLibraryCheck=result;libraryData=libraryClient.catalog;renderRevisionInfo();
    showLibraryUpdateResult(result);
  }catch(e){dialog('更新模块库',`<p>检查失败：${esc(e.message)}</p><p>当前模块库和你的草稿保留不变。</p><div class="dialog-actions"><button id="retry-library-update">重试检查</button><button id="back-library">返回模块库</button></div>`);$('#retry-library-update').onclick=checkLibraryUpdate;$('#back-library').onclick=showLibrary;}
}
function showLibraryUpdateResult(result){
  const latest=result.isLatest;
  dialog('更新模块库',`<div class="update-summary"><span class="integration-badge ${latest?'formal':'unverified'}">${latest?'已是最新项目版本':'项目有新提交，等待生成新库'}</span><p>游戏 main：<code>${esc(result.latest.slice(0,8))}</code><br>已加载模块库：<code>${esc(result.current.slice(0,8))}</code></p></div><p id="library-update-status">${latest?'已从 GitHub 重新读取并加载模块目录，打开的草稿保持原来的基线。':'需要用游戏源数据运行 Godot 提取。点击下方按钮，在 GitHub 页面点 Run workflow；保留 main 默认值即可。完成后这里可检查并加载新库。'}</p><p class="inline-help">GitHub Pages 是静态网页，启动生成任务需要 GitHub 确认。无需复制令牌；失败时保留旧库，不覆盖草稿。</p><div class="dialog-actions">${latest?'':`<a id="start-library-sync" class="button-link primary" href="${SYNC_WORKFLOW}" target="_blank" rel="noopener">在 GitHub 运行同步 ↗</a>`}<button id="refresh-library-update">再次检查并加载</button><button id="back-library">返回模块库</button></div>`);
  $('#refresh-library-update').onclick=checkLibraryUpdate;$('#back-library').onclick=showLibrary;
  if($('#start-library-sync'))$('#start-library-sync').onclick=()=>pollLibrarySync(0);
}
function pollLibrarySync(attempt){
  if(attempt>=6)return;
  setTimeout(async()=>{
    if(!$('#dialog').open||!$('#library-update-status'))return;
    try{
      const result=await libraryClient.checkUpdate();lastLibraryCheck=result;libraryData=libraryClient.catalog;
      if(result.isLatest){renderRevisionInfo();showLibraryUpdateResult(result);return;}
      const run=await libraryClient.syncRun();
      if(run?.status==='completed'&&run.conclusion==='failure')$('#library-update-status').textContent='最近一次同步失败，旧库已保留。可在 GitHub 工作流查看日志，修复后重新运行。';
      else $('#library-update-status').textContent=run?.status==='in_progress'||run?.status==='queued'?'GitHub 正在生成 / 验证新库，完成后会自动加载。':'尚未检测到新库。请在 GitHub 点 Run workflow，也可稍后再次检查。';
      pollLibrarySync(attempt+1);
    }catch(e){if($('#library-update-status'))$('#library-update-status').textContent='自动检查暂时失败：'+e.message+'。可手动再次检查，草稿保留不变。';}
  },20000);
}
function help(){dialog('随手画一段关卡',`<ol class="help-list"><li>点击素材盒里的物体，拖到你想放的位置。</li><li>选中物体，在右侧或「设置」里改大小、名称和说明；拖右下角方块也能缩放。</li><li>用「人物路线」逐点画，点「完成绘制」，再填写每一步要做的动作。</li><li>用「轨道」逐点画直线 / 折线；用「弧轨」拖出曲线，拖黄色点调整弧度。轨道起点靠近物体中心时自动绑定，也可在设置中指定。</li><li>点击「演示」或拖时间条，查看机关运动和人物预期路线。</li><li>「模块库」打开现有游戏模块的可编辑副本。</li><li>「导出图片」发给 Codex；「保存工程」用于换设备、备份或交给 Codex 读取结构。</li></ol><p><kbd>V</kbd> 选择 · <kbd>空格</kbd> 拖动画布 · <kbd>滚轮 / 双指</kbd> 缩放 · <kbd>Ctrl Z</kbd> 撤销 · <kbd>Delete</kbd> 删除</p><p>浏览器自动保存只在本机生效。草图中的动作是设计意图，正式关卡仍需在游戏里验证。</p>`);}
document.querySelectorAll('[data-tool]').forEach(b=>b.onclick=()=>setTool(b.dataset.tool));
$('#finish-draw').onclick=()=>{finishDrawing();setTool('select');};
$('#undo').onclick=()=>runUndo();$('#redo').onclick=()=>runUndo(true);$('#delete').onclick=removeSelected;$('#duplicate').onclick=duplicateSelected;
$('#zoom-in').onclick=()=>zoom(.8);$('#zoom-out').onclick=()=>zoom(1.25);$('#fit').onclick=fit;$('#zoom-label').onclick=fit;
$('#fullscreen').onclick=async()=>{try{if(document.fullscreenElement)await document.exitFullscreen();else await $('.studio').requestFullscreen();}catch{toast('当前浏览器不支持全屏');}};
$('#inspector-toggle').onclick=()=>$('#inspector').classList.toggle('mobile-open');$('#close-inspector').onclick=()=>$('#inspector').classList.remove('mobile-open');
$('#title').addEventListener('change',()=>{snapshot();doc.title=$('#title').value||'未命名关卡';changed();});
for(const key of ['description','constraints']){$('#'+key).addEventListener('focus',()=>snapshot());$('#'+key).addEventListener('input',()=>{doc[key]=$('#'+key).value;changed();});}
$('#play').onclick=()=>{finishDrawing();playing=!playing;$('#play').textContent=playing?'Ⅱ 暂停':'▶ 演示';lastFrame=performance.now();};
$('#time').oninput=()=>{playing=false;$('#play').textContent='▶ 演示';time=Number($('#time').value);$('#time-label').textContent=time.toFixed(1)+'s';render();};
$('#route-view').onchange=()=>{routeView=$('#route-view').value;render();};
function animate(now){if(playing){time+=(now-lastFrame)/1000;if(time>20)time=0;$('#time').value=time;$('#time-label').textContent=time.toFixed(1)+'s';render();}lastFrame=now;requestAnimationFrame(animate);}requestAnimationFrame(animate);
$('#projects').onclick=showProjects;$('#library').onclick=showLibrary;$('#help').onclick=help;$('#dialog-close').onclick=()=>$('#dialog').close();
$('#save-file').onclick=saveFile;$('#export').onclick=exportImage;$('#import').onclick=()=>$('#file-input').click();
$('#file-input').onchange=async()=>{const file=$('#file-input').files[0];if(!file)return;try{if(file.size>20*1024*1024)throw Error('文件超过 20 MB');const d=validateDocument(JSON.parse(await file.text()));if(!d.generationContract)d.id=uid();loadDocument(d);toast('工程已打开');}catch(e){toast('无法打开：'+e.message);}finally{$('#file-input').value='';}};
window.addEventListener('beforeunload',persist);
window.addEventListener('keydown',e=>{
  if(['INPUT','TEXTAREA','SELECT'].includes(e.target.tagName)||$('#dialog').open)return;
  if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='z'){e.preventDefault();runUndo(e.shiftKey);return;}
  if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='s'){e.preventDefault();saveFile();return;}
  if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='d'){e.preventDefault();duplicateSelected();return;}
  if(e.code==='Space'&&!e.repeat){e.preventDefault();lastPanTool=tool;setTool('pan');}
  if(e.key==='Delete'||e.key==='Backspace'){e.preventDefault();removeSelected();}
  if(e.key==='Escape'){finishDrawing();selected=null;setTool('select');render();renderInspector();}
  if(e.key==='Enter'&&drawing){finishDrawing();setTool('select');}
  if(e.key.toLowerCase()==='v')setTool('select');if(e.key.toLowerCase()==='r')setTool('terrain');
});
window.addEventListener('keyup',e=>{if(e.code==='Space'&&tool==='pan')setTool(lastPanTool);});
new ResizeObserver(()=>{const ratio=svg.clientHeight/Math.max(1,svg.clientWidth),center=camera.y+camera.h/2;camera.h=camera.w*ratio;camera.y=center-camera.h/2;render();}).observe($('#canvas-wrap'));
populatePalette();syncFields();fit();persist();
