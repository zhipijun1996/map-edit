"""Read-only observer plus real replay-button control for the transport proof."""
from pathlib import Path
import argparse,json,time
from playwright.sync_api import sync_playwright

def check(url,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    events=[];errors=[];responses=[];records=[]
    with sync_playwright() as p:
        b=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--enable-webgl','--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        page=b.new_page(viewport={'width':1280,'height':720})
        page.on('console',lambda m:events.append(dict(type=m.type,text=m.text)))
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('response',lambda r:responses.append(dict(url=r.url,status=r.status)))
        try:
            page.goto(url,wait_until='networkidle',timeout=90000)
            page.wait_for_function('window.__pcgLabStateV2 && window.__pcgLabStateV2.case_count===20',timeout=60000)
            state=page.evaluate('window.__pcgLabStateV2');records.append(dict(action='loaded',state=state))
            assert state['id']=='overlay-proof-new-id','Overlay candidate data lost to base pack'
            page.screenshot(path=str(out/'loaded.png'))
            page.mouse.click(940,55);page.wait_for_function('window.__pcgLabStateV2.mode==="replay"',timeout=10000)
            page.wait_for_function('window.__pcgLabStateV2.finished',timeout=20000)
            state=page.evaluate('window.__pcgLabStateV2');records.append(dict(action='real_input_replay',state=state))
            assert state['safe'] and state['stable_frames']>=6 and state['grounded'],state
            page.screenshot(path=str(out/'replayed.png'))
            assert any('OVERLAY_BASE_MOUNTED' in e['text'] for e in events)
            assert any('OVERLAY_SCENE_REQUESTED' in e['text'] for e in events)
            assert not errors,errors
            failures=[e for e in events if e['type']=='error']
            assert not failures,failures
            status='passed'
        except Exception as e:
            status='failed';errors.append(str(e));page.screenshot(path=str(out/'failure.png'))
        result=dict(status=status,url=url,records=records,console=events,page_errors=errors,responses=responses,transport=page.evaluate('window.__overlayTransport'))
        (out/'browser.json').write_text(json.dumps(result,ensure_ascii=False,indent=2));b.close()
        print(json.dumps(dict(status=status,records=len(records),errors=errors),ensure_ascii=False))
        if status!='passed':raise SystemExit(1)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('url');p.add_argument('out');a=p.parse_args();check(a.url,a.out)
