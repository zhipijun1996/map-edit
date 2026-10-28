// Original sequence object mapping, with the authored timed mode explicit.
import fs from 'node:fs';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {contentVersion,canonical,sha256,validateGenerationContract} from '../../../../module-contract.js';
import {validateDocument} from '../../../../model.js';
import {renderContractSvg} from '../../../../module-contract-render.js';
const[source,out]=process.argv.slice(2);
execFileSync('node',[new URL('../resource_routes/export-v4.mjs',import.meta.url).pathname,source,out],{stdio:'inherit'});
const b=JSON.parse(fs.readFileSync(source)),m=JSON.parse(fs.readFileSync(path.join(out,'manifest.json')));
for(const e of m.modules){
 const p=path.join(out,e.file),d=JSON.parse(fs.readFileSync(p)),raw=b.rows.find(r=>'generated-'+r.case.factory_id===d.id).case,c=d.generationContract;
 for(const[i,l]of raw.latches.entries()){
  const g=d.objects.find(o=>o.id===d.id+'/gate-'+i);g.mechanics={...g.mechanics,kind:'timed_sequence_gate',openSeconds:l.open_seconds,antiPinch:'original ShotLatch.grow(24)'};
 }
 for(const cell of c.composition.cells){const os=cell.objectIds.map(id=>d.objects.find(o=>o.id===id));cell.contentVersion='sha256:'+sha256(canonical(os.length===1?os[0]:os));}
 c.contentVersion=contentVersion(d);c.visualization.contentVersion=c.contentVersion;c.validations.forEach(v=>v.contentVersion=c.contentVersion);c.staticChecks.contentVersion=c.contentVersion;
 validateDocument(d);validateGenerationContract(d);fs.writeFileSync(p,JSON.stringify(d,null,2));fs.writeFileSync(path.join(out,d.id+'.svg'),renderContractSvg(d));e.contentVersion=c.contentVersion;
}
fs.writeFileSync(path.join(out,'manifest.json'),JSON.stringify(m,null,2));
