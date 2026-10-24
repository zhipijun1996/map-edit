"""Real canvas controls and all twenty input-witness replays; no state mutation."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright

def run(url,out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);records=[];events=[];errors=[]
 with sync_playwright() as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  page=b.new_page(viewport={'width':1280,'height':720});page.on('console',lambda m:events.append(dict(type=m.type,text=m.text)));page.on('pageerror',lambda e:errors.append(str(e)))
  def state():return page.evaluate('window.__pcgLabStateV2')
  def record(action):s=state();records.append(dict(action=action,state=s));return s
  def select(index):
   page.mouse.click(210,55);page.wait_for_timeout(100)
   page.mouse.click(210,90+26*index)
   page.wait_for_function('(i)=>window.__pcgLabStateV2.selected===i && window.__pcgLabStateV2.mode==="manual"',arg=index,timeout=10000)
   return record('select_'+str(index))
  def save():
   (out/'browser.json').write_text(json.dumps(dict(url=url,records=records,events=events,errors=errors),ensure_ascii=False,indent=2))
  try:
   page.goto(url,wait_until='networkidle',timeout=90000);page.wait_for_function('window.__pcgLabStateV2 && window.__pcgLabStateV2.case_count===20',timeout=90000)
   initial=record('loaded');page.screenshot(path=str(out/'initial.png'))
   page.keyboard.down('d');page.wait_for_timeout(140);page.keyboard.up('d');moved=record('manual_D');assert moved['position'][0]>initial['position'][0]+10
   page.keyboard.down('Space');page.wait_for_timeout(70);page.keyboard.up('Space');page.wait_for_timeout(90);jumped=record('manual_Space');assert jumped['events']['jump']>=1
   page.mouse.click(650,400);page.wait_for_timeout(70);assert record('disabled_shoot')['events']['shot']==0
   page.keyboard.press('r');page.wait_for_timeout(120);assert record('manual_R')['events']['jump']==0
   select(1);page.mouse.click(500,500);page.wait_for_timeout(80);assert record('manual_shoot')['events']['shot']>=1
   page.mouse.click(800,55);page.wait_for_timeout(100);assert record('mouse_retry')['events']['shot']==0
   for index in range(20):
    select(index);page.mouse.click(940,55);page.wait_for_function('window.__pcgLabStateV2.mode==="replay"',timeout=10000)
    page.wait_for_function('window.__pcgLabStateV2.finished',timeout=20000);s=record('replay_'+str(index))
    assert s['safe'] and s['stable_frames']>=6 and s['grounded'] and abs(s['velocity'][0])<=1 and abs(s['velocity'][1])<=1,s
    if index in (3,4,11,14,15):page.screenshot(path=str(out/f'replay-{index:02d}.png'))
   assert not errors,errors
   assert not [e for e in events if e['type']=='error'],events
   record('all_checks_passed');save();print(json.dumps(dict(checks='passed',replays=20,records=len(records),page_errors=errors)))
  except Exception as e:
   records.append(dict(action='failure',error=str(e),state=state()));save();page.screenshot(path=str(out/'failure.png'));raise
  finally:b.close()

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('out');args=p.parse_args();run(args.url,args.out)
