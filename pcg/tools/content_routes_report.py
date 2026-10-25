"""Compare actual traces with the rejected parent and current formal game."""
import argparse,gzip,html,json,shutil
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha

def traces(run):
    run=Path(run);cases={c['id']:c for c in json.loads((run/'cases.json').read_text())['cases']};rows=[]
    for b in json.loads((run/'physics/batches.json').read_text()):
        raw=gzip.decompress((run/'physics'/b['gzip_path']).read_bytes())
        import hashlib
        if hashlib.sha256(raw).hexdigest()!=b['raw_output_sha256']:raise ValueError('raw_evidence_drift')
        for r in json.loads(raw)['results']:
            case=cases[r['id']];legs={l['id']:l for l in case['pilot_program']};n=len(r['frames'])
            walks=sum(l['ticks']for l in r['pilot']['legs']if l.get('ok')and l['kind']=='walk')
            events=r['plains']['events'];shots=[e for e in events if e['type']=='shot_origin'];hits=[e for e in events if e['type']=='enemy_hit'and e.get('fired_airborne')]
            bells=[e for e in events if e['type']=='bell_open'];angles={tuple(round(x,1)for x in e['direction'])for e in shots}
            rows.append(dict(id=r['id'],ok=r['ok'],seconds=r['ticks']/60,shots=r['shots'],walk_policy_fraction=walks/max(1,n),
                ground_moving_fraction=sum(f['grounded']and abs(f['vx'])>10 for f in r['frames'])/max(1,n),
                airborne_enemy_hits=len(hits),actual_bell_opens=len(bells),shot_direction_bins=len(angles),
                defeated_world_policies=sum(bool(l.get('observed_enemy_defeated'))for l in r['pilot']['legs']),
                actual_chests=len([e for e in r.get('extra',{}).get('optional_challenge_events',[])if e.get('accepted')]),
                held=bool(case.get('holdout')),human_fun_score=None))
    return rows

