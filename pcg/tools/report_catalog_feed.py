"""Review all frozen Seeds, including failures and unadapted library entries."""
import gzip,html,json,os,shutil
from pathlib import Path
from pcg.map_directed.director import REPO
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha
OUT=REPO/'generation/maps/catalog-feed-v1'
SOURCE='734399fa1b04fb27794d8c73cb77c58ed1fd4574'
def link(a,b):
 if b.exists():assert file_sha(a)==file_sha(b);return
 os.link(a,b)
def physical(folder):
 cs=json.loads((folder/'cases.json').read_text())['cases'];bs=json.loads((folder/'physics/batches.json').read_text());rows=[];seams=set()
 for c,b in zip(cs,bs):
  raw=gzip.decompress((folder/'physics'/b['gzip_path']).read_bytes());assert __import__('hashlib').sha256(raw).hexdigest()==b['raw_output_sha256']
  r=json.loads(raw)['results'][0];completed={l['id']for l in r['pilot']['legs']if l.get('ok')}
  for l in c['pilot_program']:
   if l['id']in completed and l.get('edge_terminal'):seams.add((l['edge_id'],l['edge_from'],l['edge_to']))
  failure=r['pilot'].get('failure')or{}
  if not r['ok']and not failure and r.get('frames'):
   f=r['frames'][-1];failure=dict(frame=f['frame'],leg_id=f['pilot']['current_leg_id'],position=[f['x'],f['y']],reason=r['reason'])
  rows.append(dict(id=c['id'],ok=r['ok'],reason=r['reason'],ticks=r['ticks'],shots=r['shots'],airborne_shots=sum(1 for f in r['frames']for a in f['accepted']if a['type']=='shot'and not f['grounded']),player_health=r['hp'],actual_chests=sum(e['type']=='chest_claim'and e['accepted']for e in r['extra']['workshop']['events']),actual_coins=r['extra']['workshop']['coins'],stationary_grounded_fraction=sum(f['grounded']and abs(f['real_velocity'][0])<=1 for f in r['frames'])/len(r['frames']),failure=failure))
 return dict(routes=rows,passed=sum(r['ok']for r in rows),total=len(rows),directed_seams_completed=[list(v)for v in sorted(seams)],scope='Real continuous whole-world finite policies; failures do not prove impossibility')
