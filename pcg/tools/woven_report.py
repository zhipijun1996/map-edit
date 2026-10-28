"""Assemble a review page from immutable real-world evidence and native movies."""
import argparse,gzip,html,json,math,statistics,subprocess
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.plains.evaluation import observed


def graph_svg(c,out):
    g=c['exploration_graph'];positions={k:v['center']['position']for k,v in c['nodes'].items()}
    xs=[p[0]for p in positions.values()];ys=[p[1]for p in positions.values()]
    def xy(k):
        x,y=positions[k];return 60+(x-min(xs))/max(1,max(xs)-min(xs))*980,65+(y-min(ys))/max(1,max(ys)-min(ys))*530
    raw=json.loads((REPO/'pcg/results/woven-release-v1/cases.json').read_text())['cases']
    main={s['edge_id']for s in raw[0]['r2_semantics']['logical_route']}
    alt={s['edge_id']for s in next(v for v in raw if v['id']=='woven-plains-alternative-main')['r2_semantics']['logical_route']}
    lines=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 660"><rect width="1100" height="660" fill="#12262d"/><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0L8 4L0 8" fill="#deb66a"/></marker></defs><g font-family="system-ui" fill="#e8eee4">',
        '<text x="25" y="26" font-size="18">实际空间中的探索图：粉色完成路线 · 蓝色替代路线 · 金色奖励与回程</text>']
    for e in g['edges']:
        a,b=xy(e['from']),xy(e['to']);color='#66858d';width=2;dash=''
        if e['id']in alt:color='#8ed5ec';width=4
        if e['id']in main:color='#f394a4';width=4
        if e.get('purpose')in ['reward_expedition','return_shortcut','hidden_route']:color='#e6c16d';width=3
        if e['switch']:dash=' stroke-dasharray="7 5"'
        arrow=' marker-end="url(#arrow)"'if not e['bidirectional']else''
        lines.append(f'<path d="M{a[0]:.1f} {a[1]:.1f}L{b[0]:.1f} {b[1]:.1f}" stroke="{color}" stroke-width="{width}" fill="none"{dash}{arrow}/>')
    for n in g['nodes']:
        x,y=xy(n['id']);color='#d8ede2'
        if n['role']=='reward':color='#e6c16d'
        if n['id']==g['entry']:color='#f394a4'
        if n['id']==g['goal']:color='#c4a1ee'
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="{color}"/><text x="{x+10:.1f}" y="{y-9:.1f}" font-size="14">{html.escape(n["id"]+" "+n.get("label",""))}</text>')
    lines.append('<text x="25" y="640" font-size="14">连线表示已声明探索职责；并不代表空间中任意跳落都已穷举验证。虚线含世界状态条件。</text></g></svg>')
    (out/'exploration.svg').write_text(''.join(lines))
    mission='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 270"><rect width="1100" height="270" fill="#12262d"/><g font-family="system-ui" fill="#e8eee4" font-size="18"><text x="25" y="30">Mission 职责：可选奖励不阻塞区域完成</text><path d="M80 95H950M160 95L320 185H570L760 95M570 185L780 220H970" fill="none" stroke="#718e92" stroke-width="3"/><text x="45" y="80">区域入口</text><text x="400" y="80">多路线探索 / 熟悉地标</text><text x="880" y="80">前庭 → 出口</text><text x="200" y="175">反冲奖励挑战</text><text x="500" y="175">实体宝箱</text><text x="740" y="210">获得回程连接</text><text x="890" y="245">商店消费 / 继续探索</text></g></svg>'''
    (out/'mission.svg').write_text(mission)


