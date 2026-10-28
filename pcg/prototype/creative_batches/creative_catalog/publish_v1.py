"""Publish byte-identical documents/full films and marked, original-speed excerpts.

No physics or candidate selection happens here. Input is a frozen model-reviewed
selection and the original persistent CandidateLibrary audit.
"""
import argparse, hashlib, html, json, shutil, subprocess
from pathlib import Path

REPO=Path(__file__).resolve().parents[4]

def read(p):return json.loads((REPO/p).read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n')
def probe(p):return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]))

def media_index():
    result={}
    for c in read('pcg/creative-production/jump_wall/video-index-v1.json')['clips']:
        result[c['case_id']]=dict(path=c['path'],sha256=c['sha256'],trace=c['native_trace_path'],strict='passed',frames=c['frames_exact'],evidence=c['comparison_path'])
    for c in read('pcg/results/workshop-creative-grapple-videos-v2/delivery-v1.json')['clips']:
        m=read(c['manifest']);case=m['clips'][0]['id']
        result[case]=dict(path=c['mp4'],sha256=c['sha256'],trace=str(Path(c['mp4']).with_suffix('.trace.json')),strict='passed',frames=c['strict_frames'],evidence=c['manifest'])
    for c in read('pcg/results/workshop-creative-machinery-delivery-v19/manifest.json')['candidates']:
        m=read(c['video_manifest']);case=m['clips'][0]['id']
        result[case]=dict(path=c['video'],sha256=c['video_sha256'],trace=c['native_trace'],strict='passed',frames=c['native_exact_frames'],evidence=c['video_manifest'])
    for c in read('pcg/results/workshop-creative-resource-routes-native-v1/manifest-v1.json')['clips']:
        result[c['id']]=dict(path=c['file'],sha256=c['sha256'],trace=str(Path(c['raw_directory'])/(c['family']+'.trace.json')),strict=c['strict_comparison'],frames=c.get('frames_exact',0),evidence=c.get('original_movie_manifest',c['raw_directory']+'/strict-differences-v1.json'))
    for c in read('pcg/results/workshop-creative-enemy-world-videos-v2/playlist.json')['clips']:
        result[c['id']]=dict(path=c['path'],sha256=c['sha256'],trace=str(Path(c['path']).with_suffix('.trace.json')),strict='passed',frames=c['frames_exact'],evidence=c['manifest'])
    m=read('pcg/results/workshop-creative-occupancy-media-v1/manifest.json');c=m['clips'][0]
    result[c['id']]=dict(path='pcg/results/workshop-creative-occupancy-media-v1/'+c['file'],sha256=c['sha256'],trace='pcg/results/workshop-creative-occupancy-media-v1/'+c['family']+'.trace.json',strict='passed',frames=c['frames_exact'],evidence='pcg/results/workshop-creative-occupancy-media-v1/manifest.json')
    return result