def build(run,out):
    run=Path(run).resolve();out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    if(out/'report.html').exists():raise ValueError('immutable_content_report_exists')
    c=json.loads((run/'compiled.json').read_text());rows=traces(run);old=traces(REPO/'pcg/results/woven-release-v1')
    baseline=REPO/'pcg/results/content-formal-baseline-v1';formal=json.loads((baseline/'capture.json').read_text());live=json.loads((baseline/'live.json').read_text())
    formal_rows=[]
    for raw in formal['rows']:
        m=raw['manifest'];formal_rows.append(dict(seed=raw['seed'],ok=raw['ok'],version=m['version'],manifest_hash=m['manifest_hash'],
            places=len(m['areas']),modules=len(m['nodes']),edges=len(m['connections']),enemies=len(m['enemies']),chests=len(m['rewards']),
            recipe_ids=sorted({e.get('recipe','')for e in m['connections']}),generation_ms=raw['generation_usec']/1000))
    selected=[r for r in rows if not r['held']and 'coverage'not in r['id']]
    frames=live['frames'];formal_live=dict(route_reached=live['route_reached'],seconds=live['tick_count']/60,
        shots=sum(e['kind']=='shot_accepted'for e in live['events']),health_start=frames[0]['health'],health_end=frames[-1]['health'],
        ground_moving_fraction=sum(f['grounded']and abs(f['velocity'][0])>10 for f in frames)/len(frames),
        scope='Actual current DemoApp, fast / kill_from_bank_v2 to Boss preparation, no Boss fight; different map scale and policy')
    result=dict(schema='pcg/content-routes-comparison/v1',source_commit=json.loads((run/'module-library/bundle.json').read_text())['sourceCommit']if(run/'module-library/bundle.json').exists()else __import__('subprocess').check_output(['git','rev-parse','HEAD'],cwd=REPO,text=True).strip(),
        source_run=str(run.relative_to(REPO)),compiled_sha256=file_sha(run/'compiled.json'),
        parent=dict(run='woven-release-v1',rows=[r for r in old if not r['held']and 'coverage'not in r['id']]),
        revised=dict(modules=len(c['modules']),seams=len(c['seams']),physical_topologies=1,rows=rows,changed_challenge_modules=[m['id']for m in c['modules']if m.get('realized_challenge')],
            content={k:len(c['case'][k])for k in ['enemies','latches','thorns','moving_platforms','reward_sites','shop_sites']},
            generation=json.loads((run/'generation-log.json').read_text()),whole_map_passed=json.loads((run/'summary.json').read_text())['all_passed']),
        formal_main_commit='26e7f2a4459623f35613a857da8a75e89daa3e62',formal_generations=formal_rows,formal_live=formal_live,
        cautions=['No automatic fun score or human approval; improvements below are design hypotheses and measured action differences.',
            'Parent and revised share the same topology and initial capability; formal has different scale, content budget and pilot. Route times are not difficulty or fun rankings.',
            'Only four Macro content roles were revised. Many vertical recoil transfers and long branch approaches remain.',
            'Inline tunnel gates define the tested low passage, not a proven global ability lock. Skilled higher-route bypass remains an explicit unverified boundary; only treasure chambers have solid-enclosure checks.',
            'Enemy refund is a useful witnessed strategy, not a proof that no single-shot alternate route exists.',
            'One physical topology; no Boss, campaign persistence, broad semantic matching or production admission.'],human_fun='awaiting_user_video_observation',production_admitted=False)
    write(out/'results.json',result)
    route_rows=''.join(f'<tr><td>{html.escape(r["id"].removeprefix("woven-plains-"))}</td><td>{r["seconds"]:.1f}s</td><td>{r["shots"]}</td><td>{r["walk_policy_fraction"]:.1%}</td><td>{r["airborne_enemy_hits"]}</td><td>{r["actual_bell_opens"]}</td></tr>'for r in selected)
    comparison='''<tr><td>探索骨架</td><td>19 Macro / 27 接缝；本轮一张冻结图</td><td>20 探索地点 / 59–63 实例；五 Seed 三种空间家族</td></tr><tr><td>动作内容</td><td>四处需求适配：限时击铃反冲、真实敌人回充、尖刺岩拱；保留两种宝库</td><td>已有远程顺序铃、受控渡台、齿轮、荆棘、反冲跨度等配方及区域分配</td></tr><tr><td>生态与完成度</td><td>1敌人、2宝箱、1商人；无Boss战、战役</td><td>15–19敌人、4宝箱、商人、Boss及跨图流程</td></tr><tr><td>本轮取舍</td><td>加强主动射击，保留零填充拼接与真实回程；内容仍不够丰富</td><td>借鉴其内容配方、区域身份、恢复带和生态；不能只复制房间数量</td></tr>'''
    videos=''.join(f'<article><h3>{label}</h3><video controls preload="metadata" src="{file}"></video><p><a href="{file}" download>下载完整录像</a> · 正常1倍 / 程序输入；保留原始连续过程。</p></article>'for label,file in [('A 主线：空中击铃 → 命中回充 → 岩拱','main-route.mp4'),('B 奖励远征与回程：进阶限时通道 → 实体宝库','reward-route.mp4')])
    page=f'''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>风隙回响 · 内容驱动整图对照</title><style>body{{margin:auto;max-width:1180px;padding:24px;background:#12262d;color:#e8eee4;font:17px/1.65 system-ui}}a{{color:#e4c27a}}img,video{{width:100%;height:auto}}td,th{{padding:10px;text-align:left;border-bottom:1px solid #456}}table{{border-collapse:collapse;width:100%}}article{{margin:28px 0}}</style><h1>风铃平原 · 风隙回响</h1><p><a href="index.html">真实 Godot 整图试玩</a> · A/D 移动，Space 单跳，鼠标松开反冲，S 下穿，E 购买，M 整图。</p><p>保留上一轮19 Macro多环路整图，按具体动作需求修订四处内容。其余15份内容复用；Map新增连接地形0。技术通过不等于好玩，等待这轮实际视频反馈。</p><h2>本轮整图</h2><a href="whole-map.png"><img src="whole-map.png"></a><h2>关键路线</h2>{videos}<h2>与上一轮相比，好在哪里</h2><p>入口不再只是跑过地形：空中向后击铃的同一枪负责开门与穿越。主线加入真实敌人命中回充和第二次反冲；出口前增加实际尖刺净空。回程验证保留敌人受伤、死亡及门关闭后的状态，不靠重置恢复成功。</p><h2>仍然差在哪里，哪些地方可能更差</h2><p>只有四处内容得到修订，其余长廊和反冲竖井仍重复，替代主路线改善较少。入口限时与尖刺提高了失败压力，缺少足够教学与可恢复失误区；测试通过不能代替手感认可。岩廊因动作净空而局部变薄，地貌与动作仍需联合设计。通路铃不能冒称不可绕过的全局锁，真正宝箱腔另做闭门隔离检查。</p><table><tr><th>路线</th><th>实测程序耗时</th><th>射击</th><th>走路策略时间</th><th>空中敌人命中</th><th>实际开铃</th></tr>{route_rows}</table><p>走路策略含到达稳定，不能当纯跑图比例；更多射击也不能直接当趣味评分。</p><h2>与主游戏当前正式Map比较</h2><table><tr><th>维度</th><th>本轮实验图</th><th>主游戏正式v12</th></tr>{comparison}</table><p>主游戏五 Seed 已重新实际生成；一条当前正式主路线实际运行到Boss准备区。地图规模、内容预算和输入策略不同，不用通关秒数判优劣。</p><h2>下一步取其精华</h2><p>沿用主游戏的动作配方、区域身份、战斗与恢复节奏；结合本研究的探索职责、直接拼接、收益保护和连续回程验证。先让少量明显不同的挑战形成完整体验段，再由它们约束形状与端口。扩大库前先审核原型；不能适配就反馈导演，不能删挑战后继续算成功。</p><p><a href="results.json">结构化三方对照、原始证据与限制</a> · 人工趣味认可0，生产准入关闭。</p></html>'''
    (out/'report.html').write_text(page);return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--out',required=True);a=p.parse_args();r=build(a.run,a.out);print(json.dumps(r['revised']['content']))
