// AND across allOf and every OR group. These are design requirements, not physics proof.
export const ABILITIES={jump:'基础跳跃',shot_recoil:'射击反冲',double_jump:'二段跳',multi_air_shot:'多发空中射击',grapple:'钩索',wall_climb:'蹬墙 / 攀墙',recoil_burst:'爆发反冲'};
export const emptyRequirements=()=>({version:1,status:'unspecified',allOf:[],anyOfGroups:[],note:''});
export const abilityName=id=>ABILITIES[id]??id;
export function validateRequirements(value){
  if(value==null)return emptyRequirements();
  const validList=a=>Array.isArray(a)&&a.length<=50&&a.every(x=>typeof x==='string'&&x.trim()===x&&x.length>0&&x.length<=80)&&new Set(a).size===a.length;
  if(value.version!==1||!['unspecified','partial','defined'].includes(value.status)||!validList(value.allOf)||!Array.isArray(value.anyOfGroups)||value.anyOfGroups.length>20||value.anyOfGroups.some(a=>!validList(a)||!a.length)||typeof value.note!=='string'||value.note.length>4000)throw Error('能力要求格式无效');
  if(value.status==='unspecified'&&(value.allOf.length||value.anyOfGroups.length))throw Error('已有能力条件不能标为未填写');
  return JSON.parse(JSON.stringify(value));
}
export function requirementSummary(value){
  const r=validateRequirements(value);
  if(r.status==='unspecified')return '能力锁未填写';
  const terms=[...r.allOf.map(abilityName),...r.anyOfGroups.map(g=>'（'+g.map(abilityName).join(' 或 ')+'）')];
  return (terms.length?terms.join(' 且 '):r.status==='defined'?'无能力锁':'暂无已声明能力锁')+(r.status==='partial'?' · 尚未确认完整':'');
}
export function evaluateRequirements(value,owned){
  const r=validateRequirements(value),abilities=new Set(owned);
  const missingAll=r.allOf.filter(a=>!abilities.has(a)),missingGroups=r.anyOfGroups.filter(g=>!g.some(a=>abilities.has(a)));
  return {satisfied:missingAll.length||missingGroups.length?false:r.status==='defined'?true:null,missingAll,missingGroups};
}
