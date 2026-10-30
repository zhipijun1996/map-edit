import {validateGenerationContract} from './module-contract.js';
import {DIFFICULTY_LEVELS,validateDifficulty,difficultySummary,difficultyChanges} from './difficulty.js';
import {ABILITIES,abilityName,emptyRequirements,requirementSummary} from './capabilities.js';
import {TYPES,SCHEMA,uid,clone,createObject,blankDocument,validateDocument,pathPoint,progressAt,translateObject,objectBounds,makeRevision,objectChanges,changeRequest} from './model.js';
import {CurrentModuleLibraryClient} from './current-module-library-client.js';
import {cornerRelocationRows,FACE_NAMES} from './corner-port-view.js';
import {foundationReview,physicalPortGroups,portCounts,renderFoundationReview} from './module-review-overlay.js';
import {loadCornerBatch,moduleCornerProgress,stageLabel,loadCornerPreview} from './corner-batch-review.js';
import {renderMirrorReview} from './module-mirror-review.js';
const $=s=>document.querySelector(s), svg=$('#canvas'), NS='http://www.w3.org/2000/svg';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=n=>Math.round(n*100)/100;
const STORE='map-notes-v1';
let saved={documents:[],activeId:null};
try{const raw=JSON.parse(localStorage.getItem(STORE));if(raw&&Array.isArray(raw.documents)){saved.documents=raw.documents.flatMap(d=>{try{return [validateDocument(d)];}catch{return [];}});saved.activeId=raw.activeId;}}catch{ /* A malformed draft must not prevent opening the editor. */ }
function newDraft(){const d=blankDocument('Module 设计草稿');d.canvas.width=1536;d.canvas.height=1024;return d;}
let doc=clone(saved.documents.find(d=>d.id===saved.activeId)??saved.documents[0]??newDraft());
let selected=null,tool='select',undo=[],redo=[],gesture=null,pointers=new Map(),drawing=null,playing=false,time=0,lastFrame=0,saveTimer=null,toastTimer;
let camera={x:0,y:0,w:1600,h:900},lastPanTool='select',libraryData=null,routeView='all';
const currentModuleLibraryClient=new CurrentModuleLibraryClient(location.href);
let libraryPreviewObserver=null,libraryBatchData=null;
let archiveCornerRows=[];
let archiveConfigurationContext=null;
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
function loadDocument(d,cornerRows=[],configurationContext=null){if(drawing)finishDrawing();persist();doc=clone(d);archiveCornerRows=cornerRows;archiveConfigurationContext=configurationContext;selected=null;undo=[];redo=[];time=0;playing=false;$('#time').value=0;$('#play').textContent='▶ 演示';syncFields();setTool('select');fit();persist();}
function syncFields(){$('#title').value=doc.title;$('#description').value=doc.description;$('#constraints').value=doc.constraints;routeView=doc.objects.find(o=>o.type==='route'&&o.sourceRoute==='main')?.id??doc.objects.find(o=>o.type==='route')?.id??'all';renderInspector();renderRevisionInfo();renderCapabilities();renderDifficulty();updateHistory();updateRouteOptions();}
function integrationBadge(status){return `<span class="integration-badge ${esc(status?.usage??'unverified')}">${esc(status?.label??'接入状态待核实')}</span>`;}
function renderRevisionInfo(){
  const s=doc.source,op=doc.intent?.operation??(s?'modify_existing':'new_module'),changes=objectChanges(doc);
  const generated=s?.kind==='generated',archive=doc.intent?.archiveOrigin;
  let html=`<div class="revision-card"><label class="field">本次用途<select id="revision-operation">${generated?option('new_module','生成候选草稿（未接入）',op)+option('new_variant','派生新变体',op):s?option('modify_existing','修改原模块',op)+option('new_variant','基于它新增变体',op):option('new_module','新增模块',op)}</select></label>`;
  if(s){
    const status=archive?{usage:'unverified',label:archive.experimental?'换边试验 · 未认证':'当前库基线 · 技术范围通过',reason:archive.experimental?'这是冻结换边草案的审阅副本，预检或质量阶段不能替代完整认证；不提供给 Map 匹配。':`${archive.mapReady?'通用 Map 接入已认证':'通用 Map 接入未认证'}；人工评审 ${archive.humanReview==='UNKNOWN'?'待评':archive.humanReview}。编辑后的内容需重新验证。`}:s.integration;
    html+=`<div class="revision-source">${archive?'当前库基线':generated?'来源候选':'原模块'}：<b>${esc(s.moduleId)}</b><br>${integrationBadge(status)}<p>${esc(status?.reason??'本草稿尚无当前版本的接入审查信息。')}</p><span>来源版本 ${esc(archive?.contentVersion??s.commit?.slice(0,8)??'本地目录')}</span></div>`;
    if(status?.evidence?.length)html+=`<details class="integration-evidence"><summary>查看接入依据</summary>${status.evidence.map(e=>`<a href="${esc('https://github.com/zhipijun1996/gunman-rush/blob/'+status.checkedCommit+'/'+e.path+'#L'+e.line)}" target="_blank" rel="noopener">${esc(e.path.split('/').at(-1))} ↗</a>`).join('')}<p>依据是来源版本的游戏入口调用链；不表示此修改稿已应用或通过物理验证。</p></details>`;
  }
  if(op==='new_variant')html+=field('新变体建议名称（可留空）','suggestedModuleId',doc.intent?.suggestedModuleId??'');
  html+=`<p class="revision-state">${op==='modify_existing'?'保留原模块身份与引用。':op==='new_variant'?'保留原版，创建独立变体。':'创建新模块。'}本稿尚未写回游戏。</p>`;
  if(changes)html+=`<div class="change-count">新增 ${changes.added.length} · 调整 ${changes.modified.length} · 删除 ${changes.removed.length}${JSON.stringify(doc.capabilityRequirements??emptyRequirements())!==JSON.stringify(doc.baselineCapabilityRequirements??doc.source?.capabilityRequirements??emptyRequirements())?' · 能力要求已调整':''}</div>`;
  if(difficultyChanges(doc)?.changed)html+='<div class="change-count difficulty-change">难度评分已调整</div>';
  if(doc.generationContract){let current=false;try{current=validateGenerationContract(doc).versionMatches;}catch{}const c=doc.generationContract;html+=`<div class="revision-warning" data-contract-state="${current?'current':'stale'}"><b>生成契约：${current?'当前内容版本':'已变更 / 证据不可沿用'}</b><br>${esc(c.contentVersion)}<p>静态检查、物理见证与正式接入分别记录。UNKNOWN 接口不可自动拼装；编辑后需重新导出和验证。</p><p>${c.version===2?`${portCounts(c.ports).physical} 个物理 Port · ${c.ports.length} 个逻辑名`:`${c.ports?.length??0} 个逻辑口（旧合同）`} · 有向关系 ${c.relations?.length??0} · 物理记录 ${c.validations?.filter(v=>v.kind==='physics').length??0}</p></div>`;}
  const corners=archiveCornerRows.length?archiveCornerRows:cornerRelocationRows(doc);
  if(corners.length)html+=`<details class="revision-warning" data-corner-port-options><summary>角落 Port 换边 · ${corners.length} 项${archiveCornerRows.length?'来源版本记录':''}</summary><p>同一 Port 的替代方向，不能同时作为两个出口。未验证的方向不能用于 Map 匹配；编辑后需重新认证。</p>${corners.map(o=>`<p data-corner-option="${esc(o.portId+'/'+o.corner)}" data-relocation-allowed="${o.allowed}"><b>${esc(o.portId)} · ${esc(o.cornerName)}</b>：${esc(FACE_NAMES[o.sourceFace]??o.sourceFace)} → ${esc(FACE_NAMES[o.targetFace]??o.targetFace)}<br>${esc(o.statusLabel)}${o.proposedSurface?' · '+esc(o.proposedSurface):''}${o.reason?'<br><small>'+esc(o.reason)+'</small>':''}</p>`).join('')}</details>`;
  if(archiveConfigurationContext?.receipts.length)html+=`<details class="revision-warning"><summary>打开已认证的接口配置</summary><p>读取离线编译的配置副本；当前草稿先自动保存。</p>${archiveConfigurationContext.receipts.map(r=>`<button data-open-port-configuration="${esc(r.configurationId)}">${esc(r.relocations.map(p=>`${p.portId} → ${FACE_NAMES[p.targetFace]??p.targetFace}`).join('，'))} · ${r.retiredSidePolicy==='preserve_geometry_no_extra_closure'?'不额外封旧口':'历史 v1 配置'}</button>`).join('')}</details>`;
  html+='</div>';$('#revision-info').innerHTML=html;
  $('#revision-operation').onchange=e=>{snapshot();doc.intent={...doc.intent,operation:e.target.value};changed();};
  const input=$('#revision-info [data-prop="suggestedModuleId"]');if(input)input.onchange=()=>{snapshot();doc.intent={...doc.intent,suggestedModuleId:input.value.slice(0,100)};changed();};
  document.querySelectorAll('[data-open-port-configuration]').forEach(button=>button.onclick=async()=>{
    const context=archiveConfigurationContext,receipt=context.receipts.find(r=>r.configurationId===button.dataset.openPortConfiguration);
    button.disabled=true;
    try{
      const reference=await currentModuleLibraryClient.cornerModule(context.entry,receipt),copy=makeRevision(reference,'new_variant');
      copy.title=context.entry.title+' · 接口配置编辑副本';
      copy.intent.archiveOrigin={...doc.intent?.archiveOrigin,configurationId:receipt.configurationId,configurationContentVersion:receipt.configuration.contentVersion};
      loadDocument(copy,[],context);toast('已打开离线认证的接口配置副本');
    }catch(error){button.disabled=false;toast('配置打开失败：'+error.message);}
  });
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
function defs(){return `<defs><pattern id="grid" width="128" height="128" patternUnits="userSpaceOnUse"><path d="M128 0H0V128" fill="none" stroke="#c8cfbc" stroke-width=".65" opacity=".55"/></pattern><pattern id="soil" width="16" height="16" patternUnits="userSpaceOnUse"><path d="M2 5l3-2m5 8l3-2" stroke="#a7af94" stroke-width="1" opacity=".5"/></pattern><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0 0L6 3L0 6" fill="none" stroke="#7395a4" stroke-width="1.2"/></marker><marker id="rail-arrow" markerWidth="7" markerHeight="7" refX="5" refY="3" orient="auto"><path d="M0 0L5 3L0 6" fill="none" stroke="#b49a66" stroke-width="1.2"/></marker></defs>`;}
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
  const label=o.type!=='note'&&o.label&&o.label!=='Local boundary connector'?`<text x="${o.w/2}" y="-12" text-anchor="middle" font-size="12" fill="#7e896e" paint-order="stroke" stroke="#f7f7ee" stroke-width="4">${esc(o.label)}</text>`:'';
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
  const portMarkers=new Set(foundationReview(doc)?doc.generationContract.ports.map(p=>p.objectId):[]);
  const tracks=doc.objects.filter(o=>o.type.startsWith('track')),objects=doc.objects.filter(o=>!o.type.startsWith('track')&&o.type!=='route'&&!portMarkers.has(o.id)),routes=doc.objects.filter(o=>o.type==='route'&&(routeView==='all'||routeView===o.id||o.id===drawing?.id));
  const links=doc.objects.filter(o=>o.targetId).map(o=>{const t=doc.objects.find(t=>t.id===o.targetId);return t?`<path d="M${o.x+o.w/2} ${o.y+o.h/2}L${t.x+t.w/2} ${t.y+t.h/2}" fill="none" stroke="#c1ab70" stroke-width="1" stroke-dasharray="3 6"/>`:'';}).join('');
  let html=links+[...tracks,...objects,...routes].map(o=>objectMarkup(o,interactive)).join('');
  if(time>0){for(const route of routes){const p=pathPoint(route,Math.min(1,time/route.duration));html+=`<g transform="translate(${p.x},${p.y-18})" pointer-events="none"><circle cy="-9" r="7" fill="#46685a"/><path d="M0 -2v14m-9-7L0 0l9 5M0 12l-6 9m6-9 6 9" fill="none" stroke="#46685a" stroke-width="3" stroke-linecap="round"/></g>`;}}
  return html;
}
function render(){
  svg.setAttribute('viewBox',`${camera.x} ${camera.y} ${camera.w} ${camera.h}`);
  const review=foundationReview(doc),grid=$('#block-grid').checked,ports=$('#show-ports').checked,u=camera.w/Math.max(1,svg.clientWidth);
  const background=`<rect x="${camera.x}" y="${camera.y}" width="${camera.w}" height="${camera.h}" fill="#f4f5eb"/>`+(!review&&grid?`<rect x="${camera.x}" y="${camera.y}" width="${camera.w}" height="${camera.h}" fill="url(#grid)" data-draft-block-grid="128"/>`:'');
  svg.innerHTML=defs()+background+contentMarkup()+renderFoundationReview(doc,{unitsPerPixel:u,grid,ports,interactive:true})+selectionMarkup(current());
  if($('#module-review-status'))$('#module-review-status').textContent=review?`${review.widthBlocks}×${review.heightBlocks} Block · ${portCounts(review.ports).physical} 物理 Port / ${review.ports.length} 逻辑名`:'128 px 参考网格 · 设计草稿';
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
  if(!o){$('#selection').innerHTML='<div class="empty-selection"><div class="symbol">↖</div><b>把想法摆到画布上</b><p>点击左侧素材添加物体。<br>选中物体后，在这里调整大小、轨道和说明。</p></div>'+(doc.source?`<div class="source-note">来自原项目模块：${esc(doc.source.moduleId)}<br>打开后可自由修改；原版保留在模块库。<br><a href="${esc('https://github.com/'+(doc.source.repository??'zhipijun1996/gunman-rush')+'/blob/'+doc.source.commit+'/'+doc.source.path)}" target="_blank" rel="noopener">查看原模块 ↗</a></div>`:'');return;}
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
  const review=foundationReview(doc),bs=doc.objects.map(objectBounds);if(review)bs.push({...review.bounds});let x=0,y=0,right=doc.canvas.width,bottom=doc.canvas.height;
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
  const request=changeRequest(doc),purpose=doc.source?`${request.operation==='modify_existing'?'修改原模块':'新增变体'}：${doc.source.moduleId} · 基线 ${(doc.source.commit?.slice(0,8)??'本地目录')} · 尚未写回游戏`:'';
  const lines=wrapText([purpose,difficultySummary(doc.difficulty),doc.difficulty?.note?'评分依据：'+doc.difficulty.note:'','能力要求：'+requirementSummary(doc.capabilityRequirements),doc.capabilityRequirements?.note,doc.description,doc.constraints?'制作时请保留：'+doc.constraints:''].filter(Boolean).join('\n'));
  const w=right-left,h=bottom-top+90+lines.length*22;
  const notes=lines.map((line,i)=>`<text x="${left+35}" y="${bottom+45+i*22}" font-size="15" fill="#64725a">${esc(line)}</text>`).join('');
  return {w,h,text:`<svg xmlns="${NS}" width="${w}" height="${h}" viewBox="${left} ${top} ${w} ${h}"><style>text{font-family:Arial,"Microsoft YaHei",sans-serif}</style>${defs()}<rect x="${left}" y="${top}" width="${w}" height="${h}" fill="#f4f5eb"/><text x="${left+35}" y="${top+45}" font-size="25" font-weight="600" fill="#38634c">${esc(doc.title)}</text><text x="${right-35}" y="${top+44}" font-size="12" text-anchor="end" fill="#89967a">MAP NOTES / 设计草图</text>${contentMarkup(false)}${renderFoundationReview(doc,{unitsPerPixel:1.5,grid:$('#block-grid').checked,ports:$('#show-ports').checked})}<path d="M${left+35} ${bottom+12}H${right-35}" stroke="#cbd3be"/>${notes}<text x="${right-35}" y="${top+h-15}" text-anchor="end" font-size="11" fill="#9ba48d">示意位置 · 预期动作 · 正式制作需验证物理</text><metadata>${esc(JSON.stringify({schema:doc.schema,source:doc.source??null}))}</metadata></svg>`};
}
async function exportImage(){
  finishDrawing();const data=exportSvg();const url=URL.createObjectURL(new Blob([data.text],{type:'image/svg+xml;charset=utf-8'}));
  try{const img=new Image();await new Promise((resolve,reject)=>{img.onload=resolve;img.onerror=reject;img.src=url;});const factor=Math.min(2,4096/Math.max(data.w,data.h));const c=document.createElement('canvas');c.width=Math.ceil(data.w*factor);c.height=Math.ceil(data.h*factor);c.getContext('2d').drawImage(img,0,0,c.width,c.height);const blob=await new Promise(resolve=>c.toBlob(resolve,'image/png'));if(!blob)throw new Error('PNG export failed');download(blob,filename()+'.png');toast('草图已导出，包含关卡说明');}catch{download(new Blob([data.text],{type:'image/svg+xml'}),filename()+'.svg');toast('已导出 SVG 图片，可用浏览器打开');}finally{URL.revokeObjectURL(url);}
}
function dialog(title,html){$('#dialog-title').textContent=title;$('#dialog-body').innerHTML=html;if(!$('#dialog').open)$('#dialog').showModal();}
function showProjects(){
  persist();dialog('我的草稿',`<p>草稿保存在当前浏览器。换设备时用「保存工程」和「打开工程」。</p><div class="dialog-actions"><button id="new-doc" class="primary">＋ Module 草稿</button></div><div>${[...saved.documents].reverse().map(d=>`<div class="draft-row"><button data-open-draft="${esc(d.id)}">${esc(d.title)}<small>${d.objects.length} 个对象 · ${new Date(d.updatedAt).toLocaleDateString('zh-CN')}</small></button><button data-delete-draft="${esc(d.id)}">删除</button></div>`).join('')}</div>`);
  $('#new-doc').onclick=()=>{$('#dialog').close();loadDocument(newDraft());};
  document.querySelectorAll('[data-open-draft]').forEach(b=>b.onclick=()=>{const d=saved.documents.find(d=>d.id===b.dataset.openDraft);$('#dialog').close();loadDocument(d);});
  document.querySelectorAll('[data-delete-draft]').forEach(b=>b.onclick=()=>{if(!confirm('删除这份本机草稿？已导出的工程文件不受影响。'))return;const id=b.dataset.deleteDraft;saved.documents=saved.documents.filter(d=>d.id!==id);if(doc.id===id){doc=newDraft();syncFields();fit();}persist();showProjects();});
}
function batchSummary(data){
  if(!data)return '换边批次状态尚未发布；已认证配置按当前目录显示。';
  const counts=Object.entries(data.counts??{}).map(([status,n])=>stageLabel(status)+' '+n).join(' · ');
  const stamp=data.createdUtc?new Date(data.createdUtc).toLocaleString('zh-CN'):'';
  return `${data.batchId??'当前目录'} · ${data.currentOptions??data.rows.length} 个换边选项 · ${counts||'待开始'}${stamp?' · 快照 '+stamp:''}`;
}
async function showCornerProgress(entry){
  const progress=moduleCornerProgress(libraryBatchData,entry);
  dialog(entry.title+' · 换边进度',`<p>当前目录中 ${progress.certified} 份已认证配置。岩体可按需要改为可穿平台；换边不额外封旧开口，旧位置不作为另一个连接口。</p><p class="review-notice">草案仅供审阅。预检通过不等于完整认证；只有正式目录列出的配置可供匹配。</p><div class="corner-progress-list">${progress.rows.map(row=>`<article class="corner-progress-row" data-corner-batch-key="${esc(row.key)}"><b>${esc(row.portId)} · ${esc(row.corner)} → ${esc(FACE_NAMES[row.targetFace]??row.targetFace)}</b><span data-corner-stage="${esc(row.status)}">${esc(stageLabel(row.status))}</span>${row.failures?.routes||row.failures?.boundaryProbes||row.failures?.counters?`<small>原路线 ${row.failures.routes} 项未通过 · 出入口 ${row.failures.boundaryProbes} 项未通过 · 反例 ${row.failures.counters} 项</small>`:''}${row.reason?`<small class="corner-failure-reason">${esc(row.reason)}</small>`:''}${row.preview?`<button data-open-corner-proposal="${esc(row.key)}">查看冻结换边草案（未认证）</button>`:''}</article>`).join('')||'<p>这个模块尚无当前版本的批次记录。</p>'}</div><button id="back-current-library">返回新版库</button>`);
  $('#back-current-library').onclick=showLibrary;
  document.querySelectorAll('[data-open-corner-proposal]').forEach(button=>button.onclick=async()=>{
    const row=progress.rows.find(r=>r.key===button.dataset.openCornerProposal);button.disabled=true;
    try{const reference=await loadCornerPreview(row,entry,currentModuleLibraryClient.baseURL),copy=makeRevision(reference,'new_variant');
      copy.title=entry.title+' · 换边试验审阅副本';
      copy.intent.archiveOrigin={id:entry.id,moduleId:entry.moduleId,contentVersion:row.preview.contentVersion,technicalStatus:'prepared_unverified',mapReady:false,humanReview:'UNKNOWN',experimental:true,batchId:libraryBatchData.batchId,portId:row.portId,corner:row.corner};
      $('#dialog').close();loadDocument(copy,[],null);toast('已打开未认证换边草案；当前正式模板未改动');
    }catch(error){button.disabled=false;toast('草案打开失败：'+error.message);}
  });
}
async function showMirrorPreview(entry){
  try{
    const reference=await currentModuleLibraryClient.module(entry),status=reference.generationContract?.mirror?.status??'UNKNOWN';
    dialog(entry.title+' · 左右镜像预览',`<p class="review-notice">同一模板的几何方向预览；当前镜像认证状态：${esc(status==='verified'?'已认证':status==='failed'?'未通过':'未验证')}。图中 Port ID、初始权限和路线起止身份保持原样；预览不生成新模板，也不授予物理或 Map 使用资格。</p><div class="mirror-review-figure">${renderMirrorReview(reference)}</div><button id="back-mirror-library">返回新版库</button>`);
    $('#back-mirror-library').onclick=showLibrary;
  }catch(error){toast('镜像预览失败：'+error.message);}
}
async function showLibrary(){
  const client=currentModuleLibraryClient;
  dialog('新版 Module 库','<p>正在读取当前新版模块…</p>');
  try{
    libraryData=await client.load();
    libraryBatchData=null;
    const categoryOf=m=>client.displayCategory(m),countOf=m=>portCounts(m.ports??[]);
    const cats=[...new Set(libraryData.modules.map(categoryOf))];
    const counts=[...new Set(libraryData.modules.map(m=>countOf(m).physical))].sort((a,b)=>a-b);
    const commit=client.snapshotCommit??libraryData.sourceCommit;
    dialog('新版 Module 库',`<div class="library-version"><span>${libraryData.modules.length} 份当前 Module · ${libraryData.designs?.length??0} 份待审设计 · ${commit?`版本 <code>${esc(commit.slice(0,8))}</code>`:'本地目录'}</span><button id="update-library">↻ 更新新版 Module</button></div><p id="repository-library-notice" role="status">来源 modules/catalog.json；待审设计在工坊查看。按物理口计数；打开的是编辑副本。</p><div id="corner-batch-summary" class="batch-summary" role="status">${esc(batchSummary(libraryBatchData))}</div><div class="library-filters"><label class="field">搜索模块<input id="library-search" placeholder="名称 / ID / 动作"></label><label class="field">地区<select id="library-category"><option value="">全部地区</option>${cats.map(c=>option(c,c,'')).join('')}</select></label><label class="field">Map 接入<select id="library-readiness"><option value="">全部状态</option><option value="ready">通用接入已认证</option><option value="pending">通用接入未认证</option></select></label><label class="field">模块难度<select id="library-difficulty"><option value="">全部难度</option><option value="unrated">未评分</option>${DIFFICULTY_LEVELS.map(level=>option(String(level.score),`${level.score} · ${level.name}`,'')).join('')}</select></label><label class="field">物理 Port 数量<select id="library-ports"><option value="">全部物理口</option>${counts.map(n=>option(String(n),`${n} 个物理口`,'')).join('')}</select></label><label class="field">逻辑别名<select id="library-port-aliases"><option value="">全部</option><option value="yes">包含同口别名</option><option value="no">无同口别名</option></select></label><label class="field">角口换边<select id="library-corner-stage"><option value="">全部进度</option><option value="certified">有已认证配置</option><option value="pending">待测 / 处理中</option><option value="failed">失败 / 待修</option></select></label></div><div id="library-results"></div>`);
    const list=()=>{
      libraryPreviewObserver?.disconnect();
      const q=$('#library-search').value.toLowerCase(),cat=$('#library-category').value,difficulty=$('#library-difficulty').value,ports=$('#library-ports').value,ready=$('#library-readiness').value,aliases=$('#library-port-aliases').value,cornerStage=$('#library-corner-stage').value;
      const mods=libraryData.modules.filter(m=>{const n=countOf(m),progress=moduleCornerProgress(libraryBatchData,m),failure=progress.rows.some(r=>['preflight_failed','quality_failed','native_failed','tooling_gap'].includes(r.status)),pending=progress.rows.some(r=>!['verified','preflight_failed','quality_failed','native_failed','tooling_gap'].includes(r.status));return (!cornerStage||(cornerStage==='certified'?progress.certified>0:cornerStage==='failed'?failure:pending))&&(!ports||n.physical===Number(ports))&&(!aliases||(n.logical>n.physical)===(aliases==='yes'))&&(!cat||categoryOf(m)===cat)&&(!ready||m.mapReady===(ready==='ready'))&&(!difficulty||(difficulty==='unrated'?m.difficulty?.score==null:m.difficulty?.score===Number(difficulty)))&&JSON.stringify([m.title,m.id,m.moduleId,m.tags,requirementSummary(m.capabilityRequirements)]).toLowerCase().includes(q);});
      $('#library-results').innerHTML=mods.map(m=>{
        const n=countOf(m),image=client.thumbnail(m),progress=moduleCornerProgress(libraryBatchData,m),aliasGroups=physicalPortGroups(m.ports??[]).filter(p=>p.ids.length>1);
        return `<article class="module-card" data-module="${esc(m.id)}" data-physical-port-count="${n.physical}" data-logical-port-count="${n.logical}"><a class="module-preview" href="${esc(image)}" target="_blank" rel="noopener" title="查看布局预览"><img data-module-preview="${esc(m.id)}" src="${esc(image)}" alt="${esc(m.title)}布局预览" loading="lazy"></a><b>${esc(m.title)}</b><small>${esc(m.moduleId??m.id)}</small><small>${esc(categoryOf(m))} · ${n.physical} 个物理 Port${n.logical!==n.physical?' / '+n.logical+' 个逻辑名':''} · ${m.foundation.widthBlocks}×${m.foundation.heightBlocks} Block</small>${aliasGroups.length?`<small class="port-alias-note">同口别名：${aliasGroups.map(g=>esc(g.ids.join(' = '))).join('；')}</small>`:''}<span class="integration-badge">${m.technicalStatus==='passed_scoped'?'技术范围通过':'待技术验证'} · ${m.deliveryStatus==='ready'?'可交付':'待运行交付验证'}</span><small class="corner-progress-line" data-certified-corner-count="${progress.certified}">角口已认证 ${progress.certified} 份配置${progress.rows.length?' · '+Object.entries(progress.counts).map(([status,n])=>esc(stageLabel(status))+' '+n).join(' / '):' · 无当前批次项'}</small><small>${m.mapReady?'通用 Map 接入已认证':'通用 Map 接入未认证'} · 人工评审 ${esc(m.humanReview==='UNKNOWN'?'待评':m.humanReview)}</small><small class="mirror-status">左右镜像：${progress.mirrorStatus==='verified'?'已认证':progress.mirrorStatus==='failed'?'未通过':'可预览 · 未认证'}</small><small class="module-difficulty">${esc(difficultySummary(m.difficulty))}</small><small>${esc(requirementSummary(m.capabilityRequirements))}</small><div class="module-actions"><button data-copy-module="${esc(m.id)}">打开编辑副本</button><button data-mirror-preview="${esc(m.id)}">左右镜像预览</button><button data-corner-progress="${esc(m.id)}">换边进度</button></div></article>`;
      }).join('')||'<p>没有匹配的当前模块</p>';
      document.querySelectorAll('[data-copy-module]').forEach(button=>button.onclick=async()=>{try{
        const m=libraryData.modules.find(m=>m.id===button.dataset.copyModule);
        const [raw,assessment,receipts]=await Promise.all([client.module(m),client.cornerAssessment(m),client.cornerConfigurations(m)]);
        const reference=validateDocument(raw),corners=cornerRelocationRows(reference,assessment,receipts),d=makeRevision(reference,'new_variant');
        d.title=m.title.slice(0,180)+' · 编辑副本';d.intent.archiveOrigin={id:m.id,moduleId:m.moduleId,contentVersion:m.contentVersion,technicalStatus:m.technicalStatus,mapReady:m.mapReady,humanReview:m.humanReview};
        $('#dialog').close();loadDocument(d,corners,{entry:m,receipts});toast('已打开新版编辑副本，库内原版本保留');
      }catch(error){toast('模块打开失败：'+error.message);}});
      document.querySelectorAll('[data-corner-progress]').forEach(button=>button.onclick=()=>showCornerProgress(libraryData.modules.find(m=>m.id===button.dataset.cornerProgress)));
      document.querySelectorAll('[data-mirror-preview]').forEach(button=>button.onclick=()=>showMirrorPreview(libraryData.modules.find(m=>m.id===button.dataset.mirrorPreview)));
      const observer=libraryPreviewObserver=new IntersectionObserver(entries=>{for(const item of entries)if(item.isIntersecting){observer.unobserve(item.target);const entry=libraryData.modules.find(m=>m.id===item.target.dataset.modulePreview);client.reviewThumbnail(entry).then(url=>{if(item.target.isConnected){item.target.src=url;item.target.closest('a').href=url;}}).catch(()=>{});}}, {root:$('#library-results')});
      document.querySelectorAll('[data-module-preview]').forEach(img=>observer.observe(img));
    };
    for(const selector of ['#library-search','#library-category','#library-difficulty','#library-ports','#library-readiness','#library-port-aliases','#library-corner-stage'])$(selector)[selector==='#library-search'?'oninput':'onchange']=list;
    $('#update-library').onclick=updateCurrentModules;list();
  }catch(error){
    dialog('新版 Module 库',`<p>${esc(error.message)}</p><p>本机草稿保留。</p><div class="dialog-actions"><button id="retry-library">重试</button><button id="fetch-current-library">从仓库更新新版</button></div>`);
    $('#retry-library').onclick=showLibrary;$('#fetch-current-library').onclick=updateCurrentModules;
  }
}
async function updateCurrentModules(){
  persist();dialog('更新新版 Module','<p id="repository-update-status" role="status">正在读取并校验新地基目录…</p>');
  try{
    const result=await currentModuleLibraryClient.checkUpdate((done,total)=>{if($('#repository-update-status'))$('#repository-update-status').textContent=`正在校验 ${done} / ${total}…`;});
    await showLibrary();
    const message=`当前库已更新：共 ${result.total} 份${result.added?'，新增 '+result.added+' 份':''}${result.changed?'，更新 '+result.changed+' 份':''}${result.removed?'，目录移除 '+result.removed+' 份':''}。`;
    if($('#repository-library-notice'))$('#repository-library-notice').textContent=message+' 编辑副本和本机草稿保留。';toast(message);
  }catch(error){
    if(currentModuleLibraryClient.catalog){await showLibrary();if($('#repository-library-notice'))$('#repository-library-notice').textContent='更新失败：'+error.message+'。当前库与草稿保留。';}
    else{dialog('更新新版 Module',`<p>更新失败：${esc(error.message)}</p><p>本机草稿保留。</p><button id="retry-current-update">重试更新</button>`);$('#retry-current-update').onclick=updateCurrentModules;}
  }
}
function help(){dialog('随手画一段关卡',`<ol class="help-list"><li>点击素材盒里的物体，拖到你想放的位置。</li><li>选中物体，在右侧或「设置」里改大小、名称和说明；拖右下角方块也能缩放。</li><li>用「人物路线」逐点画，点「完成绘制」，再填写每一步要做的动作。</li><li>用「轨道」逐点画直线 / 折线；用「弧轨」拖出曲线，拖黄色点调整弧度。轨道起点靠近物体中心时自动绑定，也可在设置中指定。</li><li>点击「演示」或拖时间条，查看机关运动和人物预期路线。</li><li>「模块库」只显示新地基当前 Module。128 px Block 网格与占地线用于审阅，不会添加物理墙；Port 箭头是外法线，同口逻辑别名合并显示。</li><li>「导出图片」发给 Codex；「保存工程」用于换设备、备份或交给 Codex 读取结构。</li></ol><p><kbd>V</kbd> 选择 · <kbd>空格</kbd> 拖动画布 · <kbd>滚轮 / 双指</kbd> 缩放 · <kbd>Ctrl Z</kbd> 撤销 · <kbd>Delete</kbd> 删除</p><p>浏览器自动保存只在本机生效。草图中的动作是设计意图，正式关卡仍需在游戏里验证。</p>`);}
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
$('#block-grid').onchange=render;$('#show-ports').onchange=render;
function animate(now){if(playing){time+=(now-lastFrame)/1000;if(time>20)time=0;$('#time').value=time;$('#time-label').textContent=time.toFixed(1)+'s';render();}lastFrame=now;requestAnimationFrame(animate);}requestAnimationFrame(animate);
$('#projects').onclick=showProjects;$('#library').onclick=showLibrary;$('#update-repository-modules').onclick=updateCurrentModules;$('#help').onclick=help;$('#dialog-close').onclick=()=>$('#dialog').close();
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
