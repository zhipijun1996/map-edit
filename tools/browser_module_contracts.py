"""Read actual SVGs; import exact JSON into editor, verify edit invalidation."""
import argparse,hashlib,json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
def run(base,out,collection="plains-v1",sample_prefix="P01",expected_count=4):
 out=Path(out);out.mkdir(parents=True,exist_ok=True);errors=[]
 manifest=json.loads((ROOT/f'generation/contracts/{collection}/manifest.json').read_text());sample=next(m for m in manifest['modules']if m['title'].startswith(sample_prefix))
 with sync_playwright()as p:
  b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox']);page=b.new_page(viewport={'width':1360,'height':950},accept_downloads=True);page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(base.rstrip('/')+f'/generation/contracts/{collection}/',wait_until='networkidle');assert page.locator('img').count()==expected_count
  assert page.locator('img').evaluate_all('(xs)=>xs.every(x=>x.complete&&x.naturalWidth>0)')
  with page.expect_download()as download:page.locator('[data-module-id="'+sample['id']+'"] a[download]').click()
  downloaded=out/'module.mapnote.json';download.value.save_as(str(downloaded));assert hashlib.sha256(downloaded.read_bytes()).hexdigest()==sample['contentSha256']
  page.screenshot(path=str(out/'contracts.png'),full_page=True)
  page.goto(base,wait_until='networkidle');page.locator('#file-input').set_input_files(str(downloaded));page.locator('[data-contract-state="current"]').wait_for()
  state=page.evaluate('async()=>{const c=await import("./module-contract.js");return {hash:c.sha256("失序之钟"),api:typeof c.assemblyInterface}}');assert state['api']=='function'and state['hash']==hashlib.sha256('失序之钟'.encode()).hexdigest()
  doc=json.loads(downloaded.read_text());assert doc['id']==sample['id'];first=doc['objects'][0];page.locator('[data-id="'+first['id']+'"]').first.click(force=True)
  field=page.locator('[data-prop="w"]');field.fill(str(first['w']-1));field.dispatch_event('change');page.locator('[data-contract-state="stale"]').wait_for();page.wait_for_timeout(400)
  page.reload(wait_until='networkidle');page.locator('[data-contract-state="stale"]').wait_for();page.screenshot(path=str(out/'editor-stale.png'),full_page=True);assert not errors
  receipt=dict(base=base,documents=expected_count,svg_decoded=True,json_download_sha256=sample['contentSha256'],import_preserves_identity=True,browser_sha256_matches_node=True,edited_geometry_invalidates_contract=True,stale_draft_survives_reload=True,errors=errors,human_playtests=0)
  (out/'browser.json').write_text(json.dumps(receipt,indent=2));b.close();print(json.dumps(receipt))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('base');a.add_argument('out');a.add_argument('--collection',default='plains-v1');a.add_argument('--sample-prefix',default='P01');a.add_argument('--count',type=int,default=4);x=a.parse_args();run(x.base,x.out,x.collection,x.sample_prefix,x.count)
