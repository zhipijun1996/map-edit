"""Summarize every frozen Seed, paired control and actual native movie."""
import copy,gzip,html,json,shutil
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.map_directed.shape_search.search import search
from pcg.map_directed.shape_search.catalog import load
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest

SOURCE='6479908b4c57ab8bfa18775a7dd453ca9e5c8ab2'
OUT=REPO/'generation/maps/shape-search-v1'

def physical(folder):
    cases=json.loads((folder/'cases.json').read_text())['cases'];summary=json.loads((folder/'summary.json').read_text());rows=summary['rows']
    directed=set();entries=[];route=[]
    for case,batch in zip(cases,json.loads((folder/'physics/batches.json').read_text())):
        raw=gzip.decompress((folder/'physics'/batch['gzip_path']).read_bytes())
        if __import__('hashlib').sha256(raw).hexdigest()!=batch['raw_output_sha256']:raise ValueError('trace_drift')
        r=json.loads(raw)['results'][0];completed={l['id']for l in r['pilot']['legs']if l.get('ok')}
        for leg in case['pilot_program']:
            if leg['id']in completed and leg.get('edge_terminal'):directed.add((leg['edge_id'],leg['edge_from'],leg['edge_to']))
        for leg in r['pilot']['legs']:
            if leg['kind']=='module':entries.append(leg['start'])
        route.append(dict(id=case['id'],held=case.get('holdout',False),ok=r['ok'],ticks=r['ticks'],shots=r['shots'],reason=r['reason'],
            grounded_fraction=sum(f['grounded']for f in r['frames'])/len(r['frames']),
            actual_reward_events=len(r['extra'].get('optional_challenge_events',[])),actual_shop_events=len(r['extra'].get('shop_events',[])),
            failure=r['pilot'].get('failure'),damage_commits=r.get('damage_commits',0)))
    return dict(routes=route,nominal_passed=sum(r['ok']for r in route if not r['held']),held_passed=sum(r['ok']for r in route if r['held']),all_passed=summary['all_passed'],
        actual_directed_seams=[list(p)for p in sorted(directed)],directed_seams_covered=len(directed),
        actual_module_entry_checks=len(entries),maximum_entry_speed=max((s['real_velocity'][0]**2+s['real_velocity'][1]**2)**.5 for s in entries),
        maximum_entry_shot_cooldown=max(s['shot_cooldown']for s in entries),minimum_entry_air_shots=min(s['air_shots']for s in entries),wall_seconds=summary['wall_seconds'])

def space_svg(c,path):
    bounds=c['case']['world_bounds'];x,y,w,h=bounds;parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x-40} {y-100} {w+80} {h+160}">',f'<rect x="{x-40}" y="{y-100}" width="{w+80}" height="{h+160}" fill="#111c29"/>']
    colors=['#557f91','#a1b7a3','#987e53','#628f7b','#8b7199','#6e8153','#82729e','#a67c64']
    for i,m in enumerate(c['modules']):
        dx,dy=m['spec']['placement']
        for r in m['action_clearance']:parts.append(f'<rect x="{r[0]+dx}" y="{r[1]+dy}" width="{r[2]}" height="{r[3]}" fill="#c9edff" opacity=".035"/>')
        for j,r in enumerate(m['case']['platforms']):parts.append(f'<rect x="{r[0]+dx}" y="{r[1]+dy}" width="{r[2]}" height="{r[3]}" fill="{colors[i]}" stroke="#ccd9df" stroke-width="1" opacity="{.45 if j in m["case"]["one_way_platform_indices"] else 1}"/>')
        p=c['nodes'][m['id']]['center']['position'];parts.append(f'<text x="{p[0]}" y="{p[1]-60}" text-anchor="middle" fill="white" font-family="sans-serif" font-size="24">{m["id"]}</text>')
    main={'e0','e1','e2','e3'}
    for e in c['exploration_graph']['edges']:
        a=c['nodes'][e['from']]['center']['position'];b=c['nodes'][e['to']]['center']['position'];parts.append(f'<path d="M {a[0]} {a[1]-35} L {b[0]} {b[1]-35}" fill="none" stroke="{"#ffc964"if e["id"]in main else"#66e4cb"}" stroke-width="4" stroke-dasharray="8 6"/>')
    for seam in c['seams']:
        m=next(m for m in c['modules']if m['id']==seam['from_module']);p=m['ports'][seam['id']]['position'];dx,dy=m['spec']['placement'];parts.append(f'<circle cx="{p[0]+dx}" cy="{p[1]+dy}" r="8" fill="#ffdd7b"/>')
    parts.append('</svg>');path.write_text(''.join(parts))

