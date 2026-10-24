"""Actual canvas menus, manual controls and all recorded V3 witnesses."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright

def run(url,out,count=17):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);records=[];events=[];errors=[]
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  page=browser.new_page(viewport={'width':1280,'height':720})
  page.on('console',lambda m:events.append(dict(type=m.type,text=m.text)))
  page.on('pageerror',lambda e:errors.append(str(e)))
  def state():return page.evaluate('window.__pcgLabStateV3')
  def record(action):
   s=state();records.append(dict(action=action,state=s));return s
  def save():
   (out/'browser.json').write_text(json.dumps(dict(url=url,records=records,events=events,errors=errors),ensure_ascii=False,indent=2))
  def select(index):
   page.mouse.click(220,55);page.wait_for_timeout(100)
   page.mouse.click(220,90+26*index)
   page.wait_for_function('(i)=>window.__pcgLabStateV3.selected===i && window.__pcgLabStateV3.mode==="manual"',arg=index,timeout=10000)
  try:
   page.goto(url,wait_until='networkidle',timeout=90000)
   page.wait_for_function('(n)=>window.__pcgLabStateV3 && window.__pcgLabStateV3.case_count===n',arg=count,timeout=90000)
   initial=record('loaded');page.screenshot(path=str(out/'initial.png'))
   page.keyboard.down('d');page.wait_for_timeout(120);page.keyboard.up('d')
   moved=record('manual_D');assert moved['position'][0]>initial['position'][0]+5,moved
   page.keyboard.down('Space');page.wait_for_timeout(60);page.keyboard.up('Space');page.wait_for_timeout(70)
   assert record('manual_jump')['events']['jump']>=1
   page.keyboard.press('r');page.wait_for_timeout(160);assert record('manual_R')['events']['jump']==0
   for index in range(count):
    select(index)
    page.mouse.click(960,55)
    page.wait_for_function('window.__pcgLabStateV3.mode==="replay"',timeout=10000)
    page.wait_for_function('window.__pcgLabStateV3.finished',timeout=25000)
    s=record('replay_'+str(index))
    assert s['safe'] and s['stable_frames']>=6 and s['hp']==5 and not s['damage_commits'] and not s['returns'],s
    if index in (0,3,6,12,14):page.screenshot(path=str(out/f'replay-{index:02d}.png'))
   assert not errors,errors
   engine_errors=[e for e in events if e['type']=='error' or 'SCRIPT ERROR' in e['text'] or e['text'].startswith('ERROR:')]
   assert not engine_errors,engine_errors
   record('all_checks_passed');save();print(json.dumps(dict(checks='passed',replays=count,records=len(records))))
  except Exception as e:
   records.append(dict(action='failure',error=str(e),state=state()));save();page.screenshot(path=str(out/'failure.png'));raise
  finally:browser.close()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('out');p.add_argument('--count',type=int,default=17);a=p.parse_args();run(a.url,a.out,a.count)
