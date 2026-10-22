"""Optional browser QA; requires Playwright and a local server on port 8080."""
import json
import pathlib
from playwright.sync_api import sync_playwright, expect

ROOT=pathlib.Path(__file__).resolve().parents[1]
OUT=ROOT/'test-results';OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
    page=browser.new_page(viewport={'width':1440,'height':1000},accept_downloads=True)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto('http://127.0.0.1:8080')
    page.locator('#library').click();page.locator('[data-edit-module]').first.wait_for()
    assert page.locator('[data-module]').count()==177
    page.locator('#library-integration').select_option('formal');assert page.locator('[data-module]').count()==25
    page.locator('#library-search').fill('双齿轮');page.locator('[data-edit-module="plains_twin_gears"]').click()
    expect(page.locator('#revision-operation')).to_have_value('modify_existing')
    assert '正式流程' in page.locator('#revision-info').inner_text()
    page.locator('[data-add="mushroom"]').click();assert '新增 1' in page.locator('.change-count').inner_text()
    with page.expect_download() as f:page.locator('#save-file').click()
    f.value.save_as(str(OUT/'modify.json'));modified=json.loads((OUT/'modify.json').read_text())
    assert modified['changeRequest']['target']['moduleId']=='plains_twin_gears'
    assert modified['changeRequest']['preserveModuleIdentity'] is True
    page.screenshot(path=str(OUT/'revision.png'))
    page.locator('#library').click();page.locator('#library-search').fill('双齿轮');page.locator('[data-variant-module="plains_twin_gears"]').click()
    expect(page.locator('#revision-operation')).to_have_value('new_variant')
    page.locator('#revision-info [data-prop="suggestedModuleId"]').fill('plains_twin_gears_slow')
    page.locator('#revision-info [data-prop="suggestedModuleId"]').press('Tab')
    with page.expect_download() as f:page.locator('#save-file').click()
    f.value.save_as(str(OUT/'variant.json'));variant=json.loads((OUT/'variant.json').read_text())
    assert variant['changeRequest']['target'] is None and variant['changeRequest']['suggestedModuleId']=='plains_twin_gears_slow'
    catalog=(ROOT/'library/catalog.json').read_text();game_sha=json.loads(catalog)['sourceCommit'];editor_sha='b'*40
    def response(route,data,status=200):
        route.fulfill(status=status,body=json.dumps(data),content_type='application/json',headers={'Access-Control-Allow-Origin':'*'})
    game_url='https://api.github.com/repos/zhipijun1996/gunman-rush/commits/main'
    page.route(game_url,lambda r:response(r,{'sha':game_sha}))
    page.route('https://api.github.com/repos/zhipijun1996/map-edit/commits/main',lambda r:response(r,{'sha':editor_sha}))
    def raw(route):
        path=route.request.url.split('/'+editor_sha+'/',1)[-1]
        f=ROOT/path
        route.fulfill(body=f.read_bytes(),content_type='application/json' if path.endswith('.json') else 'image/svg+xml',headers={'Access-Control-Allow-Origin':'*'})
    page.route('https://raw.githubusercontent.com/zhipijun1996/map-edit/**',raw)
    page.locator('#library').click();page.locator('#update-library').click()
    page.get_by_text('已是最新项目版本',exact=True).wait_for()
    assert page.locator('#title').input_value()==variant['title']
    page.screenshot(path=str(OUT/'update.png'))
    page.locator('#back-library').click();page.screenshot(path=str(OUT/'library.png'))
    # Open an immutable-commit module after a refresh, verifying hash and URL binding.
    page.locator('#library-search').fill('双齿轮');page.locator('[data-edit-module="plains_twin_gears"]').click()
    expect(page.locator('#revision-operation')).to_have_value('modify_existing')
    page.locator('#library').click()
    page.unroute(game_url);page.route(game_url,lambda r:response(r,{'sha':'a'*40}))
    page.locator('#update-library').click();page.get_by_text('项目有新提交，等待生成新库',exact=True).wait_for()
    assert page.locator('#start-library-sync').get_attribute('href').endswith('actions/workflows/sync-library.yml')
    page.unroute(game_url);page.route(game_url,lambda r:response(r,{},403))
    page.locator('#refresh-library-update').click();page.get_by_text('当前模块库和你的草稿保留不变。',exact=True).wait_for()
    page.locator('#back-library').click();assert page.locator('[data-module]').count()==177
    assert not errors,errors
    mobile=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True)
    mobile.goto('http://127.0.0.1:8080');mobile.locator('#library').tap();mobile.locator('[data-edit-module]').first.wait_for()
    mobile.locator('#library-search').fill('双齿轮');mobile.locator('[data-edit-module="plains_twin_gears"]').tap()
    mobile.locator('#inspector-toggle').tap();expect(mobile.locator('#revision-operation')).to_have_value('modify_existing')
    assert mobile.locator('#revision-operation').is_visible();mobile.screenshot(path=str(OUT/'phone.png'))
    print('PASS: integration filters; modify/variant identity and exports; live-library reads; pending/error states; drafts preserved; mobile controls; no JS errors.')
    browser.close()
