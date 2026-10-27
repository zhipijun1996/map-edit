"""Actual persisted-library browser smoke. No mocked assets or network routes."""
import argparse
import hashlib
import http.server
import json
from pathlib import Path
import threading
from functools import partial
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def physical_count(ports):
    return len({(tuple(port['position']), port['face']) for port in ports})


def inspect_review(page, document):
    c = document['generationContract']; b = c['space']['bounds']
    footprint = page.locator('#canvas [data-module-footprint]')
    expect(footprint).to_have_count(1)
    for name in ('x', 'y', 'width', 'height'):
        expected = b[{'width': 'w', 'height': 'h'}.get(name, name)]
        assert abs(float(footprint.get_attribute(name))-expected) < 1e-5
    expect(page.locator('#block-grid')).to_be_checked()
    expect(page.locator('#canvas [data-block-grid="128"]')).to_have_count(1)
    groups = page.locator('#canvas [data-physical-port]')
    expect(groups).to_have_count(physical_count(c['ports']))
    actual = groups.evaluate_all('(items)=>items.map(e=>({ids:JSON.parse(e.dataset.portAliases),position:e.dataset.portPosition.split(",").map(Number),face:e.dataset.portFace,text:e.textContent}))')
    assert sorted(name for group in actual for name in group['ids']) == sorted(p['id'] for p in c['ports'])
    for group in actual:
        for name in group['ids']:
            port = next(p for p in c['ports'] if p['id'] == name)
            assert group['position'] == port['position'] and group['face'] == port['face']
            assert port['surface'] in group['text'] and port['permission'] in group['text']
    canvas_box = page.locator('#canvas').bounding_box()
    for label in page.locator('#canvas [data-physical-port] rect').all():
        box = label.bounding_box()
        assert box['x'] >= canvas_box['x']-1 and box['x']+box['width'] <= canvas_box['x']+canvas_box['width']+1, 'Port labels must remain inside the fitted canvas'
    return dict(physicalPorts=len(actual), logicalNames=len(c['ports']), allPositionsMatch=True, portLabelsVisible=True)


