'use strict';
const labels={fun:'趣味',clarity:'可读性',fairness:'公平性',replay_value:'重玩意愿',difficulty:'感受难度'};
const form=document.querySelector('#review-form'), game=document.querySelector('#game');
for(const [name,label]of Object.entries(labels)){
 const row=document.createElement('div');row.className='rating';const text=document.createElement('span');text.textContent=label;row.append(text);
 const options=document.createElement('div');options.className='rating-options';
 for(let i=1;i<=5;i++){const el=document.createElement('label'),input=document.createElement('input'),value=document.createElement('b');input.type='radio';input.name=name;input.value=i;input.required=true;value.textContent=i;el.append(input,value);options.append(el);}row.append(options);document.querySelector('#ratings').append(row);
}
let catalog, current=null, storageKey, saved=[], trials=new Map();
const sessionId=crypto.randomUUID();
const testMode=new URLSearchParams(location.search).get('test_mode')==='1';
function store(){try{localStorage.setItem(storageKey,JSON.stringify(saved));}catch{document.querySelector('#feedback-status').textContent='浏览器本地保存不可用，请在离开前导出文件。';}}
function renderSaved(){
 const box=document.querySelector('#saved');box.replaceChildren();
 if(!saved.length)box.textContent='尚无评价。';
 for(const s of saved){const el=document.createElement('article');el.textContent=`${s.alias} · ${s.reviewer_code} · 趣味 ${s.fun}/5 · 已保存`;box.append(el);}
 document.querySelector('#export').disabled=!saved.length;
}
function manualTrials(){return current?[...trials.values()].filter(t=>t.candidate_uid===current.candidate_uid&&t.mode==='manual'&&t.frames>=30&&t.input_events>=1):[];}
function update(){
 if(!current||!catalog)return;
 const m=catalog.review_modules.find(x=>x.uid===current.candidate_uid&&x.module_sha256===current.module_sha256);
 if(!m)return;
 document.querySelector('#candidate').textContent=m.alias;
 const attempts=manualTrials();document.querySelector('#attempt').textContent=attempts.length?`已记录 ${attempts.length} 次亲自操作。当前 ${current.mode==='manual'?'手动':'程序回放'} · ${current.frames} 帧 · HP ${current.hp}。未通关也可以评价。`:'请在游戏中亲自操作至少半秒；只看 Replay 不能提交体验评价。';
 document.querySelector('#save').disabled=!attempts.length;
 if(saved.some(s=>s.candidate_uid===current.candidate_uid)){
  const row=catalog.candidates.find(x=>x.uid===current.candidate_uid);document.querySelector('#technical-result').textContent=JSON.stringify({engineering_tier:row.admission.engineering_tier,validation:row.validation,scope:'自动输入策略表现；不是人类成功率或趣味结论'},null,2);
 }else document.querySelector('#technical-result').textContent='先保存自己的评价，再查看自动测试结果，避免影响第一印象。';
}
window.addEventListener('message',event=>{
 if(event.origin!==location.origin||event.source!==game.contentWindow||event.data?.type!=='pcg-factory-state')return;
 const state=event.data.payload;
 if(!catalog||!state||!catalog.review_modules.some(m=>m.uid===state.candidate_uid&&m.module_sha256===state.module_sha256))return;
 if(current?.candidate_uid!==state.candidate_uid){for(const input of form.querySelectorAll('input[type=radio],input[type=checkbox]'))input.checked=false;form.notes.value='';}
 current=state;const key=sessionId+':'+state.attempt_id;
 if(state.mode==='manual')trials.set(key,{...state,session_id:sessionId});
 update();
});
form.addEventListener('submit',event=>{
 event.preventDefault();if(!current||!form.reportValidity()||!manualTrials().length)return;
 const values=new FormData(form);const value={schema:'pcg/human-feedback/v1',source_kind:testMode?'synthetic_test':'human_self_report',catalog_sha256:catalog.catalog_sha256,candidate_uid:current.candidate_uid,module_sha256:current.module_sha256,alias:current.alias,session_id:sessionId,reviewer_code:values.get('reviewer_code'),input_device:values.get('input_device'),skill:Number(values.get('skill')),flags:values.getAll('flag'),notes:values.get('notes'),manual_attempts:manualTrials(),submitted_at:new Date().toISOString(),evidence_trust:'unsigned_client_self_report_requires_curator_confirmation'};
 for(const name of Object.keys(labels))value[name]=Number(values.get(name));
 // One current response per reviewer/module; imports remain hash-deduplicated.
 saved=saved.filter(s=>s.candidate_uid!==value.candidate_uid||s.reviewer_code!==value.reviewer_code);saved.push(value);store();renderSaved();update();document.querySelector('#feedback-status').textContent='已保存到当前浏览器。请导出反馈文件并发回；尚未上传或批准。';
});
document.querySelector('#export').addEventListener('click',()=>{
 const data={schema:'pcg/feedback-export/v1',catalog_sha256:catalog.catalog_sha256,submissions:saved};const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download='module-feedback-'+catalog.run_id+'.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
});
fetch('catalog.json').then(r=>{if(!r.ok)throw Error('质量档案读取失败');return r.json();}).then(data=>{
 catalog=data;storageKey='pcg-module-review:'+catalog.catalog_sha256+(testMode?':test-only':'');
 try{saved=JSON.parse(localStorage.getItem(storageKey)||'[]');if(!Array.isArray(saved))saved=[];}catch{saved=[];}
 document.querySelector('#summary').textContent=(testMode?'合成测试模式（不计入真人反馈） · ':'')+`本轮 ${catalog.review_modules.length} 个技术合格待评样例 · 真人回收 ${catalog.human_feedback_count} · 已批准离线模块 ${catalog.approved_offline_count}。自动筛选使用独立相位、输入扰动及有限替代策略。`;
 renderSaved();update();
}).catch(error=>{document.querySelector('#summary').textContent=String(error);});
