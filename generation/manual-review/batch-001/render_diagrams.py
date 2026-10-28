from pathlib import Path
import json,hashlib,html,datetime,math,argparse,textwrap
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[3];out=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--manifest',type=Path);parser.add_argument('--out',type=Path);parser.add_argument('--draft',action='store_true');args=parser.parse_args()
manifest=json.loads((args.manifest or out/'batch.json').read_text())
if args.out:out=args.out;out.mkdir(parents=True,exist_ok=True)
catalog=[{'file':r['source'],'id':r['moduleId']} for r in manifest['rows']]
notes=[(r['title'],r['summary']) for r in manifest['rows']]
for row in manifest['rows']:
 assert hashlib.sha256((ROOT/row['source']).read_bytes()).hexdigest()==row['sourceSha256'], 'source changed; create a new review version'
esc=lambda s:html.escape(str(s),quote=True)
rows=[]
for n,(entry,(title,note)) in enumerate(zip(catalog,notes),1):
 src=ROOT/entry['file'];doc=json.loads(src.read_text());design_only=doc.get('schema')=='pcg/module-design/v1'
 if design_only:
  design=doc;doc={'id':design['id'],'objects':design['visualObjects']};gc={'contentVersion':design['designVersion'],'space':{'bounds':design['bounds']},'foundation':{'widthBlocks':design['bounds']['w']//128,'heightBlocks':design['bounds']['h']//128},'routes':design['intendedRoutes'],'ports':design['ports'],'generation':{'portConnectivityIntent':design.get('connectivityIntent')}}
 else:gc=doc['generationContract']
 matrix=design.get('routeMatrix') if design_only else None
 review_meta=manifest['rows'][n-1];instructions=review_meta.get('instructions',[])
 b=gc['space']['bounds'];s=min(1250/b['w'],(1200 if design_only and b['h']>b['w']*1.6 else 700)/b['h']);W=1440;L=(W-b['w']*s)/2;T=130;H=round(T+b['h']*s+175+(210 if matrix else 0))+(len(instructions)*32+20 if instructions else 0)
 X=lambda x:L+(x-b['x'])*s;Y=lambda y:T+(y-b['y'])*s
 parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto-start-reverse"><path d="M0 0 L7 3.5 L0 7Z" fill="context-stroke"/></marker></defs><style>text{{font-family:"Noto Sans CJK SC",sans-serif;fill:#263c37}} .label{{paint-order:stroke;stroke:#fbfaf5;stroke-width:5;stroke-linejoin:round}}</style><rect width="100%" height="100%" fill="#fbfaf5"/>']
 def text(x,y,t,size=21,fill='#263c37',anchor='start',weight=400):parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" class="label">{esc(t)}</text>')
 review_id=review_meta['reviewId']
 text(38,45,f'{review_id}  {title}',32,weight=700);text(38,84,note,20)
 for ix in range(gc['foundation']['widthBlocks']+1):
  x=X(b['x']+128*ix);parts.append(f'<path d="M{x} {T}V{Y(b["y"]+b["h"])}" stroke="#d8e2d6" stroke-width="1"/>')
 for iy in range(gc['foundation']['heightBlocks']+1):
  y=Y(b['y']+128*iy);parts.append(f'<path d="M{L} {y}H{X(b["x"]+b["w"])}" stroke="#d8e2d6" stroke-width="1"/>')
 parts.append(f'<rect x="{L}" y="{T}" width="{b["w"]*s}" height="{b["h"]*s}" fill="none" stroke="#79999e" stroke-dasharray="8 6" stroke-width="2"/>')
 gates={};bells={};reward=[];hooks={};reference_action=review_meta.get('actionDiagram') or review_meta.get('hookActionDiagram')
 for o in doc['objects']:
  typ=o['type']
  if typ in ('route','entry','exit','anchor','note'):continue
  x,y,w,h=X(o['x']),Y(o['y']),o['w']*s,o['h']*s
  if typ in ('terrain','platform'):
   parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{'#c8d5b8'if typ=='platform'else'#a4b490'}" stroke="#697e60" stroke-width="1.5"/>')
   if typ=='platform':text(x+w/2,y+h+22 if o.get('diagramLabelBelow') else y-10,o.get('label','可穿平台'),18,anchor='middle')
  elif typ=='gate':
   if (o.get('mechanics')or{}).get('collision')=='disabled_by_original_bind_motion':continue
   label='G'+str(len(gates)+1);gates[o['id']]=label;m=o.get('mechanics')or{};opened=m.get('kind')=='complementary_gates' and m.get('member')==m.get('initialOpen')
   parts.append(f'<rect x="{x}" y="{y}" width="{max(w,5)}" height="{max(h,5)}" fill="#9865bc" fill-opacity="{.13 if opened else .85}" stroke="#8056a2" stroke-width="2" '+('stroke-dasharray="6 4"'if opened else'')+'/>');text(X(o['diagramLabelPosition'][0]) if o.get('diagramLabelPosition') else x+w/2,Y(o['diagramLabelPosition'][1]) if o.get('diagramLabelPosition') else y-10,o.get('diagramLabel',label+(' 初始开'if opened else' 初始关')),18,anchor='middle')
   if o.get('diagramHint'):text(x+w/2,y+h+26,o['diagramHint'],18,anchor='middle')
  elif typ=='switch':
   parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#e4bf5f" fill-opacity=".45" stroke="#9d7a29" stroke-width="2" stroke-dasharray="4 3"/>');lp=review_meta.get('labelPositions',{}).get(o['id']);text(X(lp[0]) if lp else x+w/2,Y(lp[1]) if lp else y-10,review_meta.get('objectLabels',{}).get(o['id'],'实体检测区'),18,anchor='middle')
   target=next((v for v in doc['objects']if v['id']==o.get('targetId')),None)
   if target:parts.append(f'<path d="M{x+w/2} {y+h/2}L{X(target["x"]+target["w"]/2)} {Y(target["y"]+target["h"]/2)}" stroke="#ad8a35" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#arrow)"/>')
   enemy_id=(o.get('mechanics')or{}).get('enemyObjectId');enemy=next((v for v in doc['objects']if v['id']==enemy_id),None)
   if enemy:parts.append(f'<path d="M{X(enemy["x"]+enemy["w"]/2)} {Y(enemy["y"]+enemy["h"]/2)}L{x+w/2} {y+h/2}" stroke="#ad8a35" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#arrow)"/>')
  elif typ=='enemy':
   cx,cy=x+w/2,y+h/2;parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#dc714d" stroke="#8e432e" stroke-width="2"/>');text(cx,cy-23,'空中怪'if o.get('definition')=='plains_diver'else'陆上怪',20,anchor='middle')
  elif typ in ('hookBounce','hookHang'):
   cx,cy=x+w/2,y+h/2;radius=max(9,12*s);label='H'+str(len(hooks)+1);hooks[o['id']]=label
   parts.append(f'<circle data-hook-id="{esc(o["id"])}" cx="{cx}" cy="{cy}" r="{radius}" fill="#e2effb" stroke="#3b79c9" stroke-width="3"/><circle cx="{cx}" cy="{cy}" r="{radius*.55}" fill="none" stroke="#bf9436" stroke-width="2"/>');text(cx,cy-radius-8,label+' · '+o.get('sourceId','')+(' 弹起'if typ=='hookBounce'else' 悬挂'),18,anchor='middle')
  elif typ=='hazard' and o.get('shape')=='zone':
   parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#c75049" fill-opacity=".3" stroke="#903931" stroke-width="2"/>');text(x+w/2,y-9,o.get('label','危险区'),18,anchor='middle')
  elif typ=='hazard':
   vertical=o.get('orientation') in ('LEFT','RIGHT');count=max(2,round(h/(w*1.3)))if vertical else max(2,round(w/(h*1.3)));count=max(1,int(o.get('count',count)));step=(h if vertical else w)/count
   for j in range(count):
    if vertical:
     pts=(f'{x+w},{y+j*step} {x},{y+(j+.5)*step} {x+w},{y+(j+1)*step}' if o.get('orientation')=='LEFT' else f'{x},{y+j*step} {x+w},{y+(j+.5)*step} {x},{y+(j+1)*step}')
     parts.append(f'<polygon points="{pts}" fill="#c75049" stroke="#903931" stroke-width="1.5"/>')
    elif o.get('shape')=='gears':
     cx,cy=x+(j+.5)*step,y+h/2;radius=min(h/2,step*.46)
     pts=' '.join(f'{cx+math.cos(a*math.pi/12)*(radius if a%2==0 else radius*.67)},{cy+math.sin(a*math.pi/12)*(radius if a%2==0 else radius*.67)}'for a in range(24))
     parts.append(f'<polygon points="{pts}" fill="#d65345" stroke="#923e36" stroke-width="1.5"/><circle cx="{cx}" cy="{cy}" r="{radius*.25}" fill="#fbfaf5"/>')
    elif o.get('orientation')=='DOWN':
     pts=f'{x+j*step},{y} {x+(j+.5)*step},{y+h} {x+(j+1)*step},{y}'
     parts.append(f'<polygon points="{pts}" fill="#c75049" stroke="#903931" stroke-width="1.5"/>')
    else:
     pts=f'{x+j*step},{y+h} {x+(j+.5)*step},{y} {x+(j+1)*step},{y+h}'
     parts.append(f'<polygon points="{pts}" fill="#c75049" stroke="#903931" stroke-width="1.5"/>')
   text(x if vertical else x+w/2,y-9,o.get('label','危险带'),18,anchor='start'if vertical else'middle')
  elif typ=='trackLine':
   pts=' '.join(f'{X(p["x"])},{Y(p["y"])}' for p in o.get('points',[]))
   parts.append(f'<polyline points="{pts}" fill="none" stroke="#667e91" stroke-width="2" stroke-dasharray="7 5" marker-end="url(#arrow)"/>')
  elif typ=='bell':bells[o['id']]='铃'+str(len(bells)+1)
  elif typ=='reward':reward.append(o)
 for o in doc['objects']:
  if o.get('wallClimbable'):
   parts.append(f'<path d="M{X(o["x"])} {Y(o["y"])}V{Y(o["y"]+o["h"])}" stroke="#3b79c9" stroke-width="4" stroke-dasharray="5 4"/>');text(X(o['x'])+16,Y(o['y'])+28,'可蹬墙',18)
 for ghost in review_meta.get('ghosts',[]):
  x,y,w,h=X(ghost['x']),Y(ghost['y']),ghost['w']*s,ghost['h']*s;parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#dbecf6" fill-opacity=".5" stroke="#3b79c9" stroke-width="2" stroke-dasharray="5 4"/>');text(x+w/2,y-12,ghost['label'],18,anchor='middle')
 # Actual archived core-route paths, without per-frame numbering.
 routecolors=['#157f84','#d28b25','#3c69b0','#a35b92']
 for i,r in enumerate(gc['routes']):
  o=next(v for v in doc['objects']if v['id']==r['pathObjectId'])
  if o.get('reviewShowTrace') is False:continue
  points=o.get('points',[]);stride=max(1,len(points)//80);points=points[::stride]+points[-1:]
  points=' '.join(f'{X(p["x"])},{Y(p["y"])}'for p in points);color=routecolors[i%len(routecolors)]
  start_marker=' marker-start="url(#arrow)"' if o.get('reviewBidirectional') else ''
  parts.append(f'<polyline{start_marker} points="{points}" stroke="{color}" stroke-opacity=".85" stroke-width="3.5" fill="none" marker-end="url(#arrow)"/>')
 if design_only:
  for shot in design.get('shotGuides',[]):
   ax,ay=shot['from'];bx,by=shot['to'];cx,cy=X(ax),Y(ay)
   parts.append(f'<circle cx="{cx}" cy="{cy}" r="7" fill="#3b79c9"/><path d="M{cx} {cy}L{X(bx)} {Y(by)}" fill="none" stroke="#3b79c9" stroke-width="3" stroke-dasharray="6 4" marker-end="url(#arrow)"/>')
   lx,ly=shot.get('labelPosition',[ax,ay-20]);text(X(lx),Y(ly),shot['label'],18,anchor=shot.get('labelAnchor','middle'))
   if shot.get('recoil'):
    a,z=shot['recoil'];parts.append(f'<path d="M{X(a[0])} {Y(a[1])}L{X(z[0])} {Y(z[1])}" fill="none" stroke="#30905c" stroke-width="4" marker-end="url(#arrow)"/>')
 if reference_action:
  points=' '.join(f'{X(p["x"])},{Y(p["y"])}'for p in reference_action['points'])
  parts.append(f'<polyline data-source-action-order="true" points="{points}" stroke="#3b79c9" stroke-width="2.5" stroke-dasharray="7 6" fill="none" marker-end="url(#arrow)"/>')
 for o in doc['objects']:
  if o['type']=='bell':
   for target in o.get('targetIds',[o.get('targetId')]):
    gate=next((g for g in doc['objects'] if g['id']==target and g['type'] in ('gate','hazard','platform')),None)
    if gate:
     target_y=o['y']+o['h']/2 if gate['type']=='gate' else gate['y']+gate['h']/2
     parts.append(f'<path d="M{X(o["x"]+o["w"]/2)} {Y(o["y"]+o["h"]/2)}L{X(gate["x"]+gate["w"]/2)} {Y(target_y)}" stroke="#ad8a35" stroke-width="1.5" stroke-dasharray="4 5"/>')
   cx,cy=X(o['x']+o['w']/2),Y(o['y']+o['h']/2);parts.append(f'<circle cx="{cx}" cy="{cy}" r="11" fill="#dfbc51" stroke="#9d7a29" stroke-width="2"/>');text(cx,cy-18,o.get('diagramLabel',bells[o['id']]),19,anchor='middle')
 for o in reward:
  cx,cy=X(o['x']+o['w']/2),Y(o['y']+o['h']/2);amount=(o.get('mechanics')or{}).get('amount','');parts.append(f'<rect x="{cx-13}" y="{cy-11}" width="26" height="22" rx="3" fill="#ecc65b" stroke="#956b25" stroke-width="2"/>');text(cx,cy-21,f'宝箱 {amount}',19,anchor='middle')
 for p in gc['ports']:
  if design_only and p.get('face')=='TOP' and p.get('permission')=='INOUT' and p.get('surface')=='ONE_WAY_PLATFORM':
   cx,cy=X(p['position'][0]),Y(p['position'][1]);parts.append(f'<circle cx="{cx}" cy="{cy}" r="11" fill="white" stroke="#256776" stroke-width="3"/><path d="M{cx} {cy-29}V{cy+29}" stroke="#256776" stroke-width="3" marker-start="url(#arrow)" marker-end="url(#arrow)"/>');text(cx+18,cy-18,p['id']+' 可穿·双向',22,weight=700)
   continue
  if design_only and p.get('permission')=='OUT' and p.get('surface')=='AIR':
   cx,cy=X(p['position'][0]),Y(p['position'][1]);nx,ny=p['normal'];parts.append(f'<circle cx="{cx}" cy="{cy}" r="11" fill="white" stroke="#256776" stroke-width="3"/><path d="M{cx-nx*30} {cy-ny*30}L{cx+nx*20} {cy+ny*20}" stroke="#256776" stroke-width="3" marker-end="url(#arrow)"/>');text(cx+24,cy+5,p['id']+' 空中仅出',22,weight=700)
   continue
  if design_only and p.get('permission')=='IN':
   cx,cy=X(p['position'][0]),Y(p['position'][1]);nx,ny=p['normal'];parts.append(f'<circle cx="{cx}" cy="{cy}" r="11" fill="white" stroke="#256776" stroke-width="3"/><path d="M{cx+nx*43} {cy+ny*43}L{cx-nx*25} {cy-ny*25}" stroke="#256776" stroke-width="3" marker-end="url(#arrow)"/>');text(cx+18 if cx<260 else cx-18,cy-18,p['id']+' 空中仅入',22,anchor='start'if cx<260 else'end',weight=700)
   continue
  cx,cy=X(p['position'][0]),Y(p['position'][1]);nx,ny=p['normal'];parts.append(f'<circle cx="{cx}" cy="{cy}" r="11" fill="white" stroke="#256776" stroke-width="3"/><path d="M{cx+nx*13} {cy+ny*13}L{cx+nx*43} {cy+ny*43}" stroke="#256776" stroke-width="3" marker-end="url(#arrow)"/>')
  if len(p['id'])>2:text(cx+nx*18,cy-20,p['id'],22,anchor='end'if nx<0 else'start',weight=700)
  else:text(cx+nx*63,cy+8+ny*50,p['id'],28,anchor='middle',weight=700)
 y=Y(b['y']+b['h'])+38;caption=reference_action['caption'] if reference_action else design['routeCaption'] if design_only and design.get('routeCaption') else((f'设计目标：{len(gc["ports"])}口两两互通，共 {len(gc["ports"])*(len(gc["ports"])-1)} 个有向关系；不是通行认证。'if design_only else'目标：A/B/C/D 四口两两可达，共 12 个方向；未验证方向保持 UNKNOWN。')if gc['generation'].get('portConnectivityIntent')=='all_distinct_ordered_pairs'else('声明方向：'if args.draft else'归档路线：')+'　 /　'.join(r['from']+' → '+r['to'] for r in gc['routes']));text(40,y,caption,22,weight=600)
 if matrix:
  order=matrix['portOrder'];cells={(c['from'],c['to']):c['status']for c in matrix['cells']};left=400;top=y+19;cw=100;rh=29
  for row in range(len(order)+1):
   for col in range(len(order)+1):
    status=cells.get((order[row-1],order[col-1]))if row and col else None
    label=('起点→终点'if row==0 and col==0 else order[col-1]if row==0 else order[row-1]if col==0 else{'DESIGN_TARGET':'目标','FORBIDDEN_EGRESS':'禁止','NOT_REQUESTED_SELF_LOOP':'—'}[status])
    fill='#e3eee1'if status=='DESIGN_TARGET'else'#f4dddd'if status=='FORBIDDEN_EGRESS'else'#f1f0e9'
    parts.append(f'<rect x="{left+col*cw}" y="{top+row*rh}" width="{cw}" height="{rh}" fill="{fill}" stroke="#c7d0c4"/>');text(left+(col+.5)*cw,top+row*rh+21,label,17,anchor='middle')
  y+=210
 legend='图例：绿＝地貌　紫＝门（虚线＝开）　金＝风铃/奖励　红＝齿轮/荆棘　曲线＝路线意图'if any(o['type']=='hazard'for o in doc['objects'])else'图例：绿＝岩体　紫＝门 / 可切换桥（虚线＝初始无碰撞）　金＝风铃 / 宝箱　橙＝怪物'
 if hooks:legend='图例：蓝环＝原钩点　虚蓝线＝来源动作顺序示意　绿＝岩体/平台　曲线不代表真实轨迹' if reference_action else '图例：蓝环＝弹起钩点　绿＝岩体/落地台　曲线＝设计动作顺序，非真实轨迹'
 if design_only and design.get('shotGuides'):legend='图例：蓝虚线＝射击意图　绿箭头＝反冲　金虚线＝机关关联　紫＝门　红＝荆棘'
 if instructions:legend='图例：金框＝状态检测（非风铃）　蓝虚线＝动作/载台时刻示意　紫＝门　绿＝地貌'
 if instructions:
  for j,line in enumerate(instructions):text(40,y+35+j*32,line,20)
  y+=len(instructions)*32+20
 text(40,y+38,legend,20)
 text(40,y+72,('设计稿：每格 128 px；曲线仅表达玩法意图，不代表实际动作、可达性或技术认证。'if args.draft else'每格 128 px；虚线外框是占地，不是墙。路线为归档动作轨迹，不代表全条件通行认证。'),18)
 text(40,y+106,f'{gc["foundation"]["widthBlocks"]}×{gc["foundation"]["heightBlocks"]} Block · {entry["id"]} · 设计讨论',16)
 parts.append('</svg>');svg=out/f'{review_id}.svg';svg.write_text(''.join(parts))
 rows.append(dict(reviewId=review_id,title=title,summary=note,moduleId=entry['id'],source=entry['file'],sourceSha256=hashlib.sha256(src.read_bytes()).hexdigest(),contentVersion=gc['contentVersion'],diagram=f'{review_id}.png',svg=svg.name,decision='PENDING',humanFeedback=[]))
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for row in rows:
  page=browser.new_page(viewport={'width':1440,'height':1200},device_scale_factor=1);page.set_content((out/row['svg']).read_text());page.locator('svg').screenshot(path=str(out/row['diagram']));page.close()
 browser.close()
