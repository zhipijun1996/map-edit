// Extend the canonical Workshop exporter with the original sequence receiver
// and removable first gate, both real collision entities in the run.
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {contentVersion,canonical,sha256,validateGenerationContract} from '../../../../module-contract.js';
import {validateDocument} from '../../../../model.js';
import {renderContractSvg} from '../../../../module-contract-render.js';
const [source,out]=process.argv.slice(2);
execFileSync('node',[new URL('../../workshop/export.mjs',import.meta.url).pathname,source,out],{stdio:'inherit'});
const bundle=JSON.parse(fs.readFileSync(source));const manifest=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
for(const entry of manifest.modules){
 const file=path.join(out,entry.file),doc=JSON.parse(fs.readFileSync(file));
 const row=bundle.rows.find(r=>'generated-'+r.case.factory_id===doc.id);if(!row)throw new Error('source row not found');
 const raw=row.case,c=doc.generationContract;
 doc.source.path=raw.rule_source_path??'UNKNOWN';
 for(const [i,l]of(raw.latches??[]).entries()){
  if(!l.sequence_offset)continue;
  const bell=doc.objects.find(o=>o.id===doc.id+'/bell-'+i),gate=doc.objects.find(o=>o.id===doc.id+'/gate-'+i);
  const p=[l.bell[0]+l.sequence_offset[0],l.bell[1]+l.sequence_offset[1]],g=l.sequence_gate??[0,0,0,0];
  const receiver={id:doc.id+'/sequence-bell-'+i,type:'bell',x:p[0]-14,y:p[1]-17,w:28,h:34,rotation:0,label:'有序第二铃',sourceId:l.id+'/second',targetId:gate.id,note:'原 ShotLatch 第二接收器；sequence_step=1 才接受真实投射物',mechanics:{service:'ShotLatch',sequenceStep:2,sharesHealthWith:bell.id}};
  const firstGate={id:doc.id+'/sequence-gate-'+i,type:'gate',x:g[0],y:g[1],w:g[2],h:g[3],rotation:0,label:'第一铃移除隔断',sourceId:l.id+'/sequence-gate',note:'真实原ShotLatch.sequence_gate_rect；第一铃提交后去除碰撞',mechanics:{service:'ShotLatch.restore_sequence_gate',removedAtSequenceStep:1}};
  bell.mechanics={service:'ShotLatch',sequenceStep:1,targetId:(g[2]>0&&g[3]>0?firstGate.id:gate.id)};gate.mechanics={service:'ShotLatch',kind:'permanent_sequence_gate',requiresSequenceStep:2};
  for(const o of [receiver,...(g[2]>0&&g[3]>0?[firstGate]:[])]){doc.objects.push(o);c.space.occupancy.objectIds.push(o.id);c.composition.cells.push({id:o.id,contentVersion:'sha256:'+sha256(canonical(o)),objectIds:[o.id]});}
  c.unlocks.push({id:doc.id+'/first-sequence-unlock-'+i,trigger:{objectId:bell.id,condition:'original accepted projectile while sequence_step=0'},changes:{objectId:(g[2]>0&&g[3]>0?firstGate.id:bell.id),collision:(g[2]>0&&g[3]>0?'disabled':'unchanged'),sequenceStep:1},before:{from:'entry',to:'exit',status:'UNKNOWN',conditions:[{field:'mechanisms.'+l.id+'.sequence_step',op:'eq',value:0}]},after:{from:'entry',to:'exit',status:'UNKNOWN',conditions:[{field:'mechanisms.'+l.id+'.sequence_step',op:'eq',value:1}]}});
  c.unlocks[i].trigger={objectId:receiver.id,condition:'original accepted projectile while sequence_step=1'};
 }
 for(const cell of c.composition.cells){const os=cell.objectIds.map(id=>doc.objects.find(o=>o.id===id));cell.contentVersion='sha256:'+sha256(canonical(os.length===1?os[0]:os));}
 c.contentVersion=contentVersion(doc);c.visualization.contentVersion=c.contentVersion;c.validations.forEach(v=>v.contentVersion=c.contentVersion);c.staticChecks.contentVersion=c.contentVersion;
 validateDocument(doc);validateGenerationContract(doc);
 fs.writeFileSync(file,JSON.stringify(doc,null,2));fs.writeFileSync(path.join(out,doc.id+'.svg'),renderContractSvg(doc));entry.contentVersion=c.contentVersion;
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(manifest,null,2));
