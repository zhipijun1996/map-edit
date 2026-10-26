"""Publish measured Block diagnostics; drawings are labelled, never physics proof."""
import argparse,html,json
from pathlib import Path
from pcg.map_directed.run import write
from pcg.tools.review_contact_grammar import inspect,diagram

def observed_matrix(run,c):
    """Finite concrete Port-plane witnesses; canonical UNKNOWN stays UNKNOWN."""
    modules={m['id']:m for m in c['modules']};matrix={}
    for m in modules.values():
        matrix[m['id']]=dict(contentVersion=m['content_version'],relations=[dict(**{'from':a,'to':b},status='UNKNOWN',witnesses=[])for a in m['ports']for b in m['ports']if a!=b])
    for case in json.loads((Path(run)/'boundary-state-verification.json').read_text()):
        if not case['ok']:continue
        for incoming,outgoing in zip(case['crossings'],case['crossings'][1:]):
            if incoming['to']!=outgoing['from']or incoming['edge']==outgoing['edge']:continue
            row=next(r for r in matrix[incoming['to']]['relations']if r['from']==incoming['edge']and r['to']==outgoing['edge'])
            row['status']='observed_in_concrete_map'
            row['witnesses'].append(dict(case=case['id'],entry=incoming['samples'][-1],exit=outgoing['samples'][0]))
    return dict(scope='Actual consecutive boundary-plane crossings in this frozen map only; unobserved pairs UNKNOWN, no universal entry/exit ranges, no production admission',modules=matrix)

def grid(c,path):
    x,y,w,h=c['case']['world_bounds'];parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x-40} {y-100} {w+80} {h+160}">',f'<rect x="{x-40}" y="{y-100}" width="{w+80}" height="{h+160}" fill="#101a2b"/>',f'<text x="{x}" y="{y-40}" fill="white" font-size="28">Block128 reserved shapes + real Port anchors (diagnostic)</text>']
    palette=['#38bdf8','#a78bfa','#34d399','#fb923c']
    for i,m in enumerate(c['modules']):
        g=m['block_grid'];b=g['size'];dx,dy=m['spec']['placement'];color=palette[i%len(palette)]
        for a,z in g['cells']:
            parts.append(f'<rect x="{dx+g["origin"][0]+a*b}" y="{dy+g["origin"][1]+z*b}" width="{b}" height="{b}" fill="{color}" fill-opacity=".16" stroke="{color}" stroke-width="2"/>')
        for p in m['ports'].values():
            a,z=p['position'];parts.append(f'<circle cx="{dx+a}" cy="{dy+z}" r="8" fill="#fff"/>')
        a,z=m['center']['position'];parts.append(f'<text x="{dx+a+16}" y="{dy+z-32}" fill="white" font-size="22">{html.escape(m["id"])}</text>')
    for r in c['case']['platforms']:parts.append(f'<rect x="{r[0]}" y="{r[1]}" width="{r[2]}" height="{r[3]}" fill="#8c9d8b"/>')
    parts.append('</svg>');Path(path).write_text('\n'.join(parts))

