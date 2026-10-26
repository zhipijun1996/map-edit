"""Draw proposal diagrams, NOT world geometry, simulation or Module exports."""
import html,json,hashlib,unicodedata
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'pcg/creative-production/junction-ideas-v1.json'
OUT=ROOT/'generation/designs/junction-ideas-v1'
esc=lambda s:html.escape(str(s))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def wrap(value,width=46):
    rows=[];line='';n=0
    for ch in value:
        w=2 if unicodedata.east_asian_width(ch)in 'WF'else 1
        if n+w>width:rows.append(line);line='';n=0
        line+=ch;n+=w
    if line:rows.append(line)
    return rows

def render(card):
    d=card['concept'];ports=card['ports'];nodes={n['id']:n for n in ports+d['nodes']};n=len(ports)
    x=lambda v:48+v*4.25;y=lambda v:120+v*4.0
    pieces=['<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="670" viewBox="0 0 1040 670" role="img">',f'<title>{esc(card["id"]+" "+card["title"])}：未验证的空间构图与有向意图</title>',
      '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="5" markerHeight="5" orient="auto"><path d="M0,0 L10,5 L0,10" fill="#7ed2bf"/></marker><marker id="control" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="4" markerHeight="4" orient="auto"><path d="M0,0 L10,5 L0,10" fill="#ddb97a"/></marker><pattern id="hatch" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M-2,10 L10,-2 M8,12 L12,8" stroke="#526071" stroke-width="1"/></pattern></defs>',
      '<rect width="1040" height="670" rx="16" fill="#121b25"/><g font-family="Noto Sans CJK SC,Microsoft Yahei,system-ui,sans-serif">',
      f'<text x="32" y="44" font-size="27" fill="#f1eee4">{esc(card["id"]+" · "+card["title"])}</text>',
      f'<text x="32" y="76" font-size="14" fill="#aeb8c4">{n} 个地区接口 · 空间创意提案 · 所有物理证据 UNKNOWN</text>',
      '<rect x="24" y="94" width="500" height="454" rx="12" fill="#1b2935" stroke="#344a5c"/>',
      '<text x="42" y="116" font-size="12" fill="#aeb8c4">空间构图（概念比例；线是去向意图，不是跳跃轨迹）</text>']
    for mass in d['masses']:
        pts=' '.join(f'{x(p[0]):.1f},{y(p[1]):.1f}'for p in mass['points'])
        pieces.append(f'<polygon points="{pts}" fill="#3b4b59" stroke="#71818e" stroke-width="1.4" stroke-linejoin="round"/><polygon points="{pts}" fill="url(#hatch)" opacity=".5"/>')
    for motion in d.get('motion_paths',[]):
        if motion['shape']=='ellipse':pieces.append(f'<ellipse cx="{x(motion["cx"])}" cy="{y(motion["cy"])}" rx="{motion["rx"]*4.25}" ry="{motion["ry"]*4}" fill="none" stroke="#ddb97a" stroke-dasharray="7 5" stroke-width="2"/>')
    for e in d['routes']:
        a,b=nodes[e['from']],nodes[e['to']];path=f'M{x(a["x"])},{y(a["y"])} '
        if 'quadratic_control'in e:
            q=e['quadratic_control'];path+=f'Q{x(q[0])},{y(q[1])} {x(b["x"])},{y(b["y"])}'
        else:
            path+=' '.join(f'L{x(q[0])},{y(q[1])}'for q in e.get('via',[]))+f' L{x(b["x"])},{y(b["y"])}'
        pieces.append(f'<path d="{path}" fill="none" stroke="#7ed2bf" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round" opacity=".85" marker-end="url(#arrow)"/>')
    for e in d.get('control_links',[]):
        a,b=nodes[e['from']],nodes[e['to']]
        pieces.append(f'<path d="M{x(a["x"])},{y(a["y"])} Q{x(50)},{y(12)} {x(b["x"])},{y(b["y"])}" fill="none" stroke="#ddb97a" stroke-width="1.5" stroke-dasharray="4 4" marker-end="url(#control)"/>')
    for node in d['nodes']:
        px,py=x(node['x']),y(node['y']);kind=node['kind'];color='#ddb97a'if kind in ['decision','moving_cell','bell']else'#b8c3ce'
        if kind=='moving_cell':pieces.append(f'<rect x="{px-16}" y="{py-5}" width="32" height="10" rx="3" fill="{color}"/>')
        else:pieces.append(f'<circle cx="{px}" cy="{py}" r="5" fill="{color}"/>')
        label=wrap(node['label'],18)
        for i,line in enumerate(label):pieces.append(f'<text x="{px+9}" y="{py-9+i*16}" font-size="12" fill="{color}" paint-order="stroke" stroke="#1b2935" stroke-width="3">{esc(line)}</text>')
    for p in ports:
        px,py=x(p['x']),y(p['y']);color='#80cfc0'if p['id']=='A'else'#e3c58f'
        pieces.append(f'<circle cx="{px}" cy="{py}" r="12" fill="#182330" stroke="{color}" stroke-width="2"/><text x="{px}" y="{py+5}" text-anchor="middle" font-size="14" font-weight="bold" fill="{color}">{esc(p["id"])}</text>')
        tx=px+18 if p['x']<65 else px-18;anchor='start'if p['x']<65 else'end';ty=py-18 if p['y']>80 else py+29
        pieces.append(f'<text x="{tx}" y="{ty}" text-anchor="{anchor}" font-size="13" fill="{color}" paint-order="stroke" stroke="#1b2935" stroke-width="3">{esc(p["label"])}</text>')
    pieces+=['<text x="566" y="119" font-size="18" fill="#eee8d8">有向关系：设计意图</text>', '<text x="566" y="143" font-size="12" fill="#aeb8c4">行＝从哪里来；列＝去哪里。不是可达性结论。</text>']
    matrix={(e['from'],e['to']):e['design_intent']for e in card['directed_intent_matrix']};startx,starty,step=630,166,38
    for i,p in enumerate(ports):
        pieces.append(f'<text x="{startx+i*step+15}" y="{starty-5}" text-anchor="middle" font-size="14" fill="#dedace">{p["id"]}</text><text x="{startx-18}" y="{starty+i*step+23}" font-size="14" fill="#dedace">{p["id"]}</text>')
        for j,q in enumerate(ports):
            intent=matrix.get((p['id'],q['id']),'self');fill={'desired':'#254f4e','deliberately_undesired_reverse':'#5b3f40','not_requested':'#293541','self':'#17212b'}[intent];symbol={'desired':'→','deliberately_undesired_reverse':'×','not_requested':'?','self':'—'}[intent]
            pieces.append(f'<rect x="{startx+j*step}" y="{starty+i*step}" width="33" height="33" rx="4" fill="{fill}"/><text x="{startx+j*step+16}" y="{starty+i*step+23}" text-anchor="middle" font-size="17" fill="#d9e1df">{symbol}</text>')
    yy=starty+n*step+22
    pieces.append(f'<text x="566" y="{yy}" font-size="12" fill="#aeb8c4">→ 希望通行　× 希望限制反向　? 未请求</text>')
    yy+=38;pieces.append(f'<text x="566" y="{yy}" font-size="16" fill="#e3c58f">玩家选择</text>')
    for line in wrap(card['decision'])[:7]:yy+=23;pieces.append(f'<text x="566" y="{yy}" font-size="15" fill="#dae0e4">{esc(line)}</text>')
    status='需新增环绕轨迹 Cell / 生成规则'if card['cell_and_rule_gaps']['cells']else'原 Cell 可复用 / 生成规则与验证待做'
    pieces += [f'<text x="42" y="578" font-size="15" fill="#ddb97a">{esc(status)}</text>', '<text x="42" y="608" font-size="13" fill="#aeb8c4">拟定局部构图；所有来回方向、身体净空与资源条件尚未验证。</text>', '<text x="42" y="637" font-size="14" fill="#f1b997">提案 / NOT_RUN　·　不是可玩样品、不是生产批准</text>', '</g></svg>']
    return ''.join(pieces)

def main():
    data=json.loads(SOURCE.read_text());OUT.mkdir(parents=True,exist_ok=True);rows=[]
    for card in data['cards']:
        target=OUT/(card['id']+'.svg');target.write_text(render(card));rows.append(dict(id=card['id'],title=card['title'],diagram=target.name,sha256=sha(target),ports=len(card['ports']),physical_validation='NOT_RUN'))
    (OUT/'manifest.json').write_text(json.dumps(dict(schema='pcg/junction-concept-diagrams/v1',source=dict(path=str(SOURCE.relative_to(ROOT)),sha256=sha(SOURCE)),renderer=dict(path=str(Path(__file__).resolve().relative_to(ROOT)),sha256=sha(Path(__file__))),units='concept_only_not_world_units',cards=rows,new_modules=0,physics_cases=0),ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(concept_diagrams=len(rows),new_modules=0,physics_cases=0)))
if __name__=='__main__':main()
