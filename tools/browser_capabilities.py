"""Capability editor acceptance check. Local by default; URL env supports deployed QA."""
import json,os,pathlib
from playwright.sync_api import sync_playwright,expect
ROOT=pathlib.Path(__file__).resolve().parents[1];OUT=ROOT/'test-results';OUT.mkdir(exist_ok=True)
url=os.environ.get('EDITOR_URL','http://127.0.0.1:8080')
with sync_playwright() as p:
    options={'executable_path':'/usr/bin/chromium','headless':True,'args':['--no-sandbox']}
    if url.startswith('https:'): options['proxy']={'server':os.environ['HTTPS_PROXY']}
    browser=p.chromium.launch(**options)
    page=browser.new_page(viewport={'width':1440,'height':1000},accept_downloads=True)
    errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
    page.goto(url);page.locator('#library').click();page.locator('[data-edit-module]').first.wait_for()
    page.locator('#library-search').fill('钩索');assert page.locator('[data-module]').count()>0
    page.locator('#library-search').fill('双齿轮');page.locator('[data-edit-module="plains_twin_gears"]').click()
    expect(page.locator('#revision-operation')).to_have_value('modify_existing')
    page.locator('.capability-card > summary').click()
    page.locator('[data-ability-group="all"][data-ability="grapple"]').check()
    page.locator('#add-ability-group').click();page.locator('#add-ability-group').click()
    # First group = double jump OR wall climb; second group = shot recoil OR custom.
    page.locator('#custom-ability').fill('弹跳能力');page.locator('#add-custom-ability').click()
    page.locator('[data-ability-group="1"][data-ability="shot_recoil"]').check()
    page.locator('[data-ability-group="1"][data-ability="弹跳能力"]').check()
    page.locator('[data-ability-group="1"][data-ability="double_jump"]').uncheck()
    page.locator('[data-ability-group="1"][data-ability="wall_climb"]').uncheck()
    page.locator('[data-ability-group="all"][data-ability="弹跳能力"]').uncheck()
    page.locator('#capability-status').select_option('defined')
    page.locator('#capability-note').fill('主路必须满足；奖励支路可另外设计');page.locator('#capability-note').press('Tab')
    assert '能力要求已调整' in page.locator('.change-count').inner_text()
    assert '或' in page.locator('.capability-card > summary').inner_text()
    with page.expect_download() as f:page.locator('#save-file').click()
    f.value.save_as(str(OUT/'capabilities.json'));saved=json.loads((OUT/'capabilities.json').read_text())
    r=saved['capabilityRequirements'];assert r['status']=='defined' and 'grapple' in r['allOf']
    assert r['anyOfGroups']==[['double_jump','wall_climb'],['shot_recoil','弹跳能力']]
    assert saved['changeRequest']['capabilityChanges']['changed'] and saved['changeRequest']['target']['moduleId']=='plains_twin_gears'
    assert saved['changeRequest']['objectChanges']=={'added':[],'removed':[],'modified':[]}
    page.locator('#capability-status').select_option('partial');page.locator('#undo').click()
    page.locator('.capability-card > summary').click() if not page.locator('#capability-status').is_visible() else None
    expect(page.locator('#capability-status')).to_have_value('defined')
    page.wait_for_timeout(400);page.reload();page.locator('.capability-card > summary').click()
    expect(page.locator('#capability-status')).to_have_value('defined');expect(page.locator('#capability-note')).to_have_value(r['note'])
    page.locator('.capability-card').scroll_into_view_if_needed();page.screenshot(path=str(OUT/'capabilities.png'))
    # Export includes a nonempty PNG with capability annotation in its SVG source.
    with page.expect_download() as f:page.locator('#export').click()
    f.value.save_as(str(OUT/'capabilities-image.png'));assert (OUT/'capabilities-image.png').stat().st_size>5000
    # Phone inspector must keep requirements controls reachable without horizontal overflow.
    page.set_viewport_size({'width':390,'height':844});page.locator('#inspector-toggle').click()
    page.locator('#capability-status').scroll_into_view_if_needed();expect(page.locator('#capability-status')).to_be_visible()
    assert page.evaluate('document.documentElement.scrollWidth<=window.innerWidth')
    page.screenshot(path=str(OUT/'capabilities-phone.png'))
    assert not errors,errors
    print('PASS:',url,'AND/OR editing, custom ability, metadata-only change request, undo, reload, PNG, phone, no JS errors')
    browser.close()
