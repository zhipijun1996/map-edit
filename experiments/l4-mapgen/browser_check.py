"""Optional real Chromium QA. Start the repository HTTP server on port 8080 first."""
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results/browser'
OUT.mkdir(exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
    page = browser.new_page(viewport={'width': 1600, 'height': 1100}, accept_downloads=True)
    errors = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.goto('http://127.0.0.1:8080/experiments/l4-mapgen/viewer.html')
    page.wait_for_function("document.querySelector('#status').textContent.includes('240')")
    page.locator('#region').select_option('plains')
    page.locator('#seed').select_option('0')
    assert page.locator('article.algorithm').count() == 4
    assert page.locator('.graph svg').count() == 12
    assert '消融对照' in page.locator('article.algorithm').nth(3).inner_text()
    page.locator('#view').select_option('spatial')
    assert page.locator('[data-stage]:visible').count() == 4
    page.screenshot(path=str(OUT / 'comparison.png'), full_page=True)
    with page.expect_download() as event:
        page.locator('[data-stage="spatial"]').first.get_by_role('button', name='下载 SVG').click()
    event.value.save_as(str(OUT / 'plains-A-0-spatial.svg'))
    assert '未接真实游戏物理' in (OUT / 'plains-A-0-spatial.svg').read_text()
    page.locator('#region').select_option('forest')
    page.locator('#seed').select_option('28')
    assert '空间代理：失败' in page.locator('article.algorithm').nth(1).inner_text()
    page.locator('#view').select_option('exploration')
    page.screenshot(path=str(OUT / 'failure-forest-B-28.png'), full_page=True)
    page.locator('#view').select_option('all')
    page.locator('.graph .node').first.click()
    assert page.locator('#inspector').get_attribute('open') is not None
    assert '"id"' in page.locator('#detail').inner_text()
    # Save standalone SVGs directly from the actual viewer DOM for offline reading.
    figures = ROOT / 'results/figures'
    figures.mkdir(exist_ok=True)
    page.locator('#region').select_option('plains')
    page.locator('#seed').select_option('0')
    for i, name in enumerate(['A', 'B', 'C', 'C_random']):
        for stage in ['mission', 'exploration', 'spatial']:
            svg = page.locator('article.algorithm').nth(i).locator(f'[data-stage="{stage}"] svg')
            (figures / f'plains-0-{name}-{stage}.svg').write_text(svg.evaluate('(node) => new XMLSerializer().serializeToString(node)'))
    mobile = browser.new_page(viewport={'width': 390, 'height': 844}, is_mobile=True, has_touch=True)
    mobile.goto('http://127.0.0.1:8080/experiments/l4-mapgen/viewer.html')
    mobile.wait_for_function("document.querySelector('#status').textContent.includes('240')")
    mobile.locator('#view').select_option('spatial')
    assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth + 1')
    mobile.screenshot(path=str(OUT / 'mobile.png'), full_page=True)
    assert not errors, errors
    (OUT / 'receipt.json').write_text(json.dumps({'browser': browser.version, 'desktop': [1600, 1100],
        'mobile': [390, 844], 'checks': ['240 records', 'four comparison cards', 'SVG download',
        'view filters', 'failure seed retained', 'node inspector', 'mobile no horizontal overflow'],
        'page_errors': errors, 'status': 'passed', 'scope': 'actual local Chromium viewer; no game physics or remote deployment'}, indent=2))
    browser.close()
print('PASS: real Chromium comparison, filtering, failure diagnostics, SVG export, inspector, mobile layout.')
