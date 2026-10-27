"""Read-only review derived from the actual compiled graph/world and traces."""
import argparse,copy,gzip,hashlib,html,json,shutil,subprocess
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.map_directed.block_grid.policy import review,load

def build(run,probes,capture,out,movies):
    run,probes,capture,out=map(Path,[run,probes,capture,out]);out.mkdir(parents=True,exist_ok=False)
    c=json.loads((run/'compiled.json').read_text());g=c['exploration_graph'];s=json.loads((run/'summary.json').read_text());p=json.loads((probes/'summary.json').read_text());cs=json.loads((run/'cases.json').read_text())['cases'];rows=[]
    batches=json.loads((run/'physics/batches.json').read_text())
    for row,b in zip(s['rows'],batches):
        raw=gzip.decompress((run/'physics'/b['gzip_path']).read_bytes());assert hashlib.sha256(raw).hexdigest()==b['raw_output_sha256'];r=json.loads(raw)['results'][0];fs=r['frames'];n=len(fs)
        rows.append(dict(id=row['id'],passed=row['ok'],seconds=n/60,shots=row['shots'],airborne_fraction=sum(not f['grounded']for f in fs)/n,ground_moving_fraction=sum(f['grounded']and abs(f.get('vx',0))>10 for f in fs)/n,near_stationary_fraction=sum(abs(f.get('vx',0))<5 and abs(f.get('vy',0))<5 for f in fs)/n,actual_items=r['extra']['items'],boss_defeated=all(q['dead']for q in r['extra']['bosses']),scope='One input program, not human timing or fun'))
    bounds=cs[0]['overview_bounds'];x,y,w,h=bounds;palette=['#ffbd59','#60d7ff','#f58dcb','#a2ed8c','#d0b1ff'];svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x-80} {y-80} {w+160} {h+160}" role="img" aria-label="Actual Module placements and original exploration edges">','<rect x="-100000" y="-100000" width="200000" height="200000" fill="#102230"/>']
    for i,r in enumerate(c['case']['platforms']):
        px,py,pw,ph=r;svg.append(f'<rect x="{px}" y="{py}" width="{pw}" height="{ph}" fill="{ "#78928b"if i not in c["case"]["one_way_platform_indices"]else"#9c996b"}"/>')
    centers={k:v['center']['position']for k,v in c['nodes'].items()}
    for i,e in enumerate(g['edges']):
        a,b=[centers[e[k]]for k in ['from','to']];svg.append(f'<path d="M {a[0]} {a[1]} L {b[0]} {b[1]}" fill="none" stroke="#718c9a" stroke-width="7" opacity=".6"/>')
    tours=[dict(name='主路 '+str(i+1),nodes=q['nodes'])for i,q in enumerate(g['principal_routes'])]+[dict(name=b['kind'],nodes=[b['entry']]+b['nodes']+b.get('return_nodes',[])+[b.get('rejoin',b['entry'])])for b in g['branches']]
    for i,t in enumerate(tours):
        pts=' '.join(','.join(map(str,centers[k]))for k in t['nodes']);svg.append(f'<polyline data-route="{i}" points="{pts}" fill="none" stroke="{palette[i%len(palette)]}" stroke-width="12" stroke-linejoin="round" opacity=".8"/>')
    for k,q in centers.items():
        svg.append(f'<circle cx="{q[0]}" cy="{q[1]}" r="23" fill="#102230" stroke="#fff" stroke-width="4"/><text x="{q[0]+30}" y="{q[1]-24}" fill="white" font-family="sans-serif" font-size="48">{html.escape(k)}</text>')
    svg.append('</svg>');(out/'layout.svg').write_text(''.join(svg));shutil.copy2(capture,out/'whole-map.png')
    media=[]
    for i,m in enumerate(movies):
        m=Path(m);manifest=json.loads((m/'manifest.json').read_text());assert manifest['comparison']['passed'];name=['main-a.mp4','main-b.mp4','reward-loop.mp4'][i];shutil.copy2(m/manifest['file'],out/name);media.append(dict(manifest,file=name))
    actual=[]
    for m in c['modules']:
        actual.append(dict(node=m['id'],family=m.get('selection_family'),ports=len(m['ports']),position=m['spec']['placement'],source_version=m['source_version'],content_version=m['content_version'],nonlevel_ports=len({p['position'][1]for p in m['ports'].values()})>1,rocks=len(m['case']['platforms'])-len(m['case']['one_way_platform_indices']),one_way_platforms=len(m['case']['one_way_platform_indices']),latches=len(m['case'].get('latches',[])),enemies=len(m['case'].get('enemies',[])),saws=len(m['case'].get('saws',[]))))
    full=review(g,load(),physical=s)
    full['separate_actual_boss_evidence']='All10 whole-world routes defeat real Bellstrider; logical node encounter_verified was deliberately not mutated'
    independent=json.loads((REPO/'pcg/results/graph-map-bounded-seeds-v1/summary.json').read_text())
    result=dict(schema='pcg/graph-map-review/v1',independent_seed_audit=independent,source_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),physics_run=str(run),compiled_sha256=hashlib.sha256((run/'compiled.json').read_bytes()).hexdigest(),macro_placements=len(c['modules']),actual_module_components=s['actual_module_components'],seams=len(c['seams']),assembly=json.loads((run/'assembly-audit.json').read_text()),blueprint=c['blueprint_correspondence'],principal_routes=g['principal_routes'],branches=g['branches'],actual_modules=actual,distinct_selected_families=len({m['family']for m in actual}),route_metrics=rows,one_way_probes=dict(passed=p['passed'],total=p['total'],bypasses=p['bypasses'],inconclusive=p['inconclusive'],scope='Three finite reverse-input strategies per directed seam, not universal proof'),full_region_acceptance=full,media=media,production_admitted=False,human_fun='UNREVIEWED',design_quality='NOT_ACCEPTED: repeated terraces/steps, uneven action density',economic_balance='UNCALIBRATED')
    write(out/'results.json',result)
    table=''.join('<tr>'+''.join('<td>'+html.escape(str(row[k]))+'</td>'for k in ['id','passed','seconds','shots','actual_items'])+'</tr>'for row in rows)
    opts=''.join(f'<button onclick="route({i})" style="border-color:{palette[i%len(palette)]}">{html.escape(t["name"])}</button>'for i,t in enumerate(tours))
    vids=''.join(f'<section><h3>{html.escape(label)}</h3><video controls preload="metadata" src="{v["file"]}"></video><a href="{v["file"]}" download>下载完整原速录像</a></section>'for label,v in zip(['主路一 + 实际Boss','主路二 + 实际Boss','可选奖励挑战 + 单向环回 + Boss'],media))
    page='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>同图驱动风铃平原Map</title><style>body{max-width:1100px;margin:32px auto;padding:0 16px;background:#101c26;color:#e8edf0;font:16px/1.7 sans-serif}a{color:#73d5ff}img,video,object{width:100%;height:auto}object{aspect-ratio:1.6}button{padding:9px;background:#243641;color:white;margin:4px;border:2px solid}td,th{padding:7px;border-bottom:1px solid #40505c}table{font-size:13px;width:100%}.note{padding:16px;border-left:4px solid #ffbf64;background:#293136}</style><h1>同一张探索图 → 实际拼装Map</h1><p>22 Macro / 24 实际Module / 24零间隙接缝。2条主路，折返、单向环回、汇合三类奖励支路；实际道具、商店和Bellstrider。程序输入回放，正式游戏未改。</p><p class="note">当前是小规模接口验收样图，未达40–65 Module区域目标。10/10常规路线和9/9有限反向门体探针通过；这不代表美感、趣味、经济平衡或人类7–10分钟通过。画面仍有重复台阶、长岩台与挑战分布不均。两个新小图Seed和一个新完整区域Seed均未在固定预算内完成空间拼装，未达到稳定产出。</p><p><a href="index.html">打开同一地图手动试玩</a> · A/D移动 · 空格跳跃 · 鼠标松开射击反冲 · E购买 · M整图 · R重试</p><h2>真实Godot整图截图</h2><a href="whole-map.png"><img src="whole-map.png" alt="实际完整地图，初始状态，未移动玩家"></a><h2>实际坐标上的节点 / 路线对应</h2><p>以下是物理地形的示意图，节点位置来自真实拼装；连线仅说明探索职责，不是额外平台。</p>OPTIONS<object id="layout" data="layout.svg" type="image/svg+xml"></object><h2>关键路线录像</h2>VIDEOS<h2>真实路线记录</h2><table><tr><th>路线</th><th>通过</th><th>自动秒数</th><th>射击</th><th>实际道具</th></tr>TABLE</table><p>自动秒数不能当作熟练玩家时长。全部失败、输入、冻结源、原始轨迹及候选版本留在map-edit；候选库技术记录不等于生产准入。</p><p><a href="results.json">结构化结果 / 完整区域拒绝项 / 实际Module清单</a></p><script>function route(n){const d=document.getElementById('layout').contentDocument;if(!d)return;d.querySelectorAll('[data-route]').forEach(e=>e.style.opacity=(+e.dataset.route===n?1:.06));}</script>'''.replace('OPTIONS',opts).replace('VIDEOS',vids).replace('TABLE',table)
    (out/'report.html').write_text(page);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--probes',required=True);p.add_argument('--capture',required=True);p.add_argument('--out',required=True);p.add_argument('--movies',nargs='+',required=True);a=p.parse_args();build(a.run,a.probes,a.capture,a.out,a.movies)
