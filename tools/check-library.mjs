import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {validateDocument,pathPoint,progressAt} from '../model.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const catalog=JSON.parse(fs.readFileSync(path.join(root,'library/catalog.json')));
const coverage=JSON.parse(fs.readFileSync(path.join(root,'library/coverage.json')));
assert.equal(new Set(catalog.modules.map(m=>m.id)).size,catalog.modules.length);
assert.equal(catalog.modules.length,coverage.total);
const resources=JSON.parse(fs.readFileSync(path.join(root,'library/source/module-index.json')));
for(const source of resources)assert(catalog.modules.some(m=>m.id===source.name.replace('.tres','')),'Missing authored module '+source.name);
for(const module of catalog.modules){
  const bytes=fs.readFileSync(path.join(root,module.file));
  assert.equal(crypto.createHash('sha256').update(bytes).digest('hex'),module.contentSha256);
  const doc=validateDocument(JSON.parse(bytes));
  assert(doc.source.integration && ['formal','development','not_integrated','unverified'].includes(doc.source.integration.usage));
  assert.deepEqual(doc.source.integration,module.integration);
  assert.equal(doc.source.integration.checkedCommit,catalog.sourceCommit);
  assert([true,false,null].includes(module.integration.isIntegrated));
  assert(['平原','森林','通用','工坊'].includes(module.category));
  assert.deepEqual(validateDocument(JSON.parse(JSON.stringify(doc))),doc);
  assert.equal(doc.objects.length,module.objectCount);
  assert(fs.existsSync(path.join(root,module.thumbnail)));
  const original=doc.source.original;
  if(doc.source.kind==='resource'){
    const [dx,dy]=doc.source.editorTranslation;
    for(let i=0;i<original.platforms.length;i++){
      const obj=doc.objects.find(o=>o.sourceIndex===i),rect=original.platforms[i];
      assert.deepEqual([obj.x-dx,obj.y-dy,obj.w,obj.h],rect,'Source platform geometry must be preserved');
    }
    for(const saw of original.saws){
      const obj=doc.objects.find(o=>o.sourceId===saw.source_id),track=doc.objects.find(o=>o.id===obj.trackId);
      for(const time of [0,.17,.9,2.1,5.7]){
        let x=obj.x,y=obj.y;
        if(track){const p=pathPoint(track,progressAt(track,time)),initial=pathPoint(track,progressAt(track,0));x+=p.x-initial.x;y+=p.y-initial.y;}
        const expected=saw.origin.map((v,i)=>v+saw.travel[i]*Math.sin(2*Math.PI*(time/saw.period+saw.initial_phase)));
        assert(Math.abs(x+obj.w/2-dx-expected[0])<1e-6,'Saw X trajectory drift');
        assert(Math.abs(y+obj.h/2-dy-expected[1])<1e-6,'Saw Y trajectory drift');
      }
    }
  }
}
// A malformed engineering file must not silently lose bindings.
const good=JSON.parse(fs.readFileSync(path.join(root,catalog.modules[0].file)));
const bad=structuredClone(good);bad.objects[0].trackId='missing';assert.throws(()=>validateDocument(bad));
console.log(`Library checked: ${catalog.modules.length} editable documents; ${resources.length} authored resources fully covered; original platforms, saw trajectories, links and round trips preserved.`);
