"""Browser regression for the repository-update button, without Godot changes."""
import json,pathlib
from playwright.sync_api import sync_playwright,expect
ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'test-results/repository-library';OUT.mkdir(parents=True,exist_ok=True)
catalog=json.loads((ROOT/'library/workshop/catalog.json').read_text());tip='f'*40
entries=catalog['modules'];tree={'truncated':False,'tree':[{'type':'blob','path':e['recordPath']}for e in entries]}
curated={'rows':[{'contentVersion':e['contentVersion'],'selected_for_plains_candidates':e['scope']=='plains','selection_reason':'reserved_for_later_abilities'if e['scope']=='advanced'else'pacing_held'if e['scope']=='held'else'unclassified','content_role':e.get('contentRole','UNKNOWN')}for e in entries]}

def install(page):
 def api(route):
  url=route.request.url
  d=tree if '/git/trees/'in url else {'sha':tip}
  route.fulfill(body=json.dumps(d),content_type='application/json',headers={'Access-Control-Allow-Origin':'*'})
 def raw(route):
  relative=route.request.url.split('/'+tip+'/',1)[1]
  if relative in ['generation/workshop/plains-recoil-v1/catalog.json','generation/workshop/plains-recoil-current/catalog.json']:data=json.dumps(curated).encode()
  else:
   e=next(e for e in entries if relative in [e['recordPath'],e['sourcePath']])
   data=json.dumps({'id':e['moduleId'],'contentVersion':e['contentVersion'],'document_sha256':e['contentSha256']}).encode()if relative==e['recordPath']else(ROOT/e['file']).read_bytes()
  route.fulfill(body=data,content_type='application/json',headers={'Access-Control-Allow-Origin':'*'})
 page.route('https://api.github.com/repos/zhipijun1996/map-edit/**',api)
 page.route('https://raw.githubusercontent.com/zhipijun1996/map-edit/**',raw)

with sync_playwright()as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=b.new_page(viewport={'width':1440,'height':1000},accept_downloads=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));install(page)
 page.goto('http://127.0.0.1:8080');page.locator('#title').fill('更新前的草稿');page.locator('#update-repository-modules').click()
 expect(page.locator('[data-repository-module]')).to_have_count(len(entries),timeout=30000);expect(page.locator('#repository-library-notice')).to_contain_text('已更新')
 expect(page.locator('#title')).to_have_value('更新前的草稿')
 page.locator('#library-scope').select_option('plains');expect(page.locator('[data-repository-module]')).to_have_count(sum(e['scope']=='plains'for e in entries))
 page.locator('#library-scope').select_option('advanced');expect(page.locator('[data-repository-module]')).to_have_count(sum(e['scope']=='advanced'for e in entries))
 page.locator('#library-scope').select_option('');page.locator('#library-search').fill('先压门');expect(page.locator('[data-repository-module]')).to_have_count(1)
 page.locator('.module-card img').first.evaluate('(image)=>image.decode()')
 page.screenshot(path=str(OUT/'repository-library.png'))
 page.locator('[data-repository-module]').click();expect(page.locator('#revision-operation')).to_have_value('new_variant')
 with page.expect_download()as download:page.locator('#save-file').click()
 download.value.save_as(str(OUT/'repository-copy.json'));doc=json.loads((OUT/'repository-copy.json').read_text());assert doc['source']['repository']=='zhipijun1996/map-edit';assert doc['changeRequest']['target']is None;assert len(doc['objects'])>0
 expect(page.locator('[data-contract-state="stale"]')).to_be_visible()
 page.screenshot(path=str(OUT/'repository-module-open.png'))
 title=page.locator('#title').input_value();page.locator('#library').click();page.route('https://api.github.com/repos/zhipijun1996/map-edit/commits/**',lambda r:r.fulfill(status=403,body='{}',content_type='application/json'))
 page.locator('#update-library').click();expect(page.locator('#repository-library-notice')).to_contain_text('更新失败',timeout=30000);expect(page.locator('[data-repository-module]')).to_have_count(len(entries));expect(page.locator('#title')).to_have_value(title)
 page.locator('#library-ports').select_option('4');expect(page.locator('[data-repository-module]')).to_have_count(sum(e.get('portCount')==4 for e in entries))
 page.locator('[data-repository-module]').first.click()
 with page.expect_download()as branch_download:page.locator('#save-file').click()
 branch_download.value.save_as(str(OUT/'four-port-copy.json'));branch=json.loads((OUT/'four-port-copy.json').read_text());assert len(branch['generationContract']['ports'])==4;assert len(branch['generationContract']['relations'])==12
 page.locator('#library').click()
 page.locator('#show-game-library').click();expect(page.locator('[data-edit-module]')).to_have_count(177)
 mobile=b.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True);mobile.on('pageerror',lambda e:errors.append(str(e)));install(mobile);mobile.goto('http://127.0.0.1:8080');mobile.locator('#update-repository-modules').tap();expect(mobile.locator('[data-repository-module]')).to_have_count(len(entries),timeout=30000)
 assert mobile.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
 mobile.screenshot(path=str(OUT/'repository-mobile.png'));assert not errors,errors
 b.close();print('PASS: repository update, current candidate counts/scopes, 4-port filter and clone, search, immutable evidence, network-failure preservation, game library and mobile layout.')