def build(out):
    out=Path(out).resolve()
    if(out/'report.html').exists():raise ValueError('immutable_report_exists')
    run=REPO/'pcg/results/woven-release-v1';c=json.loads((run/'compiled.json').read_text());summary=json.loads((run/'summary.json').read_text());checks=json.loads((REPO/'pcg/results/woven-release-checks-v1/summary.json').read_text())
    warm=REPO/'pcg/results/woven-warm-reuse-v1';warm_summary=json.loads((warm/'summary.json').read_text());warm_log=json.loads((warm/'generation-log.json').read_text());returns=json.loads((REPO/'pcg/results/woven-return-value-v1/summary.json').read_text());negative=json.loads((REPO/'pcg/results/woven-bypass-v1/summary.json').read_text())
    rows=[];execution=[];cases={v['id']:v for v in json.loads((run/'cases.json').read_text())['cases']}
    for b in json.loads((run/'physics/batches.json').read_text()):
        execution.append(json.loads((run/'physics'/b['execution']).read_text()))
        for r in json.loads(gzip.decompress((run/'physics'/b['gzip_path']).read_bytes()))['results']:
            behavior=observed(cases[r['id']],r)
            rows.append(dict(id=r['id'],ok=r['ok'],seconds=r['ticks']/60,shots=r['shots'],air_shots=behavior['air_shots'],
                held=bool(cases[r['id']].get('holdout')),stationary_fraction=sum(abs(f['real_velocity'][0])+abs(f['real_velocity'][1])<2 for f in r['frames'])/len(r['frames']),
                earned_chests=r['extra'].get('optional_challenge_events',[]),purchases=r['extra'].get('shop_events',[])))
    native=[]
    for name in ['main-route','alternative-route','reward-shop-return','timed-return']:
        m=json.loads((out/name/'manifest.json').read_text());assert m['comparison']['passed'];native.append(dict(name=name,published_file=name+'.mp4',**m))
    history=[]
    for p in sorted((REPO/'pcg/results').glob('woven-*')):
        if(p/'failure.json').exists():history.append(dict(run=p.name,type='infrastructure_or_contract_failure',error=json.loads((p/'failure.json').read_text())['error']))
        elif(p/'summary.json').exists():
            s=json.loads((p/'summary.json').read_text())
            if not s.get('all_passed',True)and not s.get('counterfactual_expectations_met'):
                history.append(dict(run=p.name,type='retained_failed_stage',failures=[dict(id=r.get('id'),reason=r.get('reason'))for r in s.get('rows',[])if not r.get('ok')]))
    g=c['exploration_graph'];cold=json.loads((run/'generation-log.json').read_text())
    same_versions=[m['content_version']for m in c['modules']]==[m['content_version']for m in json.loads((warm/'compiled.json').read_text())['modules']]
    assert summary['all_passed']and checks['all_passed']and warm_summary['all_passed']and returns['all_passed']and negative['counterfactual_expectations_met']and same_versions
    result=dict(schema='pcg/woven-region-review/v1',source_commit=json.loads((run/'module-library/bundle.json').read_text())['sourceCommit'],
        selected_seed=g['seed'],physical_topologies=1,modules=len(c['modules']),connections=len(c['seams']),graph_cycle_rank=len(g['edges'])-len(g['nodes'])+1,
        module_sizes=sorted({tuple(m['spec']['space']['core_bounds'][2:])for m in c['modules']}),
        whole_world_cases=len(rows),held_input_cases=sum(r['held']for r in rows),whole_world_passed=summary['all_passed'],
        declared_directed_connections=checks['expected_directed_edges'],observed_directed_connections=checks['observed_directed_edges'],
        native_frames=sum(v['comparison']['native_frames']for v in native),native_movies=native,
        new_payload_versions=len(list((REPO/'pcg/results/woven-candidate-library-v1/payloads').glob('*/*/record.json'))),
        cold_generation=cold,warm_generation=warm_log,warm_cases=len(warm_summary['rows']),warm_passed=warm_summary['all_passed'],warm_versions_identical=same_versions,
        returns=returns['pairs'],negative_cases=negative['rows'],gates=checks['closed_chamber_checks'],
        content=dict(solid_rectangles=len(c['case']['platforms'])-len(c['case']['one_way_platform_indices']),one_way_rectangles=len(c['case']['one_way_platform_indices']),
            chests=len(c['case']['reward_sites']),merchants=len(c['case']['shop_sites']),moving_platforms=len(c['case']['moving_platforms']),gears=len(c['case']['saws']),enemies=len(c['case']['enemies'])),
        instance_audit=checks['geometry'],rows=rows,failures_retained=history,
        clips=json.loads((out/'clip-manifests.json').read_text())['clips'],
        costs=dict(offline_full_validation_seconds=summary['wall_seconds'],warm_full_validation_seconds=warm_summary['wall_seconds'],
            layout_solver_wall_seconds=json.loads((run/'layout.json').read_text())['wall_seconds'],layout_replayed_from_frozen_artifact=True,runtime_generation_measured=False,
            largest_observed_children_peak_rss_kib=max(v['children_peak_rss_kib']for v in execution),
            scope='Offline Python generation + source freeze + real Godot subprocesses + trace IO; cumulative child RSS observation, not Runtime generation latency or browser memory'),
        limits=['Only one new physical topology; warm reuse is the same map, not multi-seed experience diversity.',
            'Rectangular contact reservations contain irregular rock terrain; arbitrary irregular-mask nesting is not implemented.',
            'Content vocabulary remains narrow: recoil climbs, low arches and two bell/reward relationships. No human fun approval.',
            '50 declared directions and sampled input perturbations are tested; arbitrary motion/state, unplanned drops, global shortcut bypass and low-resource states are not exhaustively certified.',
            'Boss combat, campaign persistence, forest rollout and larger-than-formal-region acceptance remain future work.',
            'Current retrieval matches exact hard demands; arbitrary semantic/port/shape adaptation and Runtime solver deployment remain incomplete.'],
        production_admitted=False,human_fun='unreviewed',report_producer_sha256=file_sha(Path(__file__)))
    write(out/'results.json',result);graph_svg(c,out)
    short=[r for r in rows if not r['held']and 'coverage'not in r['id']]
    route_rows=''.join(f'<tr><td>{html.escape(r["id"].removeprefix("woven-plains-"))}</td><td>{r["seconds"]:.1f}s</td><td>{r["shots"]}</td><td>{r["air_shots"]}</td></tr>'for r in short)
    return_rows=''.join(f'<tr><td>奖励远征 {r["branch"]+1}</td><td>{r["detour_seconds"]:.2f}s</td><td>{r["shortcut_seconds"]:.2f}s</td><td>{r["saved_seconds"]:.2f}s</td></tr>'for r in returns['pairs'])
    labels=[('A · 完成路线','main-route.mp4','main-route.mp4'),('B · 替代完成路线','alternative-route.mp4','alternative-route.mp4'),('C · 奖励、购买与回程（35秒片段）','reward-shop-highlight.mp4','reward-shop-return.mp4'),('D · 限时宝库：关门后内部射铃返回（35秒片段）','timed-cache-highlight.mp4','timed-return.mp4')]
    videos=''.join(f'<article><h3>{title}</h3><video controls preload="metadata" src="{name}"></video><p><a href="{full}" download>下载完整录像</a> · 程序输入，正常 1 倍速度。C/D 为标明来源时间段的片段；完整录像保留全过程与末尾 1 秒完成画面。</p></article>'for title,name,full in labels)
    page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>风铃平原 · 岩谷织路 · 真实整图里程碑</title><style>body{{margin:auto;max-width:1180px;padding:24px;background:#12262d;color:#e8eee4;font:17px/1.65 system-ui}}a{{color:#e4c27a}}img,video{{width:100%;height:auto;background:#0a151b}}table{{border-collapse:collapse;width:100%}}th,td{{padding:10px;text-align:left;border-bottom:1px solid #456}}article{{margin:30px 0}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}li{{margin:9px 0}}</style><h1>风铃平原 · 岩谷织路</h1><p>现有 R2 拓扑驱动的真实完整地图：19 个 Macro、27 处直接接缝，三种尺寸；反冲岩岸、分叉汇合、两处实体宝箱、商店与获得奖励后的回程连接。</p><p><a href="index.html">打开真实 Godot 隔离试玩</a> · A/D 移动，Space 单跳，鼠标松开反冲，S 下穿，E 购买，M 整图，R 重试。</p><p><b>本轮范围：</b>一张新物理拓扑。25 条冻结整图策略通过，含 12 条独立输入扰动；50 个声明方向全部实际覆盖。人工趣味待评，正式游戏保持原流程。Boss、战役、多 Seed 品质及最终区域规模仍待后续验收。</p><h2>实际整图</h2><a href="whole-map.png"><img src="whole-map.png" alt="实际实例化 Godot 整图截图"></a><p>Map 添加连接地形 0；Module 先生成完整地形，再刚性摆放。主要活动是主动跳跃与反冲；当前内容没有移动平台、齿轮或敌人。地貌与挑战词汇仍需扩充。</p><h2>任务与探索关系</h2><img src="mission.svg" alt="任务职责图"><img src="exploration.svg" alt="实际布局中的探索关系图"><p>独立环秩为 9，只描述图结构，不作趣味评分。两处宝箱腔通过角色身体扩张后的闭门隔离检查；4 个省略奖励射击的普通跳跃替代策略均失败。这些反例不等于穷举所有玩家操作。</p><h2>路线与回程的实际结果</h2><table><tr><th>路线</th><th>连续耗时</th><th>射击</th><th>空中射击</th></tr>{route_rows}</table><p>上述为正常速度程序策略，不代表人类通关时间。奖励路线完成实际领取；购买调用原 ShopService，未注入金币。</p><table><tr><th>配对回程</th><th>绕行</th><th>获得的回程连接</th><th>节省</th></tr>{return_rows}</table><p>4 条真实配对实验均通过；每对从同一入口出发，取宝前的实际位置、输入与资源轨迹哈希相同，仅后续回程路线不同。</p><h2>自增长与复用</h2><table><tr><th>批次</th><th>需求适配创作</th><th>已验证版本复用</th><th>整图复验</th></tr><tr><td>首次新形状需求</td><td>{cold['new_geometry_instances']}</td><td>{cold['unchanged_library_reuse']}</td><td>25/25</td></tr><tr><td>同图再次拼装</td><td>{warm_log['new_geometry_instances']}</td><td>{warm_log['unchanged_library_reuse']}</td><td>{len(warm_summary['rows'])}/{len(warm_summary['rows'])}</td></tr></table><p>19 个版本进入隔离候选库；通用端口状态关系仍为 UNKNOWN，人工认可和生产准入均为 0。当前创作适配已有关系原型，尚不支持任意自然语言创意。复用批次使用同一地图，不能算第二张随机地图。</p><h2>关键路线录像</h2>{videos}<h2>实现与限制</h2><p>复用原 R2、Mission/Exploration、CP-SAT、Module 标准输出、CandidateLibrary 与真实 Harness。区域规则目前为受支持的结构化子集；布局反馈已能处理奖励空间被占、端口净空和实际下穿条件等失败。生成和物理认证仍为离线流程，Runtime 延迟未据此签署。</p><ul>{''.join('<li>'+html.escape(s)+'</li>'for s in result['limits'])}</ul><p><a href="results.json">结构化结果与保留失败索引</a> · 视频可以直接在聊天按 A/B/C/D 反馈，无需填写表单。</p></html>'''
    (out/'report.html').write_text(page);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();r=build(a.out);print(json.dumps({k:r[k]for k in ['modules','connections','whole_world_cases','held_input_cases','native_frames']},ensure_ascii=False))
