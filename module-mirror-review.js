// A read-only geometry diagram. It never changes or certifies the source Module.
import {validateGenerationContract} from './module-contract.js';
import {renderFoundationReview} from './module-review-overlay.js';
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&apos;'}[c]));
const FACES={LEFT:'RIGHT',RIGHT:'LEFT',TOP:'TOP',BOTTOM:'BOTTOM'};
export function mirrorReviewPorts(doc){
  const c=doc.generationContract,b=c.space.bounds,s=2*b.x+b.w;
  return c.ports.map(p=>({...p,position:[s-p.position[0],p.position[1]],normal:[-p.normal[0]||0,p.normal[1]],face:FACES[p.face],
    ...(p.stagingPosition?{stagingPosition:[s-p.stagingPosition[0],p.stagingPosition[1]]}:{})}));
}
export function renderMirrorReview(doc){
  validateGenerationContract(doc);
  const c=doc.generationContract,b=c.space.bounds,s=2*b.x+b.w,pad=100;
  const colors={terrain:'#607e69',platform:'#8caa8d',gear:'#cb773c',spike:'#bd4255',wallSpike:'#bd4255',hazard:'#bd4255',bell:'#b58c23',gate:'#8b5cb6',enemy:'#d25a40',hookHang:'#3b79c9',hookBounce:'#3b79c9'};
  let out=`<svg xmlns="http://www.w3.org/2000/svg" viewBox="${b.x-pad} ${b.y-pad} ${b.w+2*pad} ${b.h+2*pad}" role="img" data-mirror-preview="geometry-only"><title>${esc(doc.title)} · 左右镜像几何预览（未认证）</title><defs><marker id="mirror-route-arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="#177e77"/></marker></defs><rect x="${b.x-pad}" y="${b.y-pad}" width="${b.w+2*pad}" height="${b.h+2*pad}" fill="#faf9f2"/>`;
  for(const o of doc.objects){
    if(['entry','exit','anchor','note'].includes(o.type))continue;
    if(o.points?.length){out+=`<polyline data-source-object="${esc(o.id)}" points="${o.points.map(p=>`${s-p.x},${p.y}`).join(' ')}" fill="none" stroke="${o.type==='route'?'#177e77':'#b88436'}" stroke-width="${o.type==='route'?3:2}" ${o.type==='route'?'marker-end="url(#mirror-route-arrow)"':'stroke-dasharray="6 4"'}/>`;continue;}
    const x=s-o.x-o.w,fill=colors[o.type]??'#888';
    out+=o.type==='gear'?`<circle data-source-object="${esc(o.id)}" cx="${x+o.w/2}" cy="${o.y+o.h/2}" r="${o.w/2}" fill="${fill}"/>`:`<rect data-source-object="${esc(o.id)}" x="${x}" y="${o.y}" width="${o.w}" height="${o.h}" fill="${fill}" fill-opacity=".85" stroke="#fff" transform="rotate(${-(o.rotation??0)} ${x+o.w/2} ${o.y+o.h/2})"/>`;
    if(['bell','gate','enemy'].includes(o.type))out+=`<text x="${x}" y="${o.y-8}" font-size="14" fill="#253b37">${esc(o.label||o.id.split('/').at(-1))}</text>`;
  }
  const review={...doc,objects:doc.objects.map(o=>({...o,x:s-o.x-o.w,rotation:-(o.rotation??0),...(o.points?{points:o.points.map(p=>({...p,x:s-p.x}))}:{}),...(o.control?{control:{...o.control,x:s-o.control.x}}:{})})),generationContract:{...c,ports:mirrorReviewPorts(doc)}};
  out+=renderFoundationReview(review,{unitsPerPixel:1.15});
  return out+'</svg>';
}
