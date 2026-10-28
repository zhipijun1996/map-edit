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
 src=ROOT/entry['file'];doc=json.loads(src.read_text());gc=doc['generationContract'];b=gc['space']['bounds'];s=min(1250/b['w'],700/b['h']);W=1440;L=(W-b['w']*s)/2;T=130;H=round(T+b['h']*s+175)
 X=lambda x:L+(x-b['x'])*s;Y=lambda y:T+(y-b['y'])*s
 parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs><marker id="arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0 0 L7 3.5 L0 7Z" fill="context-stroke"/></marker></defs><style>text{{font-family:"Noto Sans CJK SC",sans-serif;fill:#263c37}} .label{{paint-order:stroke;stroke:#fbfaf5;stroke-width:5;stroke-linejoin:round}}</style><rect width="100%" height="100%" fill="#fbfaf5"/>']
 def text(x,y,t,size=21,fill='#263c37',anchor='start',weight=400):parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" class="label">{esc(t)}</text>')
 text(38,45,f'{n:02d}  {title}',32,weight=700);text(38,84,note,20)
 for ix in range(gc['foundation']['widthBlocks']+1):
  x=X(b['x']+128*ix);parts.append(f'<path d="M{x} {T}V{Y(b["y"]+b["h"])}" stroke="#d8e2d6" stroke-width="1"/>')
 for iy in range(gc['foundation']['heightBlocks']+1):
  y=Y(b['y']+128*iy);parts.append(f'<path d="M{L} {y}H{X(b["x"]+b["w"])}" stroke="#d8e2d6" stroke-width="1"/>')
 parts.append(f'<rect x="{L}" y="{T}" width="{b["w"]*s}" height="{b["h"]*s}" fill="none" stroke="#79999e" stroke-dasharray="8 6" stroke-width="2"/>')
 gates={};bells={};reward=[]
 for o in doc['objects']:
  typ=o['type']
  if typ in ('route','entry','exit','anchor','note'):continue
  x,y,w,h=X(o['x']),Y(o['y']),o['w']*s,o['h']*s
  if typ in ('terrain','platform'):
   parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#a4b490" stroke="#697e60" stroke-width="1.5"/>')
  elif typ=='gate':
   label='G'+str(len(gates)+1);gates[o['id']]=label;m=o.get('mechanics')or{};opened=m.get('kind')=='complementary_gates' and m.get('member')==m.get('initialOpen')
   parts.append(f'<rect x="{x}" y="{y}" width="{max(w,5)}" height="{max(h,5)}" fill="#9865bc" fill-opacity="{.13 if opened else .85}" stroke="#8056a2" stroke-width="2" '+('stroke-dasharray="6 4"'if opened else'')+'/>');text(x+w/2,y-10,label+(' 初始虚'if opened else' 初始实'),18,anchor='middle')
  elif typ=='enemy':
   cx,cy=x+w/2,y+h/2;parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="#dc714d" stroke="#8e432e" stroke-width="2"/>');text(cx,cy-23,'空中怪'if o.get('definition')=='plains_diver'else'陆上怪',20,anchor='middle')
  elif typ=='bell':bells[o['id']]='铃'+str(len(bells)+1)
  elif typ=='reward':reward.append(o)
 # Actual archived core-route paths, without per-frame numbering.
 routecolors=['#157f84','#d28b25','#3c69b0','#a35b92']
 for i,r in enumerate(gc['routes']):
  o=next(v for v in doc['objects']if v['id']==r['pathObjectId']);points=o.get('points',[]);stride=max(1,len(points)//80);points=points[::stride]+points[-1:]
  points=' '.join(f'{X(p["x"])},{Y(p["y"])}'for p in points);color=routecolors[i%len(routecolors)]
  parts.append(f'<polyline points="{points}" stroke="{color}" stroke-opacity=".85" stroke-width="3.5" fill="none" marker-end="url(#arrow)"/>')
 for o in doc['objects']:
  if o['type']=='bell':
   cx,cy=X(o['x']+o['w']/2),Y(o['y']+o['h']/2);parts.append(f'<circle cx="{cx}" cy="{cy}" r="11" fill="#dfbc51" stroke="#9d7a29" stroke-width="2"/>');text(cx,cy-18,bells[o['id']],19,anchor='middle')
 for o in reward:
  cx,cy=X(o['x']+o['w']/2),Y(o['y']+o['h']/2);amount=(o.get('mechanics')or{}).get('amount','');parts.append(f'<rect x="{cx-13}" y="{cy-11}" width="26" height="22" rx="3" fill="#ecc65b" stroke="#956b25" stroke-width="2"/>');text(cx,cy-21,f'宝箱 {amount}',19,anchor='middle')
 for p in gc['ports']:
  cx,cy=X(p['position'][0]),Y(p['position'][1]);nx,ny=p['normal'];parts.append(f'<circle cx="{cx}" cy="{cy}" r="11" fill="white" stroke="#256776" stroke-width="3"/><path d="M{cx+nx*13} {cy+ny*13}L{cx+nx*43} {cy+ny*43}" stroke="#256776" stroke-width="3" marker-end="url(#arrow)"/>');text(cx+nx*63,cy+8+ny*50,p['id'],28,anchor='middle',weight=700)
 y=Y(b['y']+b['h'])+38;text(40,y,('声明方向：'if args.draft else'归档路线：')+'　 /　'.join(r['from']+' → '+r['to'] for r in gc['routes']),22,weight=600)
 text(40,y+38,'图例：绿＝岩体　紫＝门 / 可切换桥（虚线＝初始无碰撞）　金＝风铃 / 宝箱　橙＝怪物',20)
 text(40,y+72,('每格 128 px；虚线外框不是墙。曲线是新版诊断轨迹，通过状态见网页；本轮仍待复审。'if args.draft else'每格 128 px；虚线外框是占地，不是墙。路线为归档动作轨迹，不代表全条件通行认证。'),18)
 text(40,y+106,f'{gc["foundation"]["widthBlocks"]}×{gc["foundation"]["heightBlocks"]} Block · {entry["id"]} · 待人工审批',16)
 parts.append('</svg>');svg=out/f'{n:02d}.svg';svg.write_text(''.join(parts))
 rows.append(dict(reviewId=f'{n:02d}',title=title,summary=note,moduleId=entry['id'],source=entry['file'],sourceSha256=hashlib.sha256(src.read_bytes()).hexdigest(),contentVersion=gc['contentVersion'],diagram=f'{n:02d}.png',svg=svg.name,decision='PENDING',humanFeedback=[]))
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 for row in rows:
  page=browser.new_page(viewport={'width':1440,'height':1200},device_scale_factor=1);page.set_content((out/row['svg']).read_text());page.locator('svg').screenshot(path=str(out/row['diagram']));page.close()
 browser.close()