def logical(g,path):
    points={n['id']:n['ideal']for n in g['nodes']};xs=[v[0]for v in points.values()];ys=[v[1]for v in points.values()]
    x,y=min(xs)-10,min(ys)-10;w,h=max(xs)-x+10,max(ys)-y+10
    s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}">',f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#101a2b"/>']
    for e in g['edges']:
        a,b=points[e['from']],points[e['to']];color='#e7ae51'if e['purpose']=='return_shortcut'else'#607d9b'
        s.append(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" stroke="{color}" stroke-width=".5"><title>{html.escape(e["id"]+": "+e["purpose"])}</title></path>')
    for n in g['nodes']:
        a,b=points[n['id']];color='#f4c95d'if n['role']=='reward'else'#fb7185'if n['role']=='boss'else'#38bdf8'
        s.append(f'<circle cx="{a}" cy="{b}" r="1.5" fill="{color}"/><text x="{a+2}" y="{b}" fill="white" font-size="2.2">{n["id"]}</text>')
    s.append('</svg>');Path(path).write_text('\n'.join(s))

def run(runs,plan,out):
    out=Path(out)
    if out.exists():raise ValueError('immutable_review_exists')
    out.mkdir(parents=True);maps=[]
    for i,folder in enumerate(runs):
        folder=Path(folder);m,c,traces=inspect(folder);summary=json.loads((folder/'summary.json').read_text());m['all_passed']=summary['all_passed'];m['passed']=summary['passed'];m['total']=summary['total']
        m['search']=json.loads((folder/'search.json').read_text());m['search'].pop('trace',None)
        m['boundary_state_verified']=all(a['ok']for a in json.loads((folder/'boundary-state-verification.json').read_text()))
        m['block_size']=128;m['reserved_cells']=sum(len(v['block_grid']['cells'])for v in c['modules']);m['root_contract_binding']='physics/source_binding.json'
        matrix=observed_matrix(folder,c);write(out/f'map-{i}-transition-matrix.json',matrix)
        m['observed_direction_pairs']=sum(sum(r['status']=='observed_in_concrete_map'for r in v['relations'])for v in matrix['modules'].values())
        maps.append(m);diagram(c,traces,out/f'map-{i}-routes.svg');grid(c,out/f'map-{i}-blocks.svg')
    g=json.loads((Path(plan)/'exploration.json').read_text());logical(g,out/'regional-logical-only.svg')
    result=dict(schema='pcg/graph-block-module-review/v1',maps=maps,total_passed=sum(m['passed']for m in maps),total_cases=sum(m['total']for m in maps),
        nominal=sum(sum('-held-'not in r['id']for r in m['rows'])for m in maps),fresh_input_perturbations=sum(sum('-held-'in r['id']for r in m['rows'])for m in maps),
        block_size=128,topology_scope='Preserved bounded 3/4-level contact graphs; new Module shapes and placements. Not unrestricted regional grammar.',
        regional_plan=json.loads((Path(plan)/'summary.json').read_text()),human_fun='unreviewed',production_admitted=False)
    write(out/'results.json',result)
    cards=[]
    for i,m in enumerate(maps):
        cards.append(f'<article><h2>Seed {i}: {html.escape(m["seed"])}</h2><p>{m["modules"]} Modules / {m["seams"]}直接接缝 / {m["passed"]}/{m["total"]}整图策略；覆盖{m["directed_edges_covered"]}/{m["directed_edges_expected"]}声明方向。Map补平台0；{m["chests"]}箱{m["currency"]}币。</p><img src="map-{i}-whole.png" alt="真实Godot完整世界截图"><p><a href="map-{i}-blocks.svg">Block占用和端口</a> · <a href="map-{i}-routes.svg">实际地形与实测路线</a></p></article>')
    (out/'report.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Graph + Block + Module 实验</title><style>body{max-width:1180px;margin:32px auto;padding:0 18px;background:#101a2b;color:#dfebf8;font:17px/1.65 system-ui}a{color:#70d3ff}img,video{width:100%;background:#0b1322}article{margin:35px 0;padding:18px;border:1px solid #36506f}</style><h1>风铃平原：Graph + Block128 + Module 第一版</h1><p>真实128网格、不规则预留轮廓、边界中心端口、零间隙直接拼接；单角色原物理、无中途重置。下方为程序输入验证，人工趣味未评审、通用接口UNKNOWN、生产准入关闭。</p><p>这是一项空间内核实验。三个Seed仍来自有限3/4层空间文法，奖励仅金币，不代表最终40～65模块区域或广泛探索多样性。</p><h2>真实原生录像 · 正常1倍 / 60Hz</h2><p>原始连续路线，包含完整等待、启动及末尾1秒；每帧对照无画面的原始物理见证。</p><video controls preload="metadata" src="main-route.mp4"></video><p><a href="main-route.mp4">下载主路线</a></p><video controls preload="metadata" src="reward-return.mp4"></video><p><a href="reward-return.mp4">下载奖励与回程路线</a></p>'+''.join(cards)+'<h2>完整区域职责蓝图：仅逻辑设计</h2><p>44节点、3主路线、6奖励支路，覆盖折返／单向环回／汇合。尚未完成真实拼装，图中Boss和道具不是已实现内容，不计入物理通过数。</p><img src="regional-logical-only.svg" alt="仅逻辑蓝图"><p><a href="results.json">结构化实验结果</a> · <a href="video-manifest.json">录像逐帧对照与SHA</a></p></html>')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--runs',nargs='+',required=True);p.add_argument('--plan',required=True);p.add_argument('--out',required=True);a=p.parse_args();print(json.dumps(run(a.runs,a.plan,a.out),ensure_ascii=False))
