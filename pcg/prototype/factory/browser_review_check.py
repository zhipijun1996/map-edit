"""Real Godot play, synthetic-only form testing, export and backend isolation."""
import argparse,json
from pathlib import Path
from playwright.sync_api import sync_playwright
from .core.feedback import validate,ingest,repair_job,FeedbackError

def run(url,out,count=4):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);records=[];events=[];errors=[]
 with sync_playwright()as p:
  browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  page=browser.new_page(viewport={'width':1360,'height':1100},accept_downloads=True)
  page.on('console',lambda m:events.append(dict(type=m.type,text=m.text)));page.on('pageerror',lambda e:errors.append(str(e)))
  def frame():return next(f for f in page.frames if '/play/'in f.url)
  def state():return frame().evaluate('window.__pcgLabStateV3')
  def click(x,y):
   page.locator('#game').scroll_into_view_if_needed();b=page.locator('#game').bounding_box();page.mouse.click(b['x']+x*b['width']/1280,b['y']+y*b['height']/720)
  def record(action):records.append(dict(action=action,state=state()))
  def save():
   (out/'browser.json').write_text(json.dumps(dict(url=url,records=records,events=events,errors=errors,feedback_actor='synthetic_test',real_human_reviews=0),ensure_ascii=False,indent=2))
  def replay(index):
   click(220,55);page.wait_for_timeout(100);click(220,90+26*index)
   frame().wait_for_function('(i)=>window.__pcgLabStateV3.selected===i && window.__pcgLabStateV3.mode==="manual"',arg=index,timeout=10000)
   click(960,55);frame().wait_for_function('window.__pcgLabStateV3.mode==="replay"',timeout=10000)
   frame().wait_for_function('window.__pcgLabStateV3.finished',timeout=25000)
   s=state();assert s['safe']and s['stable_frames']>=6 and s['hp']==5,s
   record('replay_'+str(index))
  try:
   target=url+('&'if'?'in url else'?')+'test_mode=1'
   page.goto(target,wait_until='networkidle',timeout=90000)
   page.wait_for_function('document.querySelector("#summary").textContent.includes("本轮")',timeout=30000)
   frame().wait_for_function('(n)=>window.__pcgLabStateV3 && window.__pcgLabStateV3.case_count===n',arg=count,timeout=90000)
   assert page.locator('#save').is_disabled();record('loaded_no_rating_without_play')
   replay(0);assert page.locator('#save').is_disabled();record('replay_is_not_manual_play')
   click(400,400);page.keyboard.press('r');page.wait_for_timeout(150)
   page.keyboard.down('d');page.wait_for_timeout(800);page.keyboard.up('d');page.wait_for_timeout(300)
   page.wait_for_function('!document.querySelector("#save").disabled',timeout=10000);record('real_manual_D_attempt')
   page.locator('#reviewer').fill('browser_test')
   for name in ('fun','clarity','fairness','replay_value','difficulty'):page.locator(f'input[name="{name}"][value="3"]').locator('..').click()
   page.locator('input[name="flag"][value="unreadable_landing"]').check();page.locator('textarea[name="notes"]').fill('自动化界面测试，不是真人反馈。')
   page.locator('#confirmation').check();page.locator('#save').click();page.wait_for_timeout(100)
   assert 'browser_test'in page.locator('#saved').inner_text()
   with page.expect_download()as download:page.locator('#export').click()
   export=out/'synthetic-feedback.json';download.value.save_as(export)
   raw=json.loads(export.read_text());assert len(raw['submissions'])==1
   # Use the actual browser network path. Playwright's separate Node request
   # client may choose unreachable IPv6 in this environment while Chromium's
   # same-origin page fetch works and is the path used by the product.
   # Keep the original JSON text: a JS-object round trip changes e.g. 1.0 to
   # integer 1, which would invalidate the Python canonical catalog digest.
   data=json.loads(page.evaluate('async()=>await (await fetch(new URL("catalog.json",location.href))).text()'));submission=raw['submissions'][0]
   assert submission['source_kind']=='synthetic_test'
   try:validate(submission,data)
   except FeedbackError as e:assert str(e)=='synthetic_feedback_cannot_enter_real_store'
   else:raise AssertionError('Synthetic browser test accepted as real human')
   store=ingest(out/'synthetic-only-store.json',[submission],data,test_mode=True)
   try:repair_job(store,data)
   except FeedbackError:pass
   else:raise AssertionError('Synthetic store created a real repair job')
   records.append(dict(action='synthetic_export_and_import_isolation_passed',submissions=1,real_human_reviews=0))
   page.screenshot(path=str(out/'feedback.png'),full_page=True)
   page.reload(wait_until='networkidle');page.wait_for_function('document.querySelector("#saved").textContent.includes("browser_test")',timeout=30000)
   frame().wait_for_function('window.__pcgLabStateV3',timeout=90000);record('reload_preserves_test_only_draft')
   for index in range(count):
    replay(index)
    if index in (0,count-1):page.screenshot(path=str(out/f'game-{index}.png'))
   assert not errors,errors
   bad=[e for e in events if e['type']=='error'or'SCRIPT ERROR'in e['text']or e['text'].startswith('ERROR:')]
   assert not bad,bad
   records.append(dict(action='all_checks_passed',replays=count+1,real_human_reviews=0));save();print(json.dumps(dict(passed=True,replays=count+1,real_human_reviews=0)))
  except Exception as e:
   records.append(dict(action='failure',error=str(e)));save();page.screenshot(path=str(out/'failure.png'),full_page=True);raise
  finally:browser.close()
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('out');p.add_argument('--count',type=int,default=4);a=p.parse_args();run(a.url,a.out,a.count)
