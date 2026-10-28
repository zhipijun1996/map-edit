"""Real current-library progress/proposal/mirror review; no network mocks."""
import argparse
from functools import partial
import hashlib
import http.server
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def run(site,out):
    site=site.resolve();out.mkdir(parents=True,exist_ok=True)
    catalog=json.loads((site/'modules/catalog.json').read_text())
    status=json.loads((site/'modules/corner-batch-status.json').read_text())
    before={entry['file']:sha(ROOT/entry['file']) for entry in catalog['modules']}
    proposal=next(row for row in status['rows'] if row.get('preview'))
    entry=next(e for e in catalog['modules'] if e['id']==proposal['moduleId'])
    preview=proposal['preview'];before[preview['path']]=sha(ROOT/preview['path'])
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(site)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    result=dict(schema='pcg/corner-web-browser/v1',currentTemplates=len(catalog['modules']),
        batchId=status['batchId'],batchCounts=status['counts'],requestsMocked=False,
        certificationGranted=False,sourceDocumentsMutated=False)
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
            page=browser.new_page(viewport={'width':1440,'height':1080});errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.goto(f'http://127.0.0.1:{server.server_port}/')
            page.locator('#library').click()
            expect(page.locator('[data-module]')).to_have_count(len(catalog['modules']))
            expect(page.locator('#corner-batch-summary')).to_contain_text(str(status['currentOptions'])+' 个换边选项')
            expect(page.locator('[data-mirror-preview]')).to_have_count(len(catalog['modules']))
            page.screenshot(path=str(out/'current-library-batch-status.png'))
            # Preview uses the original contract, and leaves the active draft intact.
            draft_before=page.evaluate("localStorage.getItem('map-notes-v1')")
            page.locator(f'[data-mirror-preview="{entry["id"]}"]').click()
            svg=page.locator('svg[data-mirror-preview="geometry-only"]')
            expect(svg).to_be_visible();expect(page.locator('.review-notice')).to_contain_text('不授予')
            original=json.loads((ROOT/entry['file']).read_text());ports=original['generationContract']['ports']
            actual=svg.locator('[data-physical-port]').evaluate_all('(items)=>items.map(e=>({ids:JSON.parse(e.dataset.portAliases),position:e.dataset.portPosition.split(",").map(Number),face:e.dataset.portFace}))')
            bound=original['generationContract']['space']['bounds'];faces={'LEFT':'RIGHT','RIGHT':'LEFT','TOP':'TOP','BOTTOM':'BOTTOM'}
            for group in actual:
                for name in group['ids']:
                    port=next(p for p in ports if p['id']==name)
                    assert group['position']==[2*bound['x']+bound['w']-port['position'][0],port['position'][1]]
                    assert group['face']==faces[port['face']]
            assert page.evaluate("localStorage.getItem('map-notes-v1')")==draft_before
            result['mirrorPreview']=dict(positionsAndFacesMatch=True,logicalNamesPreserved=True,draftUnchanged=True,physicalCertification=False)
            page.screenshot(path=str(out/'mirror-geometry-preview.png'))
            page.locator('#back-mirror-library').click()
            page.locator(f'[data-corner-progress="{entry["id"]}"]').click()
            row=page.locator(f'[data-corner-batch-key="{proposal["key"]}"]')
            expect(row).to_be_visible();expect(row.locator('[data-corner-stage]')).to_have_attribute('data-corner-stage',proposal['status'])
            page.screenshot(path=str(out/'corner-batch-progress.png'))
            row.locator('[data-open-corner-proposal]').click()
            expect(page.locator('#title')).to_have_value(entry['title']+' · 换边试验审阅副本')
            expect(page.locator('#revision-info')).to_contain_text('换边试验 · 未认证')
            copy=page.evaluate("(()=>{const s=JSON.parse(localStorage.getItem('map-notes-v1'));return s.documents.find(d=>d.id===s.activeId);})()")
            frozen=json.loads((ROOT/preview['path']).read_text())
            assert copy['objects']==frozen['objects'] and copy['generationContract']==frozen['generationContract']
            assert copy['intent']['archiveOrigin']['experimental'] is True
            result['proposalReview']=dict(id=entry['id'],status=proposal['status'],exactFrozenGeometry=True,explicitlyUncertified=True)
            page.screenshot(path=str(out/'frozen-corner-proposal.png'))
            assert not errors,errors;result['javascriptErrors']=errors;browser.close()
        assert all(sha(ROOT/path)==digest for path,digest in before.items())
        result['passed']=True
        (out/'verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps(result,ensure_ascii=False))
    finally:server.shutdown();server.server_close()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--site-root',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();run(args.site_root,args.out)
