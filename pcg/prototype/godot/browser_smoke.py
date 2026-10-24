from playwright.sync_api import sync_playwright
from pathlib import Path
import json,time
root=Path(__file__).parent
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':1280,'height':720});events=[];errors=[]
 page.on('console',lambda m:events.append({'type':m.type,'text':m.text}));page.on('pageerror',lambda e:errors.append(str(e)))
 t=time.perf_counter();page.goto('http://127.0.0.1:8027',wait_until='networkidle',timeout=90000);page.wait_for_timeout(10000)
 page.screenshot(path=str(root/'browser-smoke.png'))
 (root/'browser-smoke.json').write_text(json.dumps({'elapsed_s':time.perf_counter()-t,'events':events,'errors':errors},indent=2))
 print(json.dumps({'events':events[-10:],'errors':errors},indent=2));b.close()
