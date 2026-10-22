"""Difficulty editing and export acceptance; EDITOR_URL can point at Pages."""
import copy,json,os,pathlib
from playwright.sync_api import sync_playwright,expect
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'test-results';OUT.mkdir(exist_ok=True)
url=os.environ.get('EDITOR_URL','http://127.0.0.1:8080')
with sync_playwright() as p:
    opts={'executable_path':'/usr/bin/chromium','headless':True,'args':['--no-sandbox']}
    if url.startswith('https:'):opts['proxy']={'server':os.environ['HTTPS_PROXY']}
    browser=p.chromium.launch(**opts);page=browser.new_page(viewport={'width':1440,'height':1000},accept_downloads=True)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.add_init_script('''const original=URL.createObjectURL.bind(URL);URL.createObjectURL=blob=>{if(blob.type.startsWith('image/svg+xml'))window.exportSvgText=blob.text();return original(blob);};''')
    # Fixture proves the library distinguishes rated/unrated entries, including no matches.
    catalog=json.loads((ROOT/'library/catalog.json').read_text());fixture=copy.deepcopy(catalog);fixture['modules'][0]['difficulty']['score']=7
    page.route('**/library/catalog.json',lambda r:r.fulfill(body=json.dumps(fixture),content_type='application/json'))
    page.goto(url);page.locator('#library').click();page.locator('[data-module]').first.wait_for()
    page.locator('#library-difficulty').select_option('7');assert page.locator('[data-module]').count()==1
    assert '难度 7/10' in page.locator('.module-difficulty').inner_text()
    page.locator('#library-difficulty').select_option('10');assert page.locator('[data-module]').count()==0
    page.locator('#library-difficulty').select_option('unrated');assert page.locator('[data-module]').count()==176
    page.unroute('**/library/catalog.json');page.reload();page.locator('#library').click()
    page.locator('#library-search').fill('双齿轮');page.locator('[data-edit-module="plains_twin_gears"]').click()
    expect(page.locator('#revision-operation')).to_have_value('modify_existing')
    expect(page.locator('#difficulty-score')).to_have_value('')
    page.locator('#difficulty-score').select_option('7')
    page.locator('#difficulty-note').fill('连续三次精确落点，失误回收较少');page.locator('#difficulty-note').press('Tab')
    assert page.locator('.difficulty-change').inner_text()=='难度评分已调整'
    with page.expect_download() as f:page.locator('#save-file').click()
    f.value.save_as(str(OUT/'difficulty.json'));saved=json.loads((OUT/'difficulty.json').read_text())
    assert saved['difficulty']['score']==7 and saved['changeRequest']['difficultyChanges']['changed']
    assert saved['changeRequest']['target']['moduleId']=='plains_twin_gears'
    assert saved['changeRequest']['objectChanges']=={'added':[],'removed':[],'modified':[]}
    page.locator('#difficulty-score').select_option('10');page.locator('#undo').click();expect(page.locator('#difficulty-score')).to_have_value('7')
    page.wait_for_timeout(400);page.reload();expect(page.locator('#difficulty-score')).to_have_value('7')
    page.locator('#difficulty-score').select_option('');expect(page.locator('#difficulty-description')).to_contain_text('未评分不会当成 1 分')
    page.locator('#file-input').set_input_files(str(OUT/'difficulty.json'));expect(page.locator('#difficulty-score')).to_have_value('7')
    expect(page.locator('#difficulty-note')).to_have_value(saved['difficulty']['note'])
    with page.expect_download() as f:page.locator('#export').click()
    f.value.save_as(str(OUT/'difficulty.png'));assert (OUT/'difficulty.png').stat().st_size>5000
    svg=page.evaluate('window.exportSvgText');assert '难度 7/10' in svg and saved['difficulty']['note'] in svg
    page.locator('.difficulty-card summary').click();expect(page.locator('.difficulty-card ol li')).to_have_count(10)
    page.locator('#difficulty-score').scroll_into_view_if_needed();page.screenshot(path=str(OUT/'difficulty-desktop.png'))
    page.set_viewport_size({'width':390,'height':844});page.locator('#inspector-toggle').click()
    page.locator('#difficulty-score').scroll_into_view_if_needed();expect(page.locator('#difficulty-score')).to_be_visible()
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth');page.screenshot(path=str(OUT/'difficulty-phone.png'))
    assert not errors,errors
    print('PASS:',url,'difficulty filters, scoring guide, metadata-only revisions, undo, persistence, file import, PNG annotations, phone and no JS errors.')
    browser.close()
