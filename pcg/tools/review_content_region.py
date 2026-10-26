"""Measured regional review using the established trace, grid and matrix tools."""
import argparse,copy,html,json,shutil
from pathlib import Path
from pcg.map_directed.run import write
from pcg.tools.review_contact_grammar import inspect
from pcg.tools.review_block_grid import grid,logical,observed_matrix


def run(source,held,inventory,out):
    source,held,inventory,out=map(Path,[source,held,inventory,out])
    out.mkdir(exist_ok=False)
    facts,c,traces=inspect(source)
    nominal=json.loads((source/'summary.json').read_text())
    holdout=json.loads((held/'summary.json').read_text())
    stock=json.loads((inventory/'summary.json').read_text())
    # The diagrams use exactly the compiled graph, never a separate blueprint.
    g=copy.deepcopy(c['exploration_graph'])
    for n in g['nodes']:
        s=n['stage'];direction=1 if s%2==0 else -1
        x={'junction':0,'merge':20,'reward':-5}.get(n['role'],5+5*int(n['slot'][-1]) if n['slot'] else 0)
        y=12*s+(-3 if str(n['slot']).startswith('upper') else 3 if str(n['slot']).startswith('lower') else 5 if n['role']=='reward' else 0)
        n['ideal']=[x if direction==1 else 20-x,y]
    logical(g,out/'exploration.svg');grid(c,out/'block-shapes.svg')
    bounds=c['case']['world_bounds'];x,y,w,h=bounds
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {w} {h}">',f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#101a2b"/>']
    for r in c['case']['platforms']:
        svg.append(f'<rect x="{r[0]}" y="{r[1]}" width="{r[2]}" height="{r[3]}" fill="#697f75"/>')
    for name,color in [('full-region-upper','#60cfff'),('full-region-lower','#72eab4'),('full-region-reward-expeditions','#ffc35c')]:
        pts=' '.join(f'{a:.1f},{b:.1f}' for a,b in traces[name])
        svg.append(f'<polyline points="{pts}" fill="none" stroke="{color}" opacity=".8" stroke-width="5"><title>{name}</title></polyline>')
    for key,n in c['nodes'].items():
        a,b=n['center']['position'];svg.append(f'<text x="{a+18}" y="{b-25}" fill="white" font-size="28">{html.escape(key)}</text>')
    svg.append('</svg>');(out/'measured-world.svg').write_text('\n'.join(svg))
    # Adapter to the existing matrix observer: preserve all individual records.
    boundaries=[]
    for row in nominal['rows']:
        boundaries.append(dict(id=row['id'],**json.loads((source/(row['id']+'-boundary-state.json')).read_text())))
    matrix_source=out/'matrix-input';matrix_source.mkdir()
    write(matrix_source/'boundary-state-verification.json',boundaries)
    write(out/'transition-matrix.json',observed_matrix(matrix_source,c))
    write(out/'correspondence.json',dict(graph=g,recipe=json.loads((source/'map-recipe.json').read_text()),allocation=json.loads((source/'content-allocation.json').read_text())))
    shutil.copy2('pcg/results/content-domains-region-media-v1/whole-map.png',out/'whole-map.png')
    clips=[]
    for folder,alias in [('region-movie-low-v1','lower-full'),('region-movie-reward-v1','reward-return')]:
        root=Path('pcg/results/content-domains-'+folder);manifest=json.loads((root/'manifest.json').read_text())
        assert manifest['comparison']['passed']
        shutil.copy2(root/manifest['file'],out/(alias+'.mp4'));clips.append(dict(alias=alias,**manifest))
    write(out/'video-manifest.json',dict(clips=clips,human_playtests=0))
    facts.update(nominal_passed=nominal['passed'],holdout_passed=holdout['passed'],holdout_total=holdout['total'],inventory=stock,
                 unique_physical_layouts=1,stages=5,challenge_slots=30,hubs=10,reward_branches=3,
                 topology_scope='Five serial split/rejoin stages, ten arms, one-way inter-stage drops; not arbitrary mesh or three independent end-to-end routes',
                 candidate_only=True,major_items=0,boss_encounter=False,shops=0)
    write(out/'results.json',facts)
    rows=''.join(f'<tr><td>{html.escape(r["id"])}</td><td>{r["seconds"]}</td><td>{r["shots"]}</td><td>{100*r["walk_policy_fraction"]:.1f}%</td><td>{r["coins"]}</td></tr>'for r in facts['rows'])
    (out/'report.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>43模块真实整图与多路线</title><style>body{max-width:1180px;margin:30px auto;padding:0 18px;background:#101a2b;color:#e0ebf7;font:17px/1.65 system-ui}a{color:#70d3ff}img,video{width:100%;background:#0b1322}td,th{padding:9px;border:1px solid #456}table{border-collapse:collapse}</style>
<h1>风铃平原：43模块真实整图</h1><p>30挑战＋10地貌枢纽＋3奖励支路；5处分叉汇合、47处直接接缝、70/70声明方向有整图物理见证。Block128整数坐标，Map补地形0，移动平台0。全部94父版本均已审计，40版本取得有限方向接口见证，54版本仍阻塞；没有宣称全部适配完成。</p>
<p><a href="index.html">打开Godot手动试玩</a>：A/D移动、空格跳跃、鼠标松开射击反冲、M整图、R重试。</p>
<p>这次增加了真实规模，但设计验收尚未通过：仍是五段重复的双路分叉，并非自由网状探索；段间下落单向，不能保证全区域自由回程。三个宝箱为同一挑战家族，只有54金币，没有主要构筑道具、商店或真正Boss。自动熟练路线约98–128秒，明显未达到7–10分钟区域目标，也不是人类试玩时间。</p>
<h2>完整Godot世界截图</h2><a href="whole-map.png"><img src="whole-map.png" alt="全部43模块真实地图"></a>
<h2>相同节点的逻辑与物理对应</h2><p>逻辑图仅为排版；所有节点与边进入下方实际世界。蓝色高路、绿色低路、金色奖励巡回。5次二选一最多32种组合，不是32张不同地图。</p><img src="exploration.svg" alt="43节点探索图"><img src="measured-world.svg" alt="真实碰撞几何和实测路线"><p><a href="block-shapes.svg">Block形状和Port</a> · <a href="correspondence.json">逐节点版本、整数位置与边</a> · <a href="transition-matrix.json">有限Port关系见证</a></p>
<h2>24秒：尖刺奖励支路、原路回程、高路和汇合</h2><p>这是同一张43模块地图中的开头片段，没有替换成独立Module。</p><video controls preload="metadata" src="reward-return.mp4"></video><p><a href="reward-return.mp4">下载24秒录像</a></p>
<h2>99秒：完整低路抵达区域出口</h2><video controls preload="metadata" src="lower-full.mp4"></video><p><a href="lower-full.mp4">下载完整路线</a></p>
<h2>真实验证与仍存在的问题</h2><p>4/4常规连续策略＋6/6冻结布局后的新输入扰动；全部声明方向巡回约278秒。两段原生录像合计7262物理帧逐帧一致，无角色传送、资源重置或剪掉等待。另有两条有限简化策略未到达出口，不代表所有绕过均已排除。未进行真人趣味认可或生产入库。</p><table><tr><th>策略</th><th>物理秒</th><th>射击</th><th>walk策略占比</th><th>金币</th></tr>'''+rows+'''</table><p>横向岩岸和枢纽重复仍明显，部分路线仍以行走为主；没有通过扩大节点数解决美感、路线独立性或玩法深度。下一轮应增加跨段汇合和可返回的区域级回环，再用不对称地貌枢纽与更丰富挑战取代重复骨架。</p><p><a href="results.json">结构化结果与边界</a> · <a href="video-manifest.json">录像SHA与严格帧对照</a></p></html>''')
    return facts


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--held',required=True);p.add_argument('--inventory',required=True);p.add_argument('--out',required=True);a=p.parse_args();run(a.source,a.held,a.inventory,a.out)
