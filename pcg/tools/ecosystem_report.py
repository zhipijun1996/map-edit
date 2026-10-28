"""Read immutable ecosystem evidence into a small shareable review report."""
import argparse,gzip,html,json,statistics
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.map_directed.valley_complete.compare import metrics,svg
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.plains.evaluation import observed

def build(batch,out):
    batch=Path(batch).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    summary=json.loads((batch/'summary.json').read_text());runs=[]
    for entry in summary['runs']:
        path=REPO/entry['path'];s=entry['summary'];rows=[]
        cases={c['id']:c for c in json.loads((path/'cases.json').read_text())['cases']}
        for b in json.loads((path/'physics/batches.json').read_text()):
            packed=path/'physics'/b['gzip_path']
            if file_sha(packed)!=b['gzip_sha256']:raise ValueError('report_trace_drift')
            for result in json.loads(gzip.decompress(packed.read_bytes()))['results']:
                c=cases[result['id']];frames=result['frames'];behavior=observed(c,result)
                row=dict(id=result['id'],ok=result['ok'],held='ecosystem_trial'in c,
                    diagnostic='delayed-return'in result['id'],seconds=result['ticks']/60,
                    shots=result['shots'],air_hit_refunds=behavior['refunds'],
                    continuous_two_air_shots=behavior['continuous_two_air_shots'],
                    stationary_fraction=sum(abs(f['real_velocity'][0])+abs(f['real_velocity'][1])<2 for f in frames)/max(1,len(frames)),
                    earned_chests=result['extra']['optional_challenge_events'],purchases=result['extra']['shop_events'])
                rows.append(row)
        runs.append(dict(seed=s['seed'],generator_calls=s['generator_calls'],reused_modules=s['reused_modules'],
            all_passed=s['all_passed'],seconds=s['wall_seconds'],rows=rows))
    first=REPO/summary['runs'][0]['path'];c=json.loads((first/'compiled.json').read_text())
    graph=c['exploration_graph'];nodes={k:v['center']['position']for k,v in c['nodes'].items()}
    edges=[(e['from'],e['to'])for e in graph['edges']]
    (out/'exploration.svg').write_text(svg(nodes,edges,'Exploration · one fixed physical topology · 2 loops'))
    mission_nodes={k:v for k,v in nodes.items()if k in ['west','lookout','arch','east','bell','relay']}
    mission_edges=[('west','east'),('arch','lookout'),('bell','lookout'),('east','relay')]
    (out/'mission.svg').write_text(svg(mission_nodes,mission_edges,'Mission duties · route / earned treasure / merchant / return'))
    ideas=json.loads((first/'idea-proposals.json').read_text());families={v['novelty_family']:v for v in ideas['proposals']}
    library=list((batch/'library/payloads').glob('*/*/record.json'))
    result=dict(schema='pcg/ecosystem-review/v1',all_passed=summary['all_passed'],runs=runs,
        total_physical_cases=sum(len(r['rows'])for r in runs),held_cases=sum(v['held']for r in runs for v in r['rows']),
        topology=metrics(nodes,edges,'west','east'),physical_topologies=1,
        module_candidates=len(library),production_modules=0,
        content=dict(solid_rectangles=len(c['case']['platforms'])-len(c['case']['one_way_platform_indices']),
            one_way_rectangles=len(c['case']['one_way_platform_indices']),moving_platforms=len(c['case']['moving_platforms']),
            gears=len(c['case']['saws']),chests=len(c['case']['reward_sites']),merchants=len(c['case']['shop_sites']),enemies=len(c['case']['enemies'])),
        source_audit=json.loads((first/'assembly-audit.json').read_text()),
        gate_separation=json.loads((first/'gate-separation.json').read_text()),
        ideas=dict(relationship_families=len(families),implemented_rule_adapters=sum(v['relationship']['implemented']for v in families.values()),
            proposal_only=sum(not v['relationship']['implemented']for v in families.values()),validated_fun_count=0),
        limits=['One fixed eight-Macro physical topology; seeds test lifecycle, local timer demands and dynamic phases, not topological diversity',
            'Bootstrap generation adapts authored measured landforms; arbitrary new ideas still require a producer implementation',
            'Finite observable-state input policies; not human success rates or a universal movement solver',
            'General Module port/state relations remain UNKNOWN; only isolated instances may reuse these payloads',
            'No Boss fight, campaign or larger-region acceptance; human fun approval remains absent'])
    write(out/'results.json',result)
    trials=''.join(f'<tr><td>{html.escape(r["seed"])}</td><td>{r["generator_calls"]}</td><td>{r["reused_modules"]}</td><td>{sum(x["ok"]for x in r["rows"])}/{len(r["rows"])}</td><td>{r["seconds"]:.1f}s</td></tr>'for r in runs)
    cards=''.join(f'<li><b>{html.escape(k)}</b> · {"已有规则适配器"if v["relationship"]["implemented"]else"提案，尚无生成实现"}<br>{html.escape(v["relationship"]["decision"])}</li>'for k,v in families.items())
    videos=''.join(f'<article><h3>{title}</h3><video controls preload="metadata" src="{file}"></video><p><a href="{file}" download>下载完整短片</a> · 正常 1 倍速度、程序输入、末尾保留 1 秒完成画面。</p></article>'for title,file in [('A · 岩体反冲攀升、取宝、回程与购买','recoil-return.mp4'),('B · 双路线与敌人命中回充','reward-loop.mp4'),('C · 等门关闭后，从内部射铃返回','timed-return.mp4')])
    text=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Map 驱动的内容生态 · 第一轮真实闭环</title><style>body{{margin:auto;max-width:1160px;padding:24px;background:#12232b;color:#e8ede6;font:17px/1.6 system-ui}}a{{color:#e5c27b}}img,video{{width:100%;height:auto;background:#0d171d}}table{{border-collapse:collapse;width:100%}}td,th{{text-align:left;border-bottom:1px solid #456;padding:10px}}article,section{{margin:30px 0}}.pair{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}li{{margin:12px 0}}</style><h1>Map 驱动的内容生态 · 第一轮真实闭环</h1><p>8 个不同尺寸 Macro，直接拼接；双回环、3 个实体宝箱、商人、反冲攀岩与限时宝库。候选验证与人工趣味认可分开。</p><p><a href="index.html">打开真实 Godot 隔离试玩</a> · A/D 移动，空格跳跃，鼠标松开射击反冲，E 购买，M 整图，R 重试。</p><p><b>范围：</b>三个 Seed 检验补缺、复用和局部需求变更；使用同一张物理拓扑，不能视为三张不同探索地图。没有 Boss 战，尚未人工认可趣味。</p><h2>实际完整地图</h2><a href="whole-map.png"><img src="whole-map.png" alt="实际 Godot 全地图截图"></a><div class="pair"><img src="mission.svg" alt="任务职责图"><img src="exploration.svg" alt="探索拓扑图"></div><h2>产出与复用</h2><table><tr><th>Seed</th><th>生成调用</th><th>复用模块</th><th>真实整图策略通过</th><th>完整离线耗时</th></tr>{trials}</table><p>共 {result['total_physical_cases']} 条整图策略，其中 {result['held_cases']} 条独立动态相位样本。物理库候选 {len(library)} 个版本，生产准入 0。耗时含进程启动、物理测试、证据冻结和读写，不是 Runtime 帧率。</p><h2>关键路线录像</h2>{videos}<h2>创意与实现状态</h2><p>角色和参数变化不增加创意家族数量。以下是设计规则与提案，不是已被认可有趣的 Module 数量。</p><ul>{cards}</ul><h2>验证边界</h2><ul>{''.join('<li>'+html.escape(v)+'</li>'for v in result['limits'])}</ul><p><a href="results.json">结构化结果</a> · 原始失败、输入、源快照和压缩物理轨迹保存在 map-edit 版本化归档中。视频反馈可以直接在聊天中按 A/B/C 提供，无需填表。</p></html>'''
    (out/'report.html').write_text(text)
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--out',required=True);a=p.parse_args()
    result=build(a.batch,a.out);print(json.dumps({k:result[k]for k in ['all_passed','total_physical_cases','held_cases','module_candidates','content']},ensure_ascii=False))