DESCRIPTIONS={
'late-air-rise':'低檐限制提前上升，保留二跳到开阔处再用。',
'step-off-wall-return':'主动踏空获得墙面接触，再反蹬回高处；此样品没有普通跳跃。',
'switchback-wall-ascent':'利用对侧高墙换接触点，越过首墙的带刺段。',
'anchor-gap':'先挂停形成空中观察点，再主动选择离挂时机。',
'jump-refill':'先花掉二跳够环，再靠真实接触恢复二跳，跨向高岸。',
'bounce-brake':'弹钩自动抛出角色，同一次接触收益制造必须处理的新飞行。',
'attack-commit-relay':'维持视线诱使原生敌人发射，短门随攻击提交打开；随后避开真实弹丸。',
'saw-pursuit':'追随移动锯释放的空间，掉层离开它的返程轨道。',
'absorber-bell':'敌人身体吸收弹丸；清掉它才能露出真正的射铃通路。',
'sightline-backtrack':'从低处穿过遮挡，探身击中远铃，再折返进入原先关闭的左门。',
'live-enemy-pressure-support':'击退活敌使其压住感应区，借持续占区维持门。',
'trapdoor-commit':'射击打开脚下的桥，收益同时撤掉自身支撑并承诺下坠。',
'displace-landing':'敌人挤占真实身体落位间隙；击退或清除它才有安全着陆空间。',
'bell-wall-rebound':'反向射铃将角色推向侧墙，再借墙折返穿门。',
'hazard-window':'挂点给观察机会，自主周期危险决定离挂与落点窗口。',
'evacuate-rejoin':'载台驶向危险时先离台避难，再预测并重新截获同一载台。',
'moving-projectile-aperture':'角色不乘挡板，预测移动遮挡为弹丸留下的真实射线窗。',
'wall-slide-launch-window':'真实缓降不断损失发射高度，同时选择移动锯的通过窗口。',
'ordered-target-transaction':'两个目标同时可见可射，但原机关的操作顺序不可交换。',
'carrier-dual-service':'同一平台先占区作开门钥匙，再释放作运输支撑；两种用途不能同时保留。',
}

