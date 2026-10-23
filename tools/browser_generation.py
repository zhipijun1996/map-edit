"""Actual MP4 decode/download check; this produces no human evaluation."""
import argparse,hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright
def run(url,out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);errors=[];records=[]
 with sync_playwright()as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1100,'height':900},accept_downloads=True);page.on('pageerror',lambda e:errors.append(str(e)));page.goto(url,wait_until='networkidle',timeout=90000)
  for i in range(2):
   v=page.locator('video').nth(i);v.evaluate('(v)=>v.play()');page.wait_for_timeout(1200);s=v.evaluate('(v)=>({time:v.currentTime,width:v.videoWidth,height:v.videoHeight,error:v.error?.message})');assert s['time']>.1 and s['width']==1280 and not s['error'];records.append(s);v.evaluate('(v)=>v.pause()')
  with page.expect_download()as d:page.get_by_text('下载合集 A（MP4）',exact=True).click()
  target=out/'download-A.mp4';d.value.save_as(str(target))
  manifest=json.loads(page.evaluate('async()=>await(await fetch(new URL("videos/factory05/manifest.json",location.href))).text()'))
  assert target.stat().st_size==manifest['combined']['bytes']and hashlib.sha256(target.read_bytes()).hexdigest()==manifest['combined']['sha256']
  page.screenshot(path=str(out/'page.png'),full_page=True);assert not errors
  receipt=dict(url=url,decoded=records,download_verified=True,errors=errors,human_video_feedback=0)
  (out/'browser.json').write_text(json.dumps(receipt,indent=2));b.close();print(json.dumps(receipt))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('out');a=p.parse_args();run(a.url,a.out)
