import {evaluateRequirements} from '../../capabilities.js';
export const FACES={LEFT:'左',RIGHT:'右',TOP:'上',BOTTOM:'下'};
export const STAGES={ARCHIVED:'可运行交付',IMPLEMENTED_CANDIDATE:'已实现 · 待交付验证',READY_FOR_IMPLEMENTATION:'待实现',NEEDS_REPAIR:'待修复',NEEDS_ALIGNMENT:'设计版本待对齐',DESIGN_REVIEW:'待设计审核',IDEA:'创意草稿',DISCARDED:'已废弃'};
export const COMPLETE_STAGES=['ARCHIVED','IMPLEMENTED_CANDIDATE'];
export function matchingRoutes(module,filter={}){
 const ports=new Map(module.ports.map(p=>[p.id,p]));
 const matches=r=>{
  const a=ports.get(r.from),b=ports.get(r.to);if(!a||!b)return false;
  if(a.permission==='OUTPUT'||b.permission==='INPUT')return false;
  if(filter.from&&a.face!==filter.from||filter.to&&b.face!==filter.to)return false;
  const req=r.capabilityRequirements??module.capabilityRequirements??{version:1,status:'unspecified',allOf:[],anyOfGroups:[],note:''};
  if(filter.ability&&!req.allOf.includes(filter.ability)&&!req.anyOfGroups.some(g=>g.includes(filter.ability))&&!(r.requiredAbilities??[]).includes(filter.ability))return false;
  if(filter.available){
   // Some initial one-way permissions were tested with one exact ability set.
   // Extra abilities can invalidate that direction and must not be silently accepted.
   for(const p of [a,b]){const exact=p.initialPermissionConditions?.availableAbilitiesExact;if(exact&&(exact.length!==new Set(filter.available).size||exact.some(x=>!filter.available.includes(x))))return false;}
   if((r.requiredAbilities??[]).some(a=>!filter.available.includes(a)))return false;
   const evaluation=evaluateRequirements(req,filter.available);
   if(evaluation.satisfied===false||evaluation.satisfied===null&&!filter.includeUnknown)return false;
  }
  return true;
 };
 return module.routes.filter(r=>matches(r)&&(!filter.bidirectional||module.routes.some(back=>back.from===r.to&&back.to===r.from&&matchingRoutes({...module,routes:[back]},{...filter,from:filter.to,to:filter.from,bidirectional:false}).length)));
}
export function filterModules(modules,f={}){
 return modules.filter(m=>{
  if(f.stage==='complete'&&!COMPLETE_STAGES.includes(m.stage)||f.stage&&f.stage!=='complete'&&f.stage!==m.stage)return false;
  const b=m.foundation;
  if(f.width&&b.widthBlocks!==Number(f.width)||f.height&&b.heightBlocks!==Number(f.height)||f.ports&&m.ports.length!==Number(f.ports))return false;
  if(f.category&&m.category!==f.category)return false;
  const query=(f.query??'').trim().toLocaleLowerCase();if(query&&!`${m.title} ${m.id} ${m.summary}`.toLocaleLowerCase().includes(query))return false;
  const needsRoute=f.from||f.to||f.ability||f.available||f.bidirectional;
  return !needsRoute||matchingRoutes(m,f).length>0;
 });
}
export function validateDraft(d){
 if(!d||d.sourceType!=='human_idea'||typeof d.id!=='string'||!/^idea-[a-z0-9-]{6,100}$/.test(d.id)||typeof d.verbatim!=='string'||!d.verbatim.trim()||d.verbatim.length>20000||typeof d.title!=='string'||d.title.length>150||d.stage!=='IDEA')throw Error('创意备份格式无效');
 return {id:d.id,sourceType:'human_idea',title:d.title,verbatim:d.verbatim,stage:'IDEA',createdAt:d.createdAt??null,constraints:d.constraints??{},interpretation:null};
}
export function designFeedback(idea,decision,note){
 if(!idea.design||!['KEEP','CHANGE','DISCARD'].includes(decision))throw Error('请选择当前设计版的意见');
 return `Module 工坊 · 设计审阅\n创意：${idea.id}\n标题：${idea.title??idea.id}\n设计版本：${idea.design.version}\n设计文件 SHA256：${idea.design.sha256}\n决定：${{KEEP:'保留',CHANGE:'修改',DISCARD:'废弃'}[decision]}\n意见：${note}\n仅为此设计版本的人工意见，尚不代表已实现或技术验收。`;
}

// Creative work stays here until an exact-version implementation appears in the module library.
export function creativeViews(ideas,modules){
 const views=[];
 for(const idea of ideas){
  const designs=idea.designVariants?.length?idea.designVariants:idea.design?[idea.design]:[null];
  for(const design of designs){
   const approval=design?idea.designApprovals?.[design.version]:null;
   const module=design?modules.find(m=>m.designVersion===design.version&&(approval?m.id===approval.moduleId:(m.sourceIdeaId??m.id)===idea.id)):null;
   if(module&&COMPLETE_STAGES.includes(module.stage))continue;
   const decision=design?(idea.variantDecisions?.[design.version]??(idea.design?.version===design.version?idea.humanApproval:'UNKNOWN')):'UNKNOWN';
   const stage=module?.stage??(!design?(idea.stage==='DISCARDED'?'DISCARDED':'IDEA'):decision==='DISCARD'?'DISCARDED':decision==='KEEP'?'READY_FOR_IMPLEMENTATION':'DESIGN_REVIEW');
   const filterStage=stage==='IDEA'?'TEXT':stage==='DISCARDED'?'DISCARDED':decision==='KEEP'||['READY_FOR_IMPLEMENTATION','NEEDS_REPAIR','NEEDS_ALIGNMENT'].includes(stage)?'WAIT':'REVIEW';
   views.push({...idea,design,stage,filterStage,humanApproval:decision,moduleId:module?.id??approval?.moduleId??null,title:(idea.title||'未命名创意')+(design?.label?' · '+design.label:''),viewKey:idea.id+':'+(design?.version??'text')});
  }
 }
 return views;
}
export function filterCreativeViews(views,stage='ALL'){return views.filter(v=>stage==='ALL'?v.filterStage!=='DISCARDED':v.filterStage===stage);}
