"""Read-only public release verification; actual editor button, no API mocks."""
import hashlib,json,urllib.request
from pathlib import Path
from playwright.sync_api import sync_playwright,expect

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
COMMIT='1736336dd93b594b9007bdf42f5ade4ea6e1bf3c'
ASSETS='4ec03ed5b9f1e23b616695ad32a4e1f46a665588'
BASE='https://zhipijun1996.github.io/map-edit/'
RAW='https://raw.githubusercontent.com/zhipijun1996/map-edit/'+COMMIT+'/'
files=['library/workshop/catalog.json','generation/workshop/plains-recoil-current/catalog.json',
       'generation/workshop/plains30-block-v1/manifest-progress-18-v1.json',
       'generation/workshop/plains30-block-v1/videos/BN06-four-D-C-v1/central-two-wing-bridge-choice-review-only.mp4',
       'generation/workshop/plains30-block-v1/review-excerpts-v1/BA2-forward-v1-excerpt.mp4',
       'generation/workshop/plains30-block-v1/videos/BN04-seam-v1/exact-N04-block-continuity-review-only.mp4']
checks=[]
for name in files:
    data=urllib.request.urlopen(RAW+name,timeout=60).read()
    assert data==(ROOT/name).read_bytes(),name
    checks.append(dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest()))
with sync_playwright()as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000})
    errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
    page.goto(BASE+'?block-release='+COMMIT,wait_until='networkidle',timeout=90000)
    page.locator('#update-repository-modules').click()
    expect(page.locator('[data-repository-module]')).to_have_count(126,timeout=120000)
    notice=page.locator('#repository-library-notice').inner_text();assert '已更新'in notice
    page.locator('#library-scope').select_option('plains')
    expect(page.locator('[data-repository-module]')).to_have_count(108)
    page.locator('#library-search').fill('中庭双翼')
    expect(page.locator('[data-repository-module]')).to_have_count(2)
    page.locator('#library-ports').select_option('4')
    expect(page.locator('[data-repository-module]')).to_have_count(1)
    page.locator('.module-card img').first.evaluate('(image)=>image.decode()')
    page.screenshot(path=str(OUT/'four-port.png'))
    page.locator('[data-repository-module]').click()
    expect(page.locator('#revision-operation')).to_have_value('new_variant')
    assert '中庭双翼'in page.locator('#title').input_value()
    expect(page.locator('[data-contract-state="stale"]')).to_be_visible()
    page.screenshot(path=str(OUT/'four-port-open.png'))
    assert not errors,errors
    browser.close()
receipt=dict(schema='pcg/public-module-release/v2',content_commit=COMMIT,source_assets_commit=ASSETS,
    editor_commit='75d2b028dcfd7d51c8778008e6f2ef15cccc63d3',url=BASE,public_assets=checks,
    live_update_notice=notice,total_modules=126,plains_candidates=108,new_Block_candidates=18,
    real_update_button_verified=True,four_port_filter_and_editable_copy_opened=True,
    javascript_errors=errors,TLS_verification=True,production_admitted=False)
target=OUT/'verification.json';assert not target.exists()
target.write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(receipt,ensure_ascii=False))
