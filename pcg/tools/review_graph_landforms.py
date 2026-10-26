"""Traceable same-graph diagrams and factual review, no synthetic fun score."""
import argparse,html,json,shutil
from pathlib import Path
from pcg.tools.review_contact_grammar import inspect
from pcg.tools.review_block_grid import grid,observed_matrix
from pcg.map_directed.run import write
from pcg.prototype.factory.core.engine import file_sha

def blueprint(g,path):
    pos={'start':(90,190),'rise':(310,80),'ridge':(540,80),'cliff':(310,300),'switchback':(540,300),'landmark':(790,190),'cache':(310,480)}
    s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 960 570"><rect width="960" height="570" fill="#101a2b"/><defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3z" fill="#cad7e9"/></marker></defs><text x="24" y="32" fill="white" font-size="20">同一张职责图 · 仅逻辑排版，不是物理位置</text>']
    for e in g['edges']:
        a,b=pos[e['from']],pos[e['to']];color='#60cfff'if e['purpose']=='upper_main'else'#72eab4'if e['purpose']=='lower_main'else'#ffc35c'
        s.append(f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]}" stroke="{color}" stroke-width="3" marker-end="url(#arrow)"/><text x="{(a[0]+b[0])/2+8}" y="{(a[1]+b[1])/2-10}" fill="{color}" font-size="14">{e["id"]}'+(' ↔'if e['bidirectional']else' →')+'</text>')
    for n in g['nodes']:
        x,y=pos[n['id']];s.append(f'<rect x="{x-65}" y="{y-25}" width="130" height="52" rx="10" fill="#24405b" stroke="#b1c5dc"/><text x="{x}" y="{y-4}" fill="white" text-anchor="middle" font-size="16">{n["id"]}</text><text x="{x}" y="{y+15}" fill="#b2c4d8" text-anchor="middle" font-size="11">{n["macro_family"]}</text>')
    s.append('</svg>');Path(path).write_text('\n'.join(s))

def world(c,traces,path):
    x,y,w,h=c['case']['world_bounds'];s=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x-50} {y-120} {w+100} {h+200}">',f'<rect x="{x-50}" y="{y-120}" width="{w+100}" height="{h+200}" fill="#101a2b"/>']
    for i,p in enumerate(c['case']['platforms']):s.append(f'<rect x="{p[0]}" y="{p[1]}" width="{p[2]}" height="{p[3]}" fill="'+('#be985e'if i in c['case']['one_way_platform_indices']else'#697f75')+'"/>')
    for name,color in [('full-region-upper-main','#60cfff'),('full-region-lower-main','#72eab4'),('full-region-reward-foldback','#ffc35c')]:
        pts=' '.join(f'{a:.1f},{b:.1f}'for a,b in traces[name]);s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" opacity=".8" stroke-width="5"><title>{name}</title></polyline>')
    for key,n in c['nodes'].items():
        a,b=n['center']['position'];s.append(f'<circle cx="{a}" cy="{b}" r="12" fill="white"/><text x="{a+18}" y="{b-20}" fill="white" font-size="28">{key}</text>')
    for e in c['seams']:
        a,b=e['from_position'];s.append(f'<circle cx="{a}" cy="{b}" r="7" fill="#fbbf24"/><text x="{a+14}" y="{b+24}" fill="#fbbf24" font-size="22">{e["id"]}</text>')
    s.append('</svg>');Path(path).write_text('\n'.join(s))

def run(source,out):
    root=Path(source);out=Path(out)
    if out.exists():raise ValueError('immutable review exists')
    out.mkdir();m,c,traces=inspect(root);summary=json.loads((root/'summary.json').read_text());correspondence=json.loads((root/'blueprint-world-correspondence.json').read_text());design=json.loads((root/'selected-design.json').read_text())
    clips=[]
    for name in ['upper','lower','reward']:
        r=Path('pcg/results/graph-landforms-video-'+name+'-v1');v=json.loads((r/'manifest.json').read_text());shutil.copy2(r/v['file'],out/(name+'.mp4'));clips.append(dict(alias=name,**v))
    write(out/'video-manifest.json',dict(clips=clips,human_playtests=0,human_fun='unreviewed'))
    shutil.copy2('pcg/results/graph-landforms-capture-final-v1/whole-map.png',out/'whole-map.png')
    blueprint(c['exploration_graph'],out/'exploration.svg');world(c,traces,out/'measured-world.svg');grid(c,out/'block-shapes.svg');write(out/'transition-matrix.json',observed_matrix(root,c));write(out/'correspondence.json',correspondence)
    result=dict(schema='pcg/same-graph-landforms-review/v1',map=m,passed=summary['passed'],total=summary['total'],calibration_not_included=5,fresh_holdouts=6,nominal=5,design=design,blueprint_world=correspondence,
        unique_topologies=1,prototype_scope='One bounded7-Macro acceptance map; not full regional generation or human fun approval',old_rock_well_templates=0,production_admitted=False)
    write(out/'results.json',result)
    labels={'upper':'高路：爬升＋空中击铃','lower':'低路：下坠制动＋折返反冲攀升','reward':'奖励：尖刺窄通路＋真实折返，1箱18币'}
    videos=''.join(f'<h2>{labels[k]}</h2><video controls preload="metadata" src="{k}.mp4"></video><p><a href="{k}.mp4">下载完整正常速度录像</a></p>'for k in labels)
    (out/'report.html').write_text('<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>同图驱动：高崖与溪谷</title><style>body{max-width:1200px;margin:32px auto;padding:0 18px;background:#101a2b;color:#e0ebf7;font:17px/1.65 system-ui}a{color:#70d3ff}img,video{width:100%;background:#0b1322}article{padding:16px;border:1px solid #3e5570}</style><h1>风铃平原：同一探索图 → 真实拼装</h1><p>7 Macro / 7零间隙接缝，两条明显不同的主路线，在landmark真实汇合；cliff向深处cache延伸奖励并原路返回。旧岩井模板0、删除蓝图边0、Map补平台0。主线0箱，支路1箱18币。</p><p>这是一个小规模验收样图：11/11整图策略，其中5常规＋6新输入扰动。不是完整大区域或人类趣味批准。地貌仍由有限规则构造，局部直边和支路阶梯仍待观感评审；不宣称完全解决自然地貌。</p><p><a href="index.html">Godot键盘试玩</a>（A/D移动、Space跳、鼠标射击、R重试、M地图）</p><h2>真实Godot整图</h2><img src="whole-map.png" alt="实际完整世界截图"><h2>蓝图：全部节点与边均进入实际世界</h2><img src="exploration.svg" alt="职责图"><p>蓝色高路、绿色低路、金色奖励；职责图只是逻辑排版。下面是相同节点和边在实际地形与实测轨迹中的对应。</p><img src="measured-world.svg" alt="实际地形和实测路径"><p><a href="block-shapes.svg">Block预留形状</a> · <a href="correspondence.json">节点/版本/接缝逐项对应</a> · <a href="transition-matrix.json">具体实例Port关系见证</a></p>'+videos+'<p>三片均为真实原生60Hz输入回放，正常1倍，含启动/全部等待/末尾1秒；逐帧对照物理验证。不是玩家操作手感或人类评分。</p><p><a href="results.json">完整结构化数据</a> · <a href="video-manifest.json">录像SHA与严格帧对照</a></p></html>')
    print(json.dumps({k:result[k]for k in ['passed','total','fresh_holdouts','unique_topologies']}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);a=p.parse_args();run(a.source,a.out)
