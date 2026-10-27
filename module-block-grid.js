// Historical document compatibility only; not a requirement for new Module production.
// Optional extension of generationContract.space; all geometry remains objects.
const directions={W:[-1,0],E:[1,0],N:[0,-1],S:[0,1]};
const need=(ok,message)=>{if(!ok)throw Error('Block contract: '+message);};
const key=p=>p.join(',');
export function validateBlockGrid(doc){
 const g=doc.generationContract.space.blockGrid;if(!g)return;
 need(g.schema==='map-notes/block-grid/v1','schema');const b=g.size;
 need(Number.isSafeInteger(b)&&b>=32&&b%2===0,'even positive Block size');
 need(Array.isArray(g.origin)&&g.origin.length===2&&g.origin.every(x=>Number.isSafeInteger(x)&&x%b===0),'grid origin');
 need(Array.isArray(g.cells)&&g.cells.length>0&&g.cells.every(p=>Array.isArray(p)&&p.length===2&&p.every(Number.isSafeInteger)),'integer cells');
 const cells=new Set(g.cells.map(key));need(cells.size===g.cells.length,'duplicate cell');
 const pending=new Set(cells),queue=[g.cells[0]];pending.delete(key(queue[0]));
 while(queue.length){const [x,y]=queue.pop();for(const [dx,dy]of Object.values(directions)){const p=[x+dx,y+dy];if(pending.delete(key(p)))queue.push(p);}}
 need(pending.size===0,'disconnected footprint');
 need(Array.isArray(g.port_bindings)&&g.port_bindings.length===doc.generationContract.ports.length,'complete port bindings');
 const seen=new Set();
 for(const binding of g.port_bindings){
  const p=doc.generationContract.ports.find(p=>p.id===binding.port_id),d=directions[binding.edge],c=binding.cell;
  need(p&&!seen.has(p.id),'unknown/duplicate port binding');seen.add(p.id);
  need(d&&Array.isArray(c)&&c.length===2&&c.every(Number.isSafeInteger),'cardinal port');
  need(cells.has(key(c))&&!cells.has(key([c[0]+d[0],c[1]+d[1]])),'port must be on actual shape boundary');
  const expected=c.map((v,i)=>g.origin[i]+(v+.5+d[i]*.5)*b);
  need(expected.every((v,i)=>v===p.position[i])&&d.every((v,i)=>v===p.normal[i]),'port boundary center');
  need(typeof binding.profile==='string'&&binding.profile.length>0,'seam profile');
  need(p.grid&&key(p.grid.cell)===key(c)&&p.grid.edge===binding.edge&&p.grid.profile===binding.profile,'port metadata differs');
 }
 const reserves=r=>{for(let x=Math.floor((r.x-g.origin[0]+1e-6)/b);x<=Math.floor((r.x+r.w-g.origin[0]-1e-6)/b);x++)for(let y=Math.floor((r.y-g.origin[1]+1e-6)/b);y<=Math.floor((r.y+r.h-g.origin[1]-1e-6)/b);y++)need(cells.has(key([x,y])),'unreserved object or action space');};
 for(const o of doc.objects){
  const disabledGate=o.type==='gate'&&o.mechanics?.ferryId&&doc.objects.some(p=>p.type==='platform'&&p.trackId&&p.sourceId===o.mechanics.ferryId);
  if(!disabledGate&&['terrain','platform','spike','wallSpike','gate','gear','hazard','bell','reward','enemy'].includes(o.type)&&!o.trackId)reserves(o);
 }
 for(const r of doc.generationContract.space.actionClearance.regions)reserves(r);
 for(const e of doc.generationContract.space.dynamicEnvelopes)if(e.region!=='UNKNOWN')reserves(e.region);
}