def run(out, module_id=None, configuration_id=None, site_root=None, exercise_files=False, update_mode='skip'):
    out.mkdir(parents=True, exist_ok=True)
    site = Path(site_root).resolve() if site_root else ROOT
    catalog_file = site/'modules/catalog.json'
    catalog = json.loads(catalog_file.read_text())
    snapshot = {entry['file']: sha(ROOT/entry['file']) for entry in catalog['modules']}
    for entry in catalog['modules']:
        assert snapshot[entry['file']] == entry['contentSha256'], 'Catalog SHA does not match actual source document'
        for ref in entry.get('cornerConfigurationReceipts', []):
            assert sha(ROOT/ref['path']) == ref['sha256'], 'Configuration receipt SHA does not match the catalog'
            receipt = json.loads((ROOT/ref['path']).read_text())
            target_file = receipt['configuration']['path']
            snapshot[target_file] = sha(ROOT/target_file)
            assert snapshot[target_file] == receipt['configuration']['sha256'], 'Compiled alternative document SHA mismatch'
    inventory_file = site/'pcg/migration/foundation-v1/corner-port-inventory-v1.json'
    inventory = json.loads(inventory_file.read_text()) if inventory_file.exists() else {'rows': []}
    target = next((entry for entry in catalog['modules'] if any(
        r.get('scope') == 'current' and r.get('contentVersion') == entry['contentVersion']
        and r.get('documentSha256') == entry['contentSha256'] and r.get('applicableOptions', 0)
        for r in inventory['rows'])), None)
    if module_id:
        target = next(entry for entry in catalog['modules'] if entry['id'] == module_id)
    class QuietHandler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args): pass
    server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(site)))
    thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
    result = dict(schema='pcg/current-library-browser/v2', catalogSha256=sha(catalog_file),
        currentTemplates=len(catalog['modules']), requestsMocked=False, sourceMutated=False,
        originalDocumentsVerified=len(snapshot), configurationDocumentsVerified=len(snapshot)-len(catalog['modules']),
        physicsCertification=False)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(executable_path='/usr/bin/chromium', headless=True, args=['--no-sandbox'])
            page = browser.new_page(viewport={'width': 1440, 'height': 1080})
            errors = []; page.on('pageerror', lambda error: errors.append(str(error)))
            requests = []; page.on('request', lambda request: requests.append(request.url))
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            page.locator('#library').click()
            expect(page.locator('#library-ports')).to_be_visible()
            expect(page.locator('#show-current-library,#show-game-library,#show-repository-library')).to_have_count(0)
            expect(page.locator('[data-module]')).to_have_count(len(catalog['modules']))
            counts = {}
            for count in sorted({physical_count(m['ports']) for m in catalog['modules']}):
                page.locator('#library-ports').select_option(str(count))
                expected = sum(physical_count(m['ports']) == count for m in catalog['modules'])
                expect(page.locator('[data-module]')).to_have_count(expected); counts[str(count)] = expected
            page.locator('#library-ports').select_option('')
            result['portFilterCounts'] = counts
            page.locator('#library-port-aliases').select_option('yes')
            alias_entries = [m for m in catalog['modules'] if physical_count(m['ports']) != m['portCount']]
            expect(page.locator('[data-module]')).to_have_count(len(alias_entries))
            result['modulesWithAliases'] = [m['id'] for m in alias_entries]
            page.locator('#library-port-aliases').select_option('')
            page.wait_for_function("""()=>[...document.querySelectorAll('.module-card img')].slice(0,3).every(image=>image.complete&&image.naturalWidth>0)""")
            page.screenshot(path=str(out/'current-library.png'))
            if target:
                base = json.loads((ROOT/target['file']).read_text())
                if configuration_id:
                    compiled_port = next((p for p in target.get('ports', []) if any(
                        o.get('allowed') is True and o.get('profileId') == configuration_id
                        for o in p.get('cornerRelocations', {}).values())), None)
                    assert compiled_port, 'Final catalog must expose the certified whole-configuration permission'
                    original_port = next(p for p in base['generationContract']['ports'] if p['id'] == compiled_port['id'])
                    result['catalogOverlay'] = dict(portId=compiled_port['id'], originalFace=original_port['face'],
                        sourceOptions=original_port.get('cornerRelocations'),
                        compiledOptions=compiled_port['cornerRelocations'], configurationId=configuration_id)
                page.locator(f'[data-copy-module="{target["id"]}"]').click()
                panel = page.locator('[data-corner-port-options]')
                expect(panel).to_be_visible(); panel.locator('summary').click()
                expect(panel).to_contain_text('来源版本记录')
                options = panel.locator('[data-corner-option]')
                result['cornerOptionsVisible'] = options.count()
                result['cornerTemplate'] = target['id']
                result['cornerStates'] = options.evaluate_all('(items)=>items.map(el=>el.dataset.relocationAllowed)')
                result['cornerPanelText'] = panel.inner_text()
                panel.scroll_into_view_if_needed()
                result['baseReview'] = inspect_review(page, base)
                first_label = page.locator('#canvas [data-physical-port] text').first
                height = first_label.bounding_box()['height']
                page.locator('#zoom-in').click(); page.locator('#zoom-in').click()
                assert abs(first_label.bounding_box()['height']-height) < 1, 'Port text must stay readable at another zoom'
                page.locator('#fit').click()
                page.locator('#block-grid').uncheck(); expect(page.locator('#canvas [data-block-grid]')).to_have_count(0)
                page.locator('#block-grid').check()
                page.locator('#show-ports').uncheck(); expect(page.locator('#canvas [data-physical-port]')).to_have_count(0)
                page.locator('#show-ports').check()
                result['reviewTogglesAndZoomPassed'] = True
                page.screenshot(path=str(out/'corner-port-panel.png'))
                if configuration_id:
                    menu = page.locator('#revision-info details').filter(has=page.locator('summary', has_text='打开已认证的接口配置'))
                    expect(menu).to_be_visible(); menu.locator('summary').click()
                    menu.locator(f'[data-open-port-configuration="{configuration_id}"]').click()
                    expect(page.locator('#title')).to_have_value(target['title']+' · 接口配置编辑副本')
                    saved = page.evaluate("""()=>{const s=JSON.parse(localStorage.getItem('map-notes-v1'));return s.documents.find(d=>d.id===s.activeId);}""")
                    assert saved['intent']['archiveOrigin']['configurationId'] == configuration_id
                    result['configurationSelected'] = configuration_id
                    result['selectedContentVersion'] = saved['generationContract']['contentVersion']
                    result['selectedPorts'] = [{key: port[key] for key in ('id', 'position', 'face', 'surface', 'permission')}
                                              for port in saved['generationContract']['ports']]
                    result['selectedSceneOriginOffset'] = [-saved['generationContract']['space']['bounds'][key] for key in ('x', 'y')]
                    result['alternativeReview'] = inspect_review(page, saved)
                    page.screenshot(path=str(out/'corner-configuration-open.png'))
                if exercise_files:
                    saved = page.evaluate("""()=>{const s=JSON.parse(localStorage.getItem('map-notes-v1'));return s.documents.find(d=>d.id===s.activeId);}""")
                    with page.expect_download() as download:
                        page.locator('#save-file').click()
                    target_file = out/'editor-copy.mapnote.json'; download.value.save_as(str(target_file))
                    downloaded = json.loads(target_file.read_text())
                    assert downloaded['generationContract']['ports'] == saved['generationContract']['ports']
                    with page.expect_download(timeout=30000) as image:
                        page.locator('#export').click()
                    suffix = Path(image.value.suggested_filename).suffix
                    image_path = out/('editor-review'+suffix); image.value.save_as(str(image_path))
                    assert image_path.stat().st_size > 100
                    result['downloads'] = dict(project=target_file.name, image=image_path.name, passed=True)
            else:
                result['cornerOptionsVisible'] = 0; result['cornerCheck'] = 'NOT_APPLICABLE'
            result['javascriptErrors'] = errors
            assert not any('/library/catalog.json' in url or '/library/workshop/' in url for url in requests), 'Legacy catalogs must never be fetched'
            result['legacyCatalogFetches'] = 0
            if exercise_files:
                result['aliasReviews'] = []
                for entry in alias_entries:
                    page.locator('#library').click(); page.locator(f'[data-copy-module="{entry["id"]}"]').click()
                    expect(page.locator('#title')).to_have_value(entry['title']+' · 编辑副本')
                    source = json.loads((ROOT/entry['file']).read_text())
                    result['aliasReviews'].append(dict(id=entry['id'], **inspect_review(page, source)))
                page.screenshot(path=str(out/'physical-port-aliases.png'))
            if update_mode != 'skip':
                draft_before = page.evaluate("""()=>{const s=JSON.parse(localStorage.getItem('map-notes-v1')),d=s.documents.find(v=>v.id===s.activeId);return {id:d.id,objects:d.objects,contract:d.generationContract};}""")
                page.locator('#update-repository-modules').click()
                page.wait_for_function("""()=>{const e=document.querySelector('#repository-library-notice');return e&&/当前库已更新|更新失败/.test(e.textContent);}""", timeout=180000)
                notice = page.locator('#repository-library-notice').inner_text()
                draft_after = page.evaluate("""()=>{const s=JSON.parse(localStorage.getItem('map-notes-v1')),d=s.documents.find(v=>v.id===s.activeId);return {id:d.id,objects:d.objects,contract:d.generationContract};}""")
                assert draft_before == draft_after, 'Refreshing the catalog changed the active editor draft'
                if update_mode == 'success': assert '当前库已更新' in notice, notice
                else: assert '更新失败' in notice, notice
                result['actualUpdate'] = dict(mode=update_mode, notice=notice, draftUnchanged=True,
                    requestsMocked=False, currentCards=page.locator('[data-module]').count())
                page.screenshot(path=str(out/'current-library-update.png'))
            assert not errors, errors
            browser.close()
        assert all(sha(ROOT/path) == digest for path, digest in snapshot.items()), 'Original Module bytes changed'
        assert sha(catalog_file) == result['catalogSha256'], 'Catalog changed during the final browser verification'
        result['passed'] = True
        (out/'verification.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n')
        print(json.dumps(result, ensure_ascii=False))
    finally:
        server.shutdown(); server.server_close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path,
        default=ROOT/'.cache/migration/browser-current-corners')
    parser.add_argument('--module'); parser.add_argument('--configuration')
    parser.add_argument('--site-root', type=Path); parser.add_argument('--exercise-files', action='store_true')
    parser.add_argument('--update-mode', choices=('skip', 'preserve-on-failure', 'success'), default='skip')
    args = parser.parse_args()
    run(args.out, args.module, args.configuration, args.site_root, args.exercise_files, args.update_mode)