def build():
 if(OUT/'results.json').exists():raise ValueError('immutable_report_exists')
 records=[];used=set();used44=set();names={x['contentVersion']:x['title']for x in json.loads((REPO/'library/workshop/catalog.json').read_text())['modules']}
 for i in range(3):
  folder=REPO/f'pcg/results/catalog94-evaluation-{i}-v1'
  geometry=json.loads((folder/'compiled.json').read_text());physics=REPO/'pcg/results/catalog94-evaluation-2-v1-replay'if i==2 else folder
  versions={m['source_version']for m in geometry['modules']};used|=versions;s=json.loads((folder/'search-attempts.json').read_text())
  records.append(dict(seed='catalog94-eval-'+str(i),physics=str(physics.relative_to(REPO)),geometry=str(folder.relative_to(REPO)),modules=len(geometry['modules']),distinct_source_versions=len(versions),versions=sorted(versions),module_titles=[dict(node=m['id'],version=m['source_version'],title=names[m['source_version']])for m in geometry['modules']],latches=len(geometry['case']['latches']),carriers=len(geometry['case']['moving_platforms']),saws=len(geometry['case']['saws']),enemies=len(geometry['case']['enemies']),world_bounds=geometry['case']['world_bounds'],search_seconds=sum(r['wall_seconds']for r in s),search_expansions=sum(r['expanded']for r in s),search_attempts=len(s),audit=json.loads((folder/'assembly-audit.json').read_text()),**physical(physics)))
 old=[]
 for i in range(3):
  p=REPO/f'pcg/results/catalog-feed-evaluation-{i}-v1';c=json.loads((p/'compiled.json').read_text());used44|={m['source_version']for m in c['modules']};old.append(dict(seed='catalog-eval-'+str(i),**physical(p)))
 inventory=json.loads((REPO/'pcg/results/catalog-feed-audit-v2/interfaces.json').read_text())
 for row in inventory['rows']:
  row['placed_in_current_three_maps']=row['version']in used
  row['used_in_map_seeds']=[r['seed']for r in records if row['version']in r['versions']]
  p=REPO/'library/workshop/thumbnails'/(row['version'][7:]+'.svg');link(p,OUT/('module-'+row['version'][7:]+'.svg'))
 movies=[]
 for directory,name in [('latest94-route','latest94-route.mp4'),('evaluation-route','prior44-route.mp4')]:
  p=OUT/directory;m=json.loads((p/'manifest.json').read_text());assert m['comparison']['passed'];assert file_sha(p/m['file'])==m['sha256'];link(p/m['file'],OUT/name);movies.append(dict(m,file=name))
 result=dict(schema='pcg/current-library-map-experiment/v2',source_commit=SOURCE,latest_main='54d0cfc494936bb74bd9912324a840285212b995',library_source='6de70fb0482e38f31048253dcd78bf2c0f62dbfa',source_versions=94,source_routes_passed=121,plains_selected=82,source_adapter_candidates=50,unique_versions_placed=len(used),records=records,total_passed=sum(r['passed']for r in records),total_routes=12,fully_passed_maps=sum(r['passed']==4 for r in records),inventory=inventory,previous44=dict(versions=44,source_passed=52,unique_versions_placed=len(used44),records=old,total_passed=sum(r['passed']for r in old)),movies=movies,production_admitted=False,human_fun='unreviewed',stable_superiority_proved=False,holdout='NOT_RUN: nominal whole-map failures already block admission',topology='Fixed two directed split/rejoin diamonds, 16 nodes and 17 seams; no new topology diversity claim',seed2_replay='Original run interrupted by frozen-source guard after recorder-only change; same compiled geometry and Seed rerun in full, original outputs kept',scope='Library growth integration experiment. Source, exterior-adapter and whole-map success are distinct. New content and safeguards differ, so this is not a controlled algorithm superiority comparison')
 write(OUT/'results.json',result);write(OUT/'library-coverage.json',inventory)
 table=''.join(f'<tr><td>{r["seed"]}</td><td>{r["distinct_source_versions"]}/16</td><td>{r["passed"]}/4</td><td>{r["latches"]} / {r["carriers"]} / {r["enemies"]}</td><td>{r["search_seconds"]:.3f}s / {r["search_expansions"]}</td></tr>'for r in records)
 gallery=''.join(f'<article><h2>整图 {i} · {r["passed"]}/4 路线通过</h2><a href="latest94-map-{i}.png"><img src="latest94-map-{i}.png"></a><details><summary>实际拼入的全部 Module</summary>'+''.join(f'<p>{html.escape(m["node"])} · <a href="module-{m["version"][7:]}.svg">{html.escape(m["title"])}</a></p>'for m in r['module_titles'])+'</details></article>'for i,r in enumerate(records))
 library=''.join(f'<tr><td><a href="module-{r["version"][7:]}.svg">{html.escape(r["title"])}</a></td><td>{r["ports"]}</td><td>{"已拼入"if r["placed_in_current_three_maps"]else"未拼入"}</td><td>{html.escape(r["adapter"])}</td></tr>'for r in inventory['rows'])
 failures=''.join(f'<p>{r["seed"]} / {x["id"]}: {x["reason"]}, frame {x["failure"].get("frame")}, {html.escape(x["failure"].get("leg_id",""))}</p>'for r in records for x in r['routes']if not x['ok'])
 page=f'''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>94版 Module 库接入：全部整图与失败</title><style>body{{background:#111b25;color:#e5edf0;max-width:1380px;margin:auto;padding:24px;font:17px/1.7 system-ui}}a{{color:#79ddc8}}img,video{{width:100%}}article{{padding:12px;background:#192a38;margin:24px 0}}table{{border-collapse:collapse;width:100%;font-size:15px}}td,th{{border:1px solid #4a6676;padding:8px}}strong{{color:#ffce86}}</style>
<h1>把最新 Module 库真正放进完整 Map</h1><p><strong>内容变化可见；整图稳定性尚未达标。</strong>94版库、82版平原候选，原始121条路线全部重新通过。50个双口版本可进入当前外部接口适配搜索，三张预定Seed实际拼入{len(used)}个不同原版本。每张16个实例，Map新增地形为0；没有补路短平台。</p>
<p>整图连续路线 {result['total_passed']}/12，通过全部四路线的地图 {result['fully_passed_maps']}/3。失败地图保留。多端口不等于有设计的路口：15版多口的设计审查仍无通用路口准入，本轮保留实验分流/汇合，不把旧三口改名当新设计。</p>
<p><a href="index.html">手动试玩：Seed1 四路线均通过的实际 Godot 地图</a> · <a href="results.json">全部结果、奖励事务与失败 JSON</a> · <a href="library-coverage.json">94版逐项匹配/未采用原因</a></p>
<table><tr><th>Seed</th><th>不同原版本/实例</th><th>完整路线</th><th>铃/移动体/敌人</th><th>空间搜索/扩展</th></tr>{table}</table>
<h2>最新94版库：连续实际路线</h2><p>Seed1，高路→高路，正常1倍、60Hz、960×540，约37秒，13次开枪。不是单Module视频。每帧位置、速度、输入、资源、机关、敌人与最终奖励事务和无画面验证严格一致；末尾1秒冻结。程序输入，不是人工趣味认可。</p><video controls preload="metadata" src="latest94-route.mp4"></video><a href="latest94-route.mp4" download>下载完整MP4</a>{gallery}
<h2>从44版快照到94版快照</h2><p>本轮开始时44版库的52源路线通过；3张图合计只采用12个不同版本，连续路线5/12。期间新库发布50版，已重新读取94版、重验121路线并重做地图。前后内容、选择优先级和动态扫掠检查有变化，不能把通过率变化归因为某个算法更强。</p><video controls preload="metadata" src="prior44-route.mp4"></video><p>上片明确为本轮早期44版快照，不是94版结果。</p>
<h2>原八模板与正式游戏：历史图片参照</h2><img src="previous-eight-map.png"><p>上图为此前8模板空间搜索原型，本轮没有重新录制；原轮常规30/30、扰动27/30。新图挑战关系和可用版本更多，端口适配成功率更差。不同内容，不能直接作公平胜率比较。</p><img src="formal-main-history.png"><p>正式主游戏当前美术入口的历史截图，只比较构图观感。本轮实际使用相同正式角色/岩体/机关表现；仍存在悬浮矩形岸、过长岸体、规则双分流和空白区域。加库存与材质未解决地貌协调感。没有主游戏整图物理对照的新结论。</p>
<h2>失败与接口缺口</h2>{failures}<p>单模块到达目标并不保证安全离场；后挡墙/闭门内侧的出生点并不保证可从外面进入；原始落点容差也未必适合连续接缝。移动平台全行程已参与外部碰撞筛查，完全相同的显式共享落点只算一个原碰撞体。新几何版本仍须整图重验。</p><p>当前只有落地端口；高速空中互接、保证回程、完整门绕行反例、商店/Boss和更多探索拓扑没有在本轮证明。没有以抽象图或源Module成功代替整图成功，也未为失败Seed改几何重测留出。未运行新扰动留出，因为常规失败已阻止准入。</p>
<h2>全部94版清单</h2><p>50可进入当前适配；15多口需要明确有向关系与职责适配；12被平原能力/内容筛选排除；11返身/折返需要不同外轮廓接口；3入口后墙、3活敌离场冲突。未采用不表示该源挑战不好。</p><table><tr><th>内容（点击看原Module）</th><th>端口</th><th>本批整图</th><th>接口结果</th></tr>{library}</table>
<h2>下一步</h2><p>优先用本批实际失败需求扩充安全入口/安全离场与容错落点契约，让Map在有限预算内替换不满足的候选；单独创作真正有空间选择的分流/汇合Macro。再加入连续岩体、空腔与地标骨架，减少矩形长岸。固定新内容后做同内容旧/新布局与独立扰动对照。</p><p>算法冻结 {SOURCE}。原库94版来源6de70fb，main54d0cfc；所有失败、两次源码冻结中止、重跑、原输入/帧/文档、媒体与公共字节核验均保留在版本化归档。没有人类趣味/生产认可。</p>'''
 (OUT/'report.html').write_text(page);return result
if __name__=='__main__':
 r=build();print(json.dumps({k:r[k]for k in ['unique_versions_placed','total_passed','fully_passed_maps']}))
