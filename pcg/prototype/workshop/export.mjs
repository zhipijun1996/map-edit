// Reuse the canonical adapter/validator/renderer; isolated Cell mappings only.
import fs from 'node:fs';
import path from 'node:path';
import {moduleDocument,multiportDocument} from '../../../tools/export-module-contracts.mjs';
import {contentVersion,canonical,sha256,validateGenerationContract,unknownState} from '../../../module-contract.js';
import {validateDocument} from '../../../model.js';
import {renderContractSvg} from '../../../module-contract-render.js';

const [source,out]=process.argv.slice(2),bundle=JSON.parse(fs.readFileSync(source));
fs.mkdirSync(out,{recursive:true});
const groups=new Map();
for(const row of bundle.rows){const key=row.case.layout_uid??row.case.factory_id;if(!groups.has(key))groups.set(key,[]);groups.get(key).push(row);}
const manifest=[];
for(const rows of groups.values()){
 const raw=rows[0].case,doc=raw.ports?multiportDocument(rows,bundle.sourceCommit):moduleDocument(rows[0],bundle.sourceCommit),c=doc.generationContract,id=doc.id;
 doc.title=raw.layout_title??raw.review_alias??raw.family;
 doc.description='内容工坊隔离候选；技术覆盖、视频观感、手动试玩和生产认可分别记录。';
 doc.source.path='pcg/prototype/workshop/rules.py';
 c.generation.parameters.producerArguments=raw.generation_rule;
 c.generation.source.workshopSpecification=raw.map_specification??'UNKNOWN';
 c.generation.source.ideaIds=raw.idea_ids??[];
 c.seed={status:'not_used',value:null,reason:'Deterministic registered rules; phase/noise seeds are validation only'};
 const geometry=[];
 for(const [i,s]of(raw.reward_sites??[]).entries()){
  const o={id:id+'/cache-'+i,type:'reward',x:s.position[0]-18,y:s.position[1]-18,w:36,h:36,rotation:0,label:'宝箱 '+s.amount,note:'原 SimpleRoomReward 受支持接触后提交金币；可见不等于已领取',mechanics:{kind:'chest',service:'SimpleRoomReward',amount:s.amount,source:s}};
  doc.objects.push(o);geometry.push(o);
 }
 for(const [i,l]of(raw.latches??[]).entries()){
  const bell=doc.objects.find(o=>o.id===id+'/bell-'+i),gate=doc.objects.find(o=>o.id===id+'/gate-'+i);
  bell.sourceId=l.id;gate.mechanics={kind:l.ferry_id?'carrier_control':'timed_gate',openSeconds:l.open_seconds,carrierId:l.ferry_id??null,returnAccess:l.return_access??null};
  if(l.ferry_id){
   const carrier=doc.objects.find(o=>o.sourceId===l.ferry_id);bell.targetId=carrier.id;
   carrier.mechanics={control:'original ShotLatch.bind_motion start/pause',initialRunning:false,clock:'original ModuleMovingPlatform.motion_clock',bellId:bell.id};
   c.unlocks[i].changes={objectId:carrier.id,motion:'toggle original motion_running; no new behavior',originalGateNotRendered:true};
   gate.note='原 ShotLatch motion_mode 的隔离碰撞占位，已禁用；不是通路门';gate.mechanics.collision='disabled_by_original_bind_motion';
  }
  if(l.return_access){const p=l.return_access,o={id:id+'/return-bell-'+i,type:'bell',x:p[0]-14,y:p[1]-17,w:28,h:34,rotation:0,label:'返回侧接收器',note:'原 add_access_bell，与主铃共享事务',targetId:bell.targetId,sourceId:l.id+'/return',mechanics:{service:'ShotLatch.add_access_bell',returnSideOnly:true}};doc.objects.push(o);geometry.push(o);}
 }
 for(const o of geometry){c.space.occupancy.objectIds.push(o.id);c.composition.cells.push({id:o.id,contentVersion:'sha256:'+sha256(canonical(o)),objectIds:[o.id]});}
 // Changed mechanism metadata also changes the Cell identity.
 for(const cell of c.composition.cells){const os=cell.objectIds.map(id=>doc.objects.find(o=>o.id===id));cell.contentVersion='sha256:'+sha256(canonical(os.length===1?os[0]:os));}
 c.designStatus='declared';c.generation.parameters.workshop=raw.rule_parameters;
 for(const port of c.ports){port.motion={ingress:{directions:'UNKNOWN',modes:'UNKNOWN'},egress:{directions:'UNKNOWN',modes:'UNKNOWN'}};}
 for(const route of c.routes){route.transfer.requires=unknownState();route.transfer.ensures=unknownState();route.return.status='UNKNOWN';}
 c.validations.forEach(v=>{v.coverage.workshopCausal=rows.find(r=>(r.case.route_spec?.id??'main')===v.routeId)?.workshopPurpose??'UNKNOWN';v.coverage.wholeMap=false;});
 const xs=doc.objects.filter(o=>!o.points),b=c.space.bounds;
 const x=Math.min(b.x,...xs.map(o=>o.x)),y=Math.min(b.y,...xs.map(o=>o.y));
 c.space.bounds={x,y,w:Math.max(b.x+b.w,...xs.map(o=>o.x+o.w))-x,h:Math.max(b.y+b.h,...xs.map(o=>o.y+o.h))-y};
 doc.canvas.width=c.space.bounds.w;doc.canvas.height=c.space.bounds.h;
 c.contentVersion=contentVersion(doc);c.visualization.contentVersion=c.contentVersion;
 c.validations.forEach(v=>v.contentVersion=c.contentVersion);c.staticChecks.contentVersion=c.contentVersion;
 validateDocument(doc);validateGenerationContract(doc);
 const file=doc.id+'.mapnote.json';fs.writeFileSync(path.join(out,file),JSON.stringify(doc,null,2));
 fs.writeFileSync(path.join(out,doc.id+'.svg'),renderContractSvg(doc));
 manifest.push({id:doc.id,file,contentVersion:c.contentVersion,family:raw.family,portCount:c.ports.length,productionAdmitted:false});
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify({schema:'pcg/workshop-delivery/v1',modules:manifest,productionAdmitted:false},null,2));
console.log(JSON.stringify({exported:manifest.length,out}));
