import {emptyRequirements,validateRequirements} from './capabilities.js';
import {emptyDifficulty,validateDifficulty,difficultyChanges} from './difficulty.js';
export const SCHEMA = 'gunman-rush-level-sketch/v1';
export const TYPES = {
  terrain: {name:'地块 / 墙体',group:'地形',w:240,h:96}, platform:{name:'单向平台',group:'地形',w:180,h:18},
  gear:{name:'齿轮',group:'危险',w:64,h:64}, spike:{name:'地刺',group:'危险',w:120,h:24}, wallSpike:{name:'墙刺',group:'危险',w:24,h:120},
  bell:{name:'风铃',group:'机关',w:40,h:52}, switch:{name:'开关',group:'机关',w:38,h:38}, hookBounce:{name:'弹起钩点',group:'机关',w:38,h:38},hookHang:{name:'悬挂钩点',group:'机关',w:38,h:38},mushroom:{name:'弹跳蘑菇',group:'机关',w:64,h:48},
  enemy:{name:'怪物',group:'角色',w:46,h:46},entry:{name:'入口',group:'角色',w:45,h:60},exit:{name:'出口',group:'角色',w:45,h:60},
  note:{name:'文字便签',group:'标注',w:180,h:40},trackLine:{name:'直线轨道',group:'标注',w:160,h:0},trackArc:{name:'弧形轨道',group:'标注',w:160,h:80},route:{name:'人物路线',group:'标注',w:200,h:80}
  ,anchor:{name:'安全锚点',group:'标注',w:10,h:10},hazard:{name:'危险区域',group:'危险',w:120,h:30},gate:{name:'机关门',group:'机关',w:24,h:130},reward:{name:'奖励点',group:'机关',w:42,h:34}
};
export const uid = () => globalThis.crypto?.randomUUID?.() ?? `o-${Date.now()}-${Math.random().toString(36).slice(2)}`;
export const clone = value => JSON.parse(JSON.stringify(value));
export function createObject(type,x,y,extra={}) {
  const t=TYPES[type]; if(!t) throw new Error('未知对象类型');
  const o={id:uid(),type,x,y,w:t.w,h:t.h,rotation:0,label:'',note:'',...extra};
  if(type==='route' || type.startsWith('track')) {
    o.points=extra.points??[{x,y,action:'起跳'},{x:x+160,y:y-80,action:'落地'}];
    o.duration=extra.duration??4; o.mode=extra.mode??'pingpong';
    if(type==='trackArc') o.control=extra.control??{x:x+80,y:y-140};
  }
  return o;
}
export function blankDocument(title='未命名关卡') {
  return {schema:SCHEMA,id:uid(),title,description:'',constraints:'',capabilityRequirements:emptyRequirements(),difficulty:emptyDifficulty(),intent:{operation:'new_module'},canvas:{width:1600,height:900,units:'sketch',positionPrecision:'approximate'},objects:[],updatedAt:new Date().toISOString()};
}
export function makeRevision(reference,operation='modify_existing'){
  if(!reference.source)throw Error('参考模块缺少来源');
  const d=clone(reference);d.id=uid();d.intent={operation};
  d.baselineObjects=clone(reference.objects);
  d.baselineCapabilityRequirements=validateRequirements(reference.capabilityRequirements);
  d.baselineDifficulty=validateDifficulty(reference.difficulty);
  d.title+=' · '+(operation==='modify_existing'?'修改稿':'新变体');
  return d;
}
export function objectChanges(d){
  if(!Array.isArray(d.baselineObjects))return null;
  const before=new Map(d.baselineObjects.map(o=>[o.id,o])),after=new Map(d.objects.map(o=>[o.id,o]));
  return {
    added:[...after.keys()].filter(id=>!before.has(id)),
    removed:[...before.keys()].filter(id=>!after.has(id)),
    modified:[...after.keys()].filter(id=>before.has(id)&&JSON.stringify(before.get(id))!==JSON.stringify(after.get(id)))
  };
}
export function changeRequest(d){
  const operation=d.intent?.operation??(d.source?'modify_existing':'new_module');
  const source=d.source?{repository:d.source.repository,path:d.source.path,moduleId:d.source.moduleId,baseCommit:d.source.commit,method:d.source.method??null,arguments:d.source.arguments??[]}:null;
  return {version:1,operation,target:operation==='modify_existing'?source:null,derivedFrom:source,
    preserveModuleIdentity:operation==='modify_existing',suggestedModuleId:d.intent?.suggestedModuleId??null,
    objectChanges:objectChanges(d),difficulty:validateDifficulty(d.difficulty),difficultyChanges:difficultyChanges(d),capabilityRequirements:validateRequirements(d.capabilityRequirements),
    capabilityChanges:d.source?{before:validateRequirements(d.baselineCapabilityRequirements??d.source.capabilityRequirements),after:validateRequirements(d.capabilityRequirements),changed:JSON.stringify(validateRequirements(d.baselineCapabilityRequirements??d.source.capabilityRequirements))!==JSON.stringify(validateRequirements(d.capabilityRequirements))}:null,applicationStatus:'not_applied',
    instruction:operation==='modify_existing'?'修改 target 指定的原模块，保留模块身份及引用，不新增替代模块；先与最新源码比较。':operation==='new_variant'?'基于 derivedFrom 新增独立变体，不覆盖原模块。':'创建新模块。'};
}
export function exampleDocument(){
  const d=blankDocument('风铃渡口 · 一个空中小冒险');
  d.capabilityRequirements={version:1,status:'defined',allOf:['grapple','shot_recoil'],anyOfGroups:[],note:'设计示例要求；正式制作时验证通关路线。'};
  d.description='越过刺坑，钩住上方休整点，观察齿轮后落到摆渡平台。射击风铃，打开出口。';
  d.constraints='保留上方悬挂观察点；下方平台接住失误；风铃与出口开关联动。所有距离可按真实物理调整。';
  const add=(t,x,y,e)=>{const o=createObject(t,x,y,e);d.objects.push(o);return o;};
  add('terrain',96,570,{w:310,h:150}); add('terrain',1160,470,{w:320,h:250});
  add('terrain',720,730,{w:290,h:72,label:'失误回收'});
  add('platform',442,452,{w:150,label:'起跳台'});add('platform',956,350,{w:140,label:'观察落点'});
  add('spike',408,688,{w:290,h:28});add('wallSpike',1136,550,{w:24,h:140});
  add('entry',160,510,{label:'入口'});const exit=add('exit',1370,410,{label:'出口'});
  add('hookHang',710,270,{label:'悬挂休整'});add('hookBounce',1030,214,{label:'弹起钩点'});
  const rail=add('trackLine',650,520,{points:[{x:650,y:520},{x:1030,y:520}],duration:3,mode:'pingpong',label:'往返 · 两端停顿',dwell:0.5});
  add('platform',590,510,{w:120,h:20,trackId:rail.id,label:'摆渡台'});
  const arc=add('trackArc',850,400,{points:[{x:850,y:400},{x:950,y:260}],control:{x:1020,y:430},duration:2.8});
  add('gear',818,368,{w:64,h:64,trackId:arc.id});
  add('gear',543,560,{w:72,h:72});add('bell',1210,350,{label:'射击开门',targetId:exit.id});
  add('mushroom',820,682,{label:'回收弹跳'});add('enemy',1260,424);
  add('route',220,550,{duration:9,points:[{x:220,y:550,action:'从入口起跳'},{x:510,y:430,action:'落台后向下射击反冲'},{x:730,y:310,action:'钩住并等待齿轮离开'},{x:830,y:500,action:'松钩落到摆渡台'},{x:1040,y:330,action:'起跳到安全落点'},{x:1230,y:445,action:'射击风铃，前往出口'}]});
  add('note',140,290,{w:260,h:50,label:'先看清，再出发。'});
  return d;
}
const finite=v=>typeof v==='number'&&Number.isFinite(v)&&Math.abs(v)<1e7;
export function validateDocument(raw){
  if(!raw || raw.schema!==SCHEMA || !Array.isArray(raw.objects) || raw.objects.length>10000) throw new Error('这不是支持的关卡工程文件');
  if(typeof raw.title!=='string' || raw.title.length>200 || !raw.canvas || !finite(raw.canvas.width)||!finite(raw.canvas.height)||raw.canvas.width<1||raw.canvas.height<1||raw.canvas.width>30000||raw.canvas.height>30000) throw new Error('画布或名称无效');
  if(raw.intent && (!['modify_existing','new_variant','new_module'].includes(raw.intent.operation)|| (raw.intent.operation!=='new_module'&&!raw.source)))throw new Error('修改用途无效');
  if(raw.baselineObjects && (!Array.isArray(raw.baselineObjects)||raw.baselineObjects.length>10000))throw new Error('修改基线无效');
  const capabilityRequirements=validateRequirements(raw.capabilityRequirements);
  const difficulty=validateDifficulty(raw.difficulty);
  if(raw.baselineDifficulty!=null)validateDifficulty(raw.baselineDifficulty);
  if(raw.source?.difficulty!=null)validateDifficulty(raw.source.difficulty);
  if(raw.baselineCapabilityRequirements)validateRequirements(raw.baselineCapabilityRequirements);
  if(raw.source?.capabilityRequirements)validateRequirements(raw.source.capabilityRequirements);
  const ids=new Set();
  for(const o of raw.objects){
    if(!o || typeof o.id!=='string'||ids.has(o.id)||!TYPES[o.type]||![o.x,o.y,o.w,o.h,o.rotation??0].every(finite)||o.w<0||o.h<0)throw new Error('对象数据无效或 ID 重复');
    ids.add(o.id);
    for(const key of ['label','note'])if(o[key]!=null && (typeof o[key]!=='string'||o[key].length>20000))throw new Error('文字数据无效');
    if(o.type==='route'||o.type.startsWith('track')){
      if(!Array.isArray(o.points)||o.points.length<2||o.points.length>5000||o.points.some(p=>!p||!finite(p.x)||!finite(p.y)|| (p.action!=null&&typeof p.action!=='string')))throw new Error('路线数据无效');
      if(!finite(o.duration)||o.duration<=0||o.duration>3600)throw new Error('运动时间无效');
      if(o.dwell!=null&&(!finite(o.dwell)||o.dwell<0||o.dwell>60))throw new Error('停顿时间无效');
      if(o.mode!=null&&!['pingpong','loop','once','sine'].includes(o.mode))throw new Error('运动模式无效');
      if(o.type==='trackArc'&&(!o.control||!finite(o.control.x)||!finite(o.control.y)))throw new Error('弧形轨道无效');
    }
  }
  for(const o of raw.objects){
    if(o.trackId && !raw.objects.some(t=>t.id===o.trackId&&t.type.startsWith('track')))throw new Error('物体绑定的轨道不存在');
    if(o.targetId&&!ids.has(o.targetId))throw new Error('机关关联的目标不存在');
  }
  return clone({...raw,capabilityRequirements,difficulty,id:typeof raw.id==='string'?raw.id:uid(),description:String(raw.description??'').slice(0,20000),constraints:String(raw.constraints??'').slice(0,20000)});
}
export function pathPoint(track,t){
  const ps=track.points;
  t=Math.max(0,Math.min(1,t));
  if(track.type==='trackArc'){
    const a=ps[0],b=ps.at(-1),c=track.control;
    return {x:(1-t)**2*a.x+2*(1-t)*t*c.x+t*t*b.x,y:(1-t)**2*a.y+2*(1-t)*t*c.y+t*t*b.y};
  }
  const lengths=ps.slice(1).map((p,i)=>Math.hypot(p.x-ps[i].x,p.y-ps[i].y));
  const total=lengths.reduce((a,b)=>a+b,0);let remaining=t*total;
  for(let i=0;i<lengths.length;i++){
    if(remaining<=lengths[i]||i===lengths.length-1){const f=lengths[i]?remaining/lengths[i]:0;return {x:ps[i].x+(ps[i+1].x-ps[i].x)*f,y:ps[i].y+(ps[i+1].y-ps[i].y)*f};}
    remaining-=lengths[i];
  }
  return ps[0];
}
export function progressAt(track,time){
  const duration=Math.max(.1,track.duration),dwell=Math.max(0,track.dwell??0);
  const phase=(track.initialPhase??0);
  if(track.mode==='sine')return (Math.sin(Math.PI*2*(time/duration+phase))+1)/2;
  if(track.mode==='once')return Math.min(1,time/duration);
  if(track.mode==='loop')return ((time/duration+phase)%1+1)%1;
  const period=2*(duration+dwell);let t=((time+phase*period)%period+period)%period;
  if(t<dwell)return 0;t-=dwell;if(t<duration)return t/duration;t-=duration;if(t<dwell)return 1;return 1-(t-dwell)/duration;
}
export function translateObject(o,dx,dy){
  o.x+=dx;o.y+=dy;if(o.points)for(const p of o.points){p.x+=dx;p.y+=dy;}if(o.control){o.control.x+=dx;o.control.y+=dy;}
}
export function objectBounds(o){
  if(o.points){const ps=[...o.points,...(o.control?[o.control]:[])];const xs=ps.map(p=>p.x),ys=ps.map(p=>p.y);return {x:Math.min(...xs),y:Math.min(...ys),w:Math.max(...xs)-Math.min(...xs),h:Math.max(...ys)-Math.min(...ys)};}
  const a=(o.rotation??0)*Math.PI/180,co=Math.abs(Math.cos(a)),si=Math.abs(Math.sin(a)),w=o.w*co+o.h*si,h=o.w*si+o.h*co;
  return {x:o.x+o.w/2-w/2,y:o.y+o.h/2-h/2,w,h};
}
