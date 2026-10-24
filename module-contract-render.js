// Standalone version-bound SVG generated from the same Map Notes document.
import {validateGenerationContract,contentVersion,UNKNOWN} from './module-contract.js';
const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
export function renderContractSvg(doc){
 validateGenerationContract(doc);if(contentVersion(doc)!==doc.generationContract.contentVersion)throw Error('Refuse stale contract visualization');
 const c=doc.generationContract,b=c.space.bounds,pad=70,top=180,bottom=170+c.relations.length*23+c.unlocks.length*38+(c.ports.length===3?c.routes.length*23+80:0),left=b.x-pad,width=Math.max(1200,b.w+2*pad),y=b.y-top,height=b.h+top+bottom;
 const rect=(r,extra)=>`<rect x="${r.x}" y="${r.y}" width="${r.w}" height="${r.h}" ${extra}/>`;
 const text=(x,y,t,attrs='')=>`<text x="${x}" y="${y}" ${attrs}>${esc(t)}</text>`;
 const colors={terrain:'#607e69',platform:'#607e69',gear:'#cb773c',spike:'#bd4255',wallSpike:'#bd4255',hazard:'#bd4255',bell:'#b58c23',gate:'#8b5cb6',enemy:'#d25a40',hookHang:'#3b79c9',hookBounce:'#3b79c9'};
 let art=`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="${left} ${y} ${width} ${height}" data-content-version="${esc(c.contentVersion)}"><title>${esc(doc.title)}</title><metadata>${esc(JSON.stringify({schema:doc.schema,id:doc.id,contentVersion:c.contentVersion}))}</metadata><defs><marker id="arrow" markerWidth="9" markerHeight="8" refX="8" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="#177e77"/></marker></defs><style>text{font:17px system-ui,sans-serif;fill:#253b37} .small{font-size:14px}</style>${rect({x:left,y,w:width,h:height},'fill="#faf9f2"')}`;
 art+=text(left+25,y+32,doc.title,'font-weight="700" font-size="24"')+text(left+25,y+60,`${c.kind} · ${doc.id}`,'class="small"')+text(left+25,y+85,c.contentVersion,'class="small"')+text(left+25,y+112,'真实局部世界坐标 · x向右 / y向下 · 标记端口不代表可拼装 · 难度未评分')+text(left+25,y+138,c.kind==='macro'?'虚线=组成路线示意（非整段物理见证）；紫=条件锁；浅青=部件已观测扫掠':'绿=主路见证；金=奖励；蓝=回程；紫=条件锁；浅青=已观测身体扫掠（非完整净空）');
 for(const r of c.space.actionClearance.regions)art+=rect(r,'fill="#4cb8bd" fill-opacity=".09" stroke="none"');
 for(const e of c.space.dynamicEnvelopes)if(e.region!==UNKNOWN)art+=rect(e.region,'fill="#df9a55" fill-opacity=".1" stroke="#b88436" stroke-dasharray="6 4"');
 for(const o of doc.objects){
  if(o.type==='route'||['entry','exit','anchor','note'].includes(o.type))continue;
  if(o.type.startsWith('track')){art+=`<polyline points="${o.points.map(p=>p.x+','+p.y).join(' ')}" fill="none" stroke="#b88436" stroke-dasharray="6 4"/>`;continue;}
  const fill=colors[o.type]??'#888';
  if(o.type==='gear')art+=`<circle cx="${o.x+o.w/2}" cy="${o.y+o.h/2}" r="${o.w/2}" fill="${fill}"/>`;
  else art+=rect(o,`fill="${fill}" fill-opacity=".85" stroke="#ffffff" stroke-width="1" transform="rotate(${o.rotation??0} ${o.x+o.w/2} ${o.y+o.h/2})"`);
  if(['bell','gate','enemy'].includes(o.type))art+=text(o.x,o.y-8,o.label||o.id.split('/').at(-1),'class="small"');
 }
 for(const r of c.routes){const o=doc.objects.find(o=>o.id===r.pathObjectId);const color={main:'#177e77',reward:'#ba8b18',return:'#446db4',recovery:'#5585ba',shortcut:'#9a50ac'}[r.role];art+=`<polyline data-route-id="${esc(r.id)}" points="${o.points.map(p=>p.x+','+p.y).join(' ')}" fill="none" stroke="${color}" stroke-width="3" stroke-dasharray="${c.kind==='macro'||r.evidenceStatus==='failed'?'8 6':'none'}" marker-end="url(#arrow)"/>`;}
 for(const p of c.ports){const [x,yy]=p.position;art+=`<g data-port-id="${esc(p.id)}"><circle cx="${x}" cy="${yy}" r="10" fill="#fff" stroke="#1f635c" stroke-width="3"/><line x1="${x}" y1="${yy}" x2="${x+p.normal[0]*36}" y2="${yy+p.normal[1]*36}" stroke="#1f635c" stroke-width="3"/><text x="${x+12}" y="${yy-26}" font-weight="700">${esc(p.id)}</text></g>`;}
 let line=b.y+b.h+34;art+=text(left+25,line,'有向通行（path仅指列明条件/覆盖；UNKNOWN不提供给自动拼装）','font-weight="700"');line+=28;
 for(const rel of c.relations){const routes=rel.routeIds.map(id=>c.routes.find(r=>r.id===id)?.role).join(',');art+=text(left+25,line,`${rel.from} → ${rel.to} : ${rel.status} ${routes}`);line+=23;}
 art+=text(left+25,line+12,'奖励路线：'+(c.routes.some(r=>r.role==='reward')?'见上方金色标记':'UNKNOWN / 本候选未声明'))+text(left+25,line+38,'回程：'+(c.routes.some(r=>r.role==='return')?'见上方蓝色标记':'UNKNOWN / 未验证；不推断可回去'))+text(left+25,line+64,c.validations.some(v=>v.coverage?.entrySnapshot==='before_first_router_input_after_dynamic_update')?'已记录动作前状态；接缝、进入状态覆盖范围及完整净空仍未验证。':'接缝、进入状态、全状态净空未验证；设计候选，不是正式地图接入证明。');
 if(c.ports.length===3){line+=94;for(const r of c.routes){art+=text(left+25,line,`${r.id} / ${r.from} → ${r.to} / ${r.role} / ${r.evidenceStatus??UNKNOWN}`,'class="small"');line+=23;}}
 let lockY=line+98;for(const u of c.unlocks){art+=text(left+25,lockY,`条件锁 ${u.id}：命中触发器 → 门碰撞关闭 ${u.changes.openSeconds??'UNKNOWN'}s；开启前 ${u.before.status} / 开启后 ${u.after.status}`);lockY+=30;}
 return art+'</svg>';
}