def publish(selection,catalog,dest):
    s=read(selection);cat=read(catalog);assert s['count']==cat['count']==20
    lookup=media_index()
    for r in s['selected']:
        assert r['case_id'] in lookup,r['case_id']
        assert r['relation_id'].split('/')[-1] in DESCRIPTIONS,r['relation_id']
    out=REPO/dest
    if out.exists():raise ValueError('immutable_publication_exists')
    for d in ['modules','videos','previews','cases']: (out/d).mkdir(parents=True,exist_ok=True)
    lookup=media_index();rows=[]
    for r,c in zip(s['selected'],cat['candidates']):
        assert r['version']==c['contentVersion'] and r['case_id']==c['canonical_case_id']
        mid=f"M{r['index']:02}";m=lookup[r['case_id']];src=REPO/m['path'];assert sha(src)==m['sha256']
        doc=REPO/r['module'];assert sha(doc)==r['module_sha256']
        shutil.copy2(doc,out/'modules'/f'{mid}.mapnote.json');shutil.copy2(doc.with_name(doc.name.replace('.mapnote.json','.svg')),out/'modules'/f'{mid}.svg')
        canonical_svg=json.loads(doc.read_text())['generationContract']['visualization']['path']
        shutil.copy2(doc.with_name(doc.name.replace('.mapnote.json','.svg')),out/'modules'/canonical_svg)
        shutil.copy2(src,out/'videos'/f'{mid}.mp4')
        case=read(c['casepath']);write(out/'cases'/f'{mid}.json',dict(cases=[case]))
        frames=read(m['trace'])['frames'];coins=frames[-1]['workshop']['coins']
        stable=next((f['frame']for f in frames if f['goal_stable_frames']>=6 and f['workshop']['coins']==coins),len(frames)-1)
        duration=float(probe(src)['format']['duration']);excerpt=min(duration,round((stable+1)/60+.7,3))
        title=out/'previews'/f'{mid}.title.txt';title.write_text(mid+'  '+r['name']+'  · 原速节选'+(' · 录像严格比较失败' if m['strict']!='passed'else''))
        target=out/'previews'/f'{mid}.mp4'
        cmd=['ffmpeg','-nostdin','-v','error','-i',str(src),'-t',str(excerpt),'-vf',f"scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,drawbox=x=0:y=0:w=iw:h=38:color=black@0.9:t=fill,drawtext=fontfile=/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc:textfile={title}:fontcolor=white:fontsize=23:x=12:y=3",'-an','-r','60','-c:v','libx264','-preset','fast','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(target)]
        subprocess.run(cmd,check=True)
        desc=DESCRIPTIONS[r['relation_id'].split('/')[-1]]
        rows.append(dict(index=r['index'],id=mid,name=r['name'],relation_id=r['relation_id'],description=desc,contentVersion=r['version'],module=f'modules/{mid}.mapnote.json',svg=f'modules/{mid}.svg',case=f'cases/{mid}.json',capabilities=case['capabilities'],scene=c['scene'],map_specification=case['map_specification'],full_video=f'videos/{mid}.mp4',video_sha256=m['sha256'],duration=duration,native_strict_comparison=m['strict'],native_frames=len(frames),strict_frames=m['frames'],recording_evidence=m['evidence'],original_trace=m['trace'],preview=f'previews/{mid}.mp4',preview_duration=excerpt,preview_sha256=sha(target),preview_edit='start through first stable rewarded exit + 0.6s; original speed; full original movie retained',holdout=r['technical_evidence']['holdout'],proposal_source=r['proposal_source'],limitations=c['limitations'],production_admitted=False,human_fun='unreviewed'))
        print(mid,r['name'],m['strict'],excerpt,flush=True)
    groups=[('movement',[1,2,3,14,18]),('grapple',[4,5,6,15]),('world',[7,9,10,11,12,13,19]),('dynamic',[8,16,17,20])];montages=[]
    for name,ids in groups+[('all',list(range(1,21)))]:
        files=[next(r for r in rows if r['index']==i)for i in ids];listing=out/'previews'/f'{name}.concat.txt';listing.write_text(''.join("file '"+Path(r['preview']).name+"'\n"for r in files))
        path=out/f'{name}.mp4';subprocess.run(['ffmpeg','-nostdin','-v','error','-f','concat','-safe','0','-i',str(listing),'-an','-c','copy','-movflags','+faststart',str(path)],check=True)
        t=0;chapters=[]
        for r in files:
            dur=float(probe(out/r['preview'])['format']['duration']);chapters.append(dict(id=r['id'],name=r['name'],start=round(t,3),end=round(t+dur,3)));t+=dur
        montages.append(dict(id=name,file=path.name,sha256=sha(path),bytes=path.stat().st_size,duration=float(probe(path)['format']['duration']),chapters=chapters,editing='Cuts between modules; labels show boundaries. No acceleration; original full films linked individually.'))
    manifest=dict(schema='pcg/creative20-publication/v1',count=20,selection=selection,selection_sha256=sha(REPO/selection),catalog=catalog,catalog_sha256=sha(REPO/catalog),clips=rows,montages=montages,strict_native_passed=sum(r['native_strict_comparison']=='passed'for r in rows),whole_map='UNKNOWN',human_video_observation='unreviewed',human_playtest='unreviewed',production_admitted=False)
    write(out/'manifest.json',manifest)
    shutil.copy2(REPO/catalog,out/'candidate-catalog.json')
    shutil.copy2((REPO/catalog).parent/'retrieve.json',out/'retrieval.json')
    shutil.copy2(REPO/'pcg/results/workshop-creative20-validation-v1/summary.json',out/'validation-summary.json')
    cards=[]
    for r in rows:
        esc=html.escape
        cards.append(f'''<article id="{r['id']}" data-search="{esc(r['name']+' '+r['relation_id']+' '+' '.join(r['capabilities']))}"><h2>{r['id']} {esc(r['name'])}</h2><p>{esc(r['description'])}</p><video controls preload="metadata" src="{r['preview']}"></video><p><a href="{r['full_video']}">完整原生录像</a> · <a href="{r['module']}">标准 Module</a> · <a href="{r['svg']}">SVG</a> · <a href="{r['case']}">试玩输入</a></p><p class="meta">能力：{esc(' / '.join(r['capabilities']))}；留出 {r['holdout']['safe_stable']}/{r['holdout']['trials']}；录像严格比较 {r['native_strict_comparison']}</p><code>python3 -m pcg.prototype.creative_batches.catalog_v4 --play {r['index']}</code></article>''')
    (out/'index.html').write_text('''<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>失序之钟 · 20种新玩法</title><style>body{margin:30px auto;padding:0 20px;max-width:1280px;background:#10151c;color:#e2e9ee;font:16px/1.6 system-ui}a{color:#80d9d0}h1{font-size:30px}input{padding:12px;width:70%;max-width:600px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(360px,1fr));gap:20px}article{padding:18px;background:#1b242e;border:1px solid #334352;border-radius:12px}h2{font-size:20px}video{width:100%}.meta{color:#b9c9d5}code{font-size:12px;overflow-wrap:anywhere}article[hidden]{display:none}</style><h1>20种不同玩法 · 真实 Godot 候选</h1><p>模型提出与实现，程序搜索，原物理验证，独立模型审查。旧六家族不计入。人工趣味、实际试玩与生产认可待评；通用拼接与整图 UNKNOWN。</p><p>原速节选保留通过动作；各卡可下载完整原生片、标准JSON与SVG。M12录像有32处support_id差异，严格比较失败，保留review-only；局部物理候选独立有效。</p><p>分组下载：<a href="movement.mp4">墙面与跳跃</a> · <a href="grapple.mp4">钩索</a> · <a href="world.mp4">人物与世界</a> · <a href="dynamic.mp4">动态空间</a> · <a href="all.mp4">全部节选</a> · <a href="README.md">复现说明</a></p><input placeholder="搜索玩法、能力或关系ID" oninput="document.querySelectorAll('article').forEach(x=>x.hidden=!x.dataset.search.toLowerCase().includes(this.value.toLowerCase()))"><main>'''+''.join(cards)+'</main></html>')
    md=['# 20种新玩法 Module','', '本轮主交付20种不同因果关系；旧六家族不计入。全部为真实Godot技术候选，人工趣味/试玩/生产认可待评。通用接缝与整图UNKNOWN。','', '[全部原速节选](all.mp4) · [墙面跳跃](movement.mp4) · [钩索](grapple.mp4) · [人物与世界](world.mp4) · [动态空间](dynamic.mp4)','', '节选只在模块之间剪切，并截去稳定领取后的尾部等待；完整原生视频逐项保留。M12完整原片安全完成，但32处support_id差异使严格比较失败，标记review-only。其余19片完整严格比较通过。','', '|编号|玩法关系|完整录像|标准文档|独立留出|','|---|---|---|---|---|']
    for r in rows:md.append(f"|{r['id']}|{r['name']}：{r['description']}|[MP4]({r['full_video']})|[JSON]({r['module']}) / [SVG]({r['svg']})|{r['holdout']['safe_stable']}/{r['holdout']['trials']}|")
    md+=['','## 试玩与复现','','在仓库根恢复运行时和本批原件，使用官方Godot4.7.2：','','```sh','python3 pcg/tools/restore_archive.py godot-runtime-v1 --extract','python3 pcg/tools/restore_archive.py content-workshop-creative20-v1 --extract','python3 -m pcg.prototype.creative_batches.catalog_v4 --list','python3 -m pcg.prototype.creative_batches.catalog_v4 --play 1','```','','A/D移动、空格跳、左键射击、E/右键钩索；仅样品声明的能力生效。Retry重新开始，Replay播放实际见证。各自有Cell需要catalog指定的真实消费者场景。命令不会修改正式主游戏。','','[完整报告](../../../docs/l4-mapgen/content-workshop-creative20-v1.md) · [模型创意skill](../../../.agents/skills/pcg-creative-producer/SKILL.md) · [完整索引](manifest.json)']
    (out/'README.md').write_text('\n'.join(md)+'\n')
    print(json.dumps(dict(count=20,out=dest,strict_native_passed=manifest['strict_native_passed'],montages=montages),ensure_ascii=False))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--selection',required=True);p.add_argument('--catalog',required=True);p.add_argument('--out',required=True);a=p.parse_args();publish(a.selection,a.catalog,a.out)
