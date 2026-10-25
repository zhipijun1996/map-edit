"""Readable views of actual geometry and real trajectories, with failed gates."""
import argparse,html,json,gzip,shutil
from pathlib import Path
from .evaluate import traces,run as evaluate
from ..director import REPO
from ..run import write
from ..valley_complete.compare import svg
from pcg.prototype.factory.core.engine import file_sha

SOURCE=REPO/'pcg/results/full-region-phase-aware-calibration-v1'
RUNS=[REPO/'pcg/results'/v for v in ['full-region-phase-aware-routes-v1','full-region-phase-aware-core-v1','full-region-phase-aware-holdout-v1']]

def build(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 c=json.loads((SOURCE/'compiled.json').read_text());g=c['exploration_graph']
 data=evaluate(SOURCE,RUNS,out/'diagnostics.json')
 (out/'exploration.svg').write_text(svg({k:v['center']['position']for k,v in c['nodes'].items()},[(e['from'],e['to'])for e in g['edges']], '39 地点探索图 · 实际接触布局 · 奖励职责未完成'))
 bounds=c['case']['world_bounds'];x,y,w,h=bounds
 parts=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x-80} {y-180} {w+160} {h+320}"><rect x="{x-80}" y="{y-180}" width="{w+160}" height="{h+320}" fill="#14232b"/>',f'<text x="{x}" y="{y-60}" fill="#f0d9ae" font-size="72">实际碰撞地形与真实输入轨迹 · 奖励 / Boss 尚未接入</text>']
 one=set(c['case']['one_way_platform_indices'])
 for i,(a,b,u,v)in enumerate(c['case']['platforms']):parts.append(f'<rect x="{a}" y="{b}" width="{u}" height="{v}" fill="{"#7b9790"if i in one else"#aaa16e"}"/>')
 for index,(case,r)in enumerate(traces(RUNS[0])):
  if index==2:break
  points=' '.join(f'{f["x"]},{f["y"]}'for f in r['frames'][::4]);color=['#54d5ce','#edb95f'][index]
  parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="12" stroke-opacity=".9"/>')
 for k,n in c['nodes'].items():
  a,b=n['center']['position'];parts.append(f'<circle cx="{a}" cy="{b}" r="19" fill="#faf0c9"/><text x="{a+28}" y="{b-16}" fill="#faf0c9" font-size="52">{html.escape(k)}</text>')
 (out/'actual-routes.svg').write_text(''.join(parts)+'</svg>')
 baseline=json.loads((REPO/'pcg/results/full-region-baseline-sizes-v1/sizes.json').read_text())
 write(out/'baseline.json',baseline)
 write(out/'mission-status.json',dict(objectives=[dict(id=n['id'],role=n['role'],district=n['district'],planned_reward=n['reward'],status='UNMATERIALIZED'if n['reward']or n['role']=='boss'else'finite_instance_routes_only')for n in g['nodes']],
  scope='Original Director responsibilities retained; a visited location grants no unmaterialized chest or reward return flag'))
 rows=[]
 for r in data['rows']:
  if r['run'].endswith('routes-v1'):rows.append(f'<tr><td>{html.escape(r["id"])}</td><td>{r["seconds"]:.1f} 秒</td><td>{r["shots"]}</td><td>{"通过"if r["passed"]else"失败"}</td></tr>')
 (out/'report.html').write_text('''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>平原整图拼装与反馈实验</title><style>body{background:#15252a;color:#e0e8df;font:17px/1.7 system-ui;margin:30px auto;max-width:1200px;padding:0 20px}a{color:#8ad8d0}img,video{max-width:100%;background:#102025}table{border-collapse:collapse}td,th{padding:8px;border:1px solid #58716d}.status{border-left:5px solid #e7b36c;padding:12px;background:#243438}</style>
<h1>平原整图拼装与失败反馈实验</h1><p class="status">39 个真实 Macro、32 个核心探索地点，已接入完整 Godot 物理世界。当前仍是工程候选：地形过于规则、行动家族重复，宝箱、敌人生态和 Boss 尚未落实；设计目标未达成，不进入生产库。</p>
<p><a href="index.html">调试试玩（奖励 / Boss 未接入）</a> · <a href="diagnostics.json">结构化验证数据</a> · <a href="baseline.json">正式主线规模基线</a> · <a href="mission-status.json">任务职责与未完成项</a></p>
<h2>真实整图</h2><p>Godot 实例化的完整地形；没有 Map 填充平台。点击查看原图。</p><a href="whole-map.png"><img src="whole-map.png"></a>
<h2>真实路线与探索网络</h2><p>青 / 金线来自两条完整实际轨迹。它们不是任务可达性的抽象替代；未落实的奖励与回程条件仍阻止整图验收。</p><img src="actual-routes.svg"><img src="exploration.svg">
<h2>关键路线录像</h2><p>程序输入回放，1 倍速，原生帧对照通过。短片为连续摘录；完整路线保留等待和恢复。</p><video controls preload="metadata" src="recoil-excerpt.mp4"></video><p><a href="recoil-excerpt.mp4">下载连续短片</a> · <a href="full-main.mp4">下载完整主路线</a></p>
<table><tr><th>固定策略</th><th>实际时长</th><th>射击</th><th>结果</th></tr>'''+''.join(rows)+'''</table>
<h2>当前结论</h2><p>旧内容直接扩大时，主路 127 秒且没有开枪，已淘汰。内容反馈后主路约 82 秒、6 次空中击铃反冲。端口间距和跨井相位约束已补入现有流程。站立等待、瞄准和稳定到达仍占相当部分，尚不能宣称节奏优于正式游戏。</p><p>正式单图为 20–23 地点、58–68 个较小 Module；这里是 39 个 Macro，两种粒度不可直接比较。当前占地外框约 7232×4844 世界单位，较大的探索网络不代表已实现更大的有效探索空间。96–128 内容预算、更丰富的区域地形、奖励深度及趣味验收仍未完成。</p><p>没有新真人试玩或趣味认可。核心有限路线、独立相位样本与技术验证，均不替代全部状态下的防 Softlock、真实奖励回程与整图品质。</p>''')
 return data
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();build(a.out)