def build():
    if (OUT/'results.json').exists():raise ValueError('immutable_report_exists')
    g,d,b=load();records=[];ablation=[]
    for i in range(5):
        folder=REPO/f'pcg/results/shape-search-evaluation-{i}-v1';c=json.loads((folder/'compiled.json').read_text());layout=json.loads((folder/'search.json').read_text())
        # Canonicalize global reflection by retaining the bank recipe ordinals.
        # This intentionally ignores mirrors; it is spatial-content variation,
        # never a claim of a new exploration graph.
        recipe={k:v['variant'].split('/')[:2]for k,v in sorted(layout['placements'].items())}
        control=REPO/('pcg/results/shape-search-parent-control-v1'if i==0 else f'pcg/results/shape-search-parent-control-{i}-v1')
        p=physical(folder);old=physical(control);space_svg(c,OUT/f'space-{i}.svg')
        rec=dict(seed='shape-eval-'+str(i),layout_signature=layout['layout_signature'],reflection_ignored_recipe=digest(recipe),selected_variants={k:v['variant']for k,v in layout['placements'].items()},
            search_seconds=layout['wall_seconds'],expanded=layout['expanded'],new=p,paired_old=old,
            audit=json.loads((folder/'assembly-audit.json').read_text()),compiled_sha256=file_sha(folder/'compiled.json'),source_manifest_sha256=file_sha(folder/'physics/source_binding.json'))
        records.append(rec)
        for mode in ['aabb','shape_only','shape_action']:
            r=search(g,d,rec['seed'],mode);r.pop('modules',None);ablation.append(r)
    movies=[]
    for name,target in [('main-1','main-1.mp4'),('reward-0-live','reward-0.mp4'),('cache-2-live','cache-2.mp4')]:
        root=OUT/name;m=json.loads((root/'manifest.json').read_text());assert m['comparison']['passed']and file_sha(root/m['file'])==m['sha256'];shutil.copy2(root/m['file'],OUT/target);movies.append(dict(name=target,**m,renderer='frozen live Router policy'if name.endswith('live')else'JSON input replay'))
    source=REPO/'pcg/results/ecosystem-stability-v2/maps/0';shutil.copy2(source/'mission.json',OUT/'mission.json');write(OUT/'exploration.json',g)
    # Previously captured formal current-main image, explicitly historical media.
    old_image=REPO/'generation/maps/content-routes-v1/formal-whole-map.png';shutil.copy2(old_image,OUT/'formal-main-prior-capture.png')
    result=dict(schema='pcg/real-shape-spatial-experiment/v1',source_commit=SOURCE,main_commit='26e7f2a4459623f35613a857da8a75e89daa3e62',records=records,ablation=ablation,catalog=b,
        total_candidates=sum(map(len,d.values())),nominal_passed=sum(r['new']['nominal_passed']for r in records),held_passed=sum(r['new']['held_passed']for r in records),
        paired_old_nominal_passed=sum(r['paired_old']['nominal_passed']for r in records),paired_old_held_passed=sum(r['paired_old']['held_passed']for r in records),
        unique_layouts=len({r['layout_signature']for r in records}),unique_bank_recipes_without_mirror=len({r['reflection_ignored_recipe']for r in records}),unique_exploration_topologies=1,
        movies=movies,production_admitted=False,human_fun='unreviewed',stable_superiority_proved=False,
        formal_image=dict(file='formal-main-prior-capture.png',sha256=file_sha(old_image),source='content-routes-v1: actual DemoApp default plains-region-v12-root-bell-spaces; same current main, prior capture; not a new physical control'))
    write(OUT/'results.json',result)
    rows=''.join(f'<tr><td>{r["seed"]}</td><td>{r["new"]["nominal_passed"]}/6</td><td>{r["new"]["held_passed"]}/6</td><td>{r["paired_old"]["held_passed"]}/6</td><td>{r["search_seconds"]*1000:.1f} ms / {r["expanded"]}</td></tr>'for r in records)
    gallery=''.join(f'<article><h3>{r["seed"]} · 独立扰动 {r["new"]["held_passed"]}/6</h3><a href="map-{i}.png"><img src="map-{i}.png"></a><details><summary>真实形状、端口、动作样本与主支路线</summary><img src="space-{i}.svg"></details></article>'for i,r in enumerate(records))
    video=''.join(f'<article><h3>{html.escape(m["name"])} · {m["duration"]:.2f}s · 正常1倍</h3><video controls preload="metadata" src="{m["name"]}"></video><a href="{m["name"]}" download>下载完整原片</a></article>'for m in movies)
    page=f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>真实 Macro 形状空间搜索 · 全部结果</title><style>body{{margin:auto;max-width:1300px;padding:24px;background:#111a25;color:#dde9ed;font:17px/1.7 system-ui}}a{{color:#7edcc9}}img,video{{width:100%;height:auto}}article{{margin:28px 0;padding:12px;background:#192638}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #496071;padding:8px}}strong{{color:#ffcf85}}</style>
<h1>实际 Macro 形状与动作条件：空间搜索第一版</h1><p><strong>原型可运行；尚未证明稳定超过旧管线。</strong>五个预定 Seed，无删图、换 Seed 或留出后修复。固定8 Macro、9接缝、双回环、3宝箱和1商店。Map新增地形为0。主线/奖励/回程连续在真实Godot世界中验证。</p>
<p>常规路线 {result['nominal_passed']}/30；独立扰动 {result['held_passed']}/30。同内容旧布局独立扰动 {result['paired_old_held_passed']}/30。{result['unique_layouts']}个空间签名，去镜像后仅{result['unique_bank_recipes_without_mirror']}种岸体组合，探索拓扑仍只有1种。没有把镜像算作探索多样性。</p>
<p><a href="index.html">实际Godot手动地图（Seed0）</a> · <a href="results.json">所有结果及失败详情JSON</a> · <a href="mission.json">既有Mission合同</a> · <a href="exploration.json">既有Exploration合同</a></p>
<h2>全部Seed，无筛选</h2><table><tr><th>Seed</th><th>常规</th><th>独立扰动</th><th>配对旧布局扰动</th><th>空间搜索 / 扩展候选</th></tr>{rows}</table>{gallery}
<h2>完整实测录像</h2><p>程序输入，不是人工试玩。所有位置、速度、输入、资源、机关、敌人与经济事件逐帧严格核对。保留等待及结束后1秒冻结画面。初次Seed0的JSON轴输入回放有微小浮点差异，失败原件保留；live录像执行与无画面验证相同的冻结Router控制程序，未放宽比较。</p>{video}
<h2>同内容旧布局，统一表现条件</h2><img src="parent-control.png"><p>旧管线直接使用原布局坐标；新搜索不读取这些位置。两者使用同一角色、内容核心、能力与当前主游戏地标/灯光/前景。新图减少了3块退役门顶盖，两个恢复岸有有限形状变体。上述差异公开，不能把它们单独归功于搜索。</p>
<h2>做对与没做对</h2><p>同一候选库下，矩形包围盒拒绝5/5，真实形状搜索可拼5/5。shape-only与shape+action在未破坏的库里选择相同答案，说明本批尚未证实动作约束提高正常样本成功率。刻意反例只加一块邻接岩体：纯形状放行、动作避让拒绝，原生Godot实际落到错误支持面，确认动作样本确实参与约束。</p>
<p>当前动作条件只覆盖落地、已恢复射击、冷却为0、速度≤1的端口。跳跃/反冲由原物理执行。它还不是任意高速空中交接求解器；父版轨迹样本也不是变体的通用证明。每张新图均重新验证18个接缝方向和奖励回程。</p>
<h2>与当前主游戏协调感的距离</h2><img src="formal-main-prior-capture.png"><p>此图来自上一轮同一最新main的实际默认生成，明确为历史截图，不是本次配对物理控制。研究图已接入正式岩体、角色、风铃、齿轮、落地地标、局部构图、灯光和前景。整体仍有悬浮岛、横向岸体重复和简单上下层；这些来自有限Macro轮廓与固定骨架，材质不能补救。主游戏的身份配方、连续地貌、生态密度和正式流程更完整。</p>
<p>下一步应先提供数种真正不同的贯通岩体/空洞Macro，加入区域级实体与留白骨架、落点容错余量和动态相位关系，再让搜索比较空间方案；保持新的独立留出。当前结果不能生产准入，也未有人类趣味认可。</p><p>算法冻结 {SOURCE}。完整失败、源、输入、物理输出与媒体均版本化归档；详见PR #1研究报告。</p>'''
    (OUT/'report.html').write_text(page);return result

if __name__=='__main__':
    r=build();print(json.dumps({k:r[k]for k in ['nominal_passed','held_passed','paired_old_held_passed','unique_layouts','unique_bank_recipes_without_mirror']},ensure_ascii=False))
