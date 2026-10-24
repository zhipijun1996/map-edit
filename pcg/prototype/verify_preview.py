#!/usr/bin/env python3
"""Actual browser load and mouse replay of a staged/published immutable Godot export."""
from playwright.sync_api import sync_playwright
from pathlib import Path
import argparse,json
p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('--output',type=Path,required=True);p.add_argument('--all',action='store_true');args=p.parse_args()
args.output.mkdir(parents=True,exist_ok=True)
records=[];errors=[];console=[]
with sync_playwright() as pw:
 b=pw.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
 page=b.new_page(viewport={'width':1280,'height':720})
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('console',lambda m:console.append(m.text) if m.type=='error' else None)
 try:
  response=page.goto(args.url,wait_until='networkidle',timeout=90000)
  assert response.status==200
  page.wait_for_function('window.__pcgLabState && window.__pcgLabState.case_count===6',timeout=90000)
  for i in (range(6) if args.all else (0,)):
   page.mouse.click(210,55);page.wait_for_timeout(90);page.mouse.click(200,90+26*i)
   page.wait_for_function('(i)=>window.__pcgLabState.selected===i && window.__pcgLabState.mode==="manual"',arg=i,timeout=10000)
   page.mouse.click(690,55)
   page.wait_for_function('window.__pcgLabState.mode==="replay"',timeout=10000)
   page.wait_for_function('window.__pcgLabState.finished',timeout=20000)
   state=page.evaluate('window.__pcgLabState');records.append(state)
   assert state['safe'] and 'exit reached' in state['status'].lower(),state
   if i==4:assert state['reward_visited']
   page.screenshot(path=str(args.output/f'case-{i}.png'))
  assert not errors,errors
  assert not console,console
  status='passed'
 finally:
  (args.output/'browser.json').write_text(json.dumps(dict(url=args.url,records=records,page_errors=errors,console_errors=console,status=locals().get('status','failed')),indent=2))
  b.close()
print('BROWSER_PREVIEW_VERIFIED',len(records))
