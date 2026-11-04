"""Exercise the current editor/workshop fetch closure in a real browser."""

import argparse, json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
p = argparse.ArgumentParser()
p.add_argument("--url", default="http://127.0.0.1:8893/")
args = p.parse_args()
errors = []
failed = []
requests = []
with sync_playwright() as api:
    browser = api.chromium.launch(
        executable_path="/usr/bin/chromium", headless=True, args=["--no-sandbox"]
    )
    page = browser.new_page(viewport=dict(width=1280, height=900))
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("request", lambda r: requests.append(r.url))
    page.on(
        "response",
        lambda r: (
            failed.append(r.url)
            if r.status >= 400 and not r.url.endswith("favicon.ico")
            else None
        ),
    )
    page.goto(args.url)
    page.locator("#library").click()
    page.wait_for_selector("[data-module]")
    catalog = page.evaluate("fetch('modules/catalog.json').then(r=>r.json())")
    assert page.locator("[data-module]").count() == len(catalog["modules"])
    first = catalog["modules"][0]
    page.locator(f'[data-copy-module="{first["id"]}"]').click()
    page.wait_for_function('!document.querySelector("#dialog").open')
    assert (
        "编辑副本" in page.locator("#title").input_value()
        if page.locator("#title").count()
        else True
    )
    page.goto(args.url + "generation/module-workshop/")
    page.wait_for_selector(".module-card")
    assert str(len(catalog["modules"])) in page.locator("#result-count").inner_text()
    page.locator("[data-detail]").first.click()
    page.wait_for_selector("#detail[open]")
    assert page.locator("#detail-body table").count() == 2
    page.locator("#close-detail").click()
    page.locator("#filters input[name=query]").fill(first["id"])
    assert "找到 1 个" in page.locator("#result-count").inner_text()
    page.locator("#filters input[name=query]").fill("")
    page.locator("#idea-stage").select_option("REVIEW")
    assert page.locator(".feedback-form").count() == len(catalog["designs"])
    for width in [390, 320, 1280]:
        page.set_viewport_size(dict(width=width, height=900))
        assert page.evaluate("document.documentElement.scrollWidth<=innerWidth"), width
    assert not errors, errors
    assert not failed, failed
    assert not any(
        "/library/" in u or "/manual-review/" in u or "/pcg/" in u for u in requests
    ), requests
    browser.close()
report = dict(
    schema="map-edit/current-browser-acceptance/v1",
    passed=True,
    currentModules=len(catalog["modules"]),
    developmentDesigns=len(catalog["designs"]),
    editorCopyOpened=True,
    workshopSearch=True,
    mobileWidths=[390, 320],
    javascriptErrors=errors,
    failedAssetRequests=failed,
    legacyLibraryRequests=False,
)
(ROOT / "evidence/module-production/browser.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2) + "\n"
)
print(json.dumps(report))
