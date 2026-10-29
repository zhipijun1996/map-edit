"""Mobile/browser regression for the current workshop; does not run Godot."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, os
BASE=os.environ.get('WORKSHOP_BASE','http://127.0.0.1:8876/generation/module-workshop/')
with sync_playwright() as p:
 browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
 page=browser.new_page(viewport=dict(width=390,height=844),is_mobile=True,has_touch=True);errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.goto(BASE);page.wait_for_selector('.module-card');data=page.evaluate("fetch('data.json').then(r=>r.json())");assert f"找到 {data['counts']['ARCHIVED']+data['counts']['IMPLEMENTED_CANDIDATE']} 个" in page.locator('#result-count').inner_text()
 # A completed document can be filtered by its own size, same directed Route and ability.
 page.locator('#filters select[name=stage]').select_option('ARCHIVED');assert f"找到 {data['counts']['ARCHIVED']} 个" in page.locator('#result-count').inner_text();page.locator('[data-detail]').first.click();assert page.locator('#detail').is_visible();assert page.locator('#detail-body table').count()==3;assert 'UNKNOWN' in page.locator('#detail-body').inner_text();page.locator('#close-detail').click()
 page.locator('#filters button[type=reset]').click();page.wait_for_timeout(50);page.locator('#filters select[name=ports]').select_option('4');page.wait_for_function('document.querySelectorAll(".module-card").length>0');assert all('4 Port'in x for x in page.locator('.module-card .badge.neutral').all_inner_texts());page.locator('#filters select[name=width]').select_option('3');page.locator('#filters select[name=height]').select_option('1');assert page.locator('#no-results').is_visible()
 page.locator('#filters button[type=reset]').click();page.wait_for_timeout(50);page.locator('#filters select[name=from]').select_option('LEFT');page.locator('#filters select[name=to]').select_option('RIGHT');page.locator('#filters details').evaluate('(e)=>e.open=true');page.locator('#filters input[name=useAvailable]').check();page.locator('input[data-owned][value=grapple]').check();page.reload();page.wait_for_selector('.module-card');assert page.locator('input[data-owned][value=jump]').is_checked();assert page.locator('input[data-owned][value=shot_recoil]').is_checked();assert page.locator('input[data-owned][value=grapple]').is_checked();assert page.locator('#filters select[name=from]').input_value()=='LEFT'
 page.locator('#filters button[type=reset]').click();page.wait_for_timeout(50)
 for width in [390,320,1280]:
  page.set_viewport_size(dict(width=width,height=844));assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),width
 page.set_viewport_size(dict(width=390,height=844));page.locator('#idea-title').fill('手机创意');raw='  左射铃，同时反冲。\n<script>alert("不能执行")</script>  ';page.locator('#idea-text').fill(raw);page.locator('#idea-constraints').fill('5×4，反冲，三口');page.locator('#idea-form button[type=submit]').click();assert page.locator('.draft pre').inner_text()==raw;assert page.locator('.draft script').count()==0;page.reload();page.wait_for_selector('.draft');assert page.locator('#idea-text').input_value()==raw
 page.locator('[data-send-idea]').click();assert raw in page.locator('#copy-text').input_value();page.locator('#close-copy').click();page.locator('#ai-brief').click();assert '当前 Codex 大模型会话' in page.locator('#copy-text').input_value();assert '不直接实现' in page.locator('#copy-text').input_value();page.locator('#close-copy').click()
 with page.expect_download() as info:page.locator('#export-drafts').click()
 download=info.value;backup=Path('/tmp/module-workshop-browser-backup.json');download.save_as(backup);d=json.loads(backup.read_text());assert d['drafts'][0]['verbatim']==raw
 page.locator('#import-drafts').set_input_files(str(backup));assert page.locator('.draft').count()==1
 draft_id=page.locator('[data-edit-idea]').first.get_attribute('data-edit-idea');page.locator('[data-edit-idea]').first.click();assert page.locator('#idea-text').input_value()==raw;page.locator('#idea-text').fill('取消的改动');page.locator('#cancel-idea-edit').click();assert page.locator('.draft pre').inner_text()==raw
 page.locator('[data-edit-idea]').first.click();raw+='修改后的原话';page.locator('#idea-text').fill(raw);page.locator('#idea-title').fill('修改后的创意');page.locator('#save-idea').click();assert page.locator('[data-edit-idea]').first.get_attribute('data-edit-idea')==draft_id;assert page.locator('.draft pre').inner_text()==raw;page.reload();page.wait_for_selector('.draft');assert page.locator('.draft pre').inner_text()==raw
 before=page.locator('#published-ideas article').count();page.locator('[data-delete-idea]').click();assert page.locator('.draft').count()==0;assert page.locator('#published-ideas article').count()==before;page.locator('#undo-draft-delete').click();assert page.locator('.draft pre').inner_text()==raw
 with page.expect_download() as info:page.locator('#export-drafts').click()
 backup=Path('/tmp/module-workshop-edited-backup.json');info.value.save_as(backup);page.locator('[data-delete-idea]').click();page.reload();page.wait_for_selector('.module-card');assert page.locator('.draft').count()==0;page.locator('#import-drafts').set_input_files(str(backup));assert page.locator('.draft pre').inner_text()==raw
 for form in page.locator('.feedback-form').all():
  form.locator('input[value=CHANGE]').check();form.locator('button').click();assert form.get_attribute('data-version') in page.locator('#copy-text').input_value();page.locator('#close-copy').click()
 pending=page.locator('.feedback-form')
 if pending.count():
  form=pending.first;form.locator('input[value=CHANGE]').check();form.locator('textarea').fill('右岸再抬高一格');form.locator('button').click();assert 'sha256:'in page.locator('#copy-text').input_value();assert '右岸再抬高一格'in page.locator('#copy-text').input_value();page.locator('#close-copy').click();page.reload();page.wait_for_selector('.feedback-form');assert page.locator('.feedback-form').first.locator('input[value=CHANGE]').is_checked();assert page.locator('.feedback-form').first.locator('textarea').input_value()=='右岸再抬高一格'
  assert '待设计审核' in page.locator('#published-ideas').inner_text()
 else:
  assert page.locator('.received-idea-decision').count()==len([i for i in data['ideas']if i.get('design')]);assert '设计保留' in page.locator('#published-ideas').inner_text()
 # Browser-local opinions never change the repository workflow state.
 page.locator('[data-idea-zoom]').first.click();page.wait_for_function('document.querySelector("#detail-body img").complete && document.querySelector("#detail-body img").naturalWidth>0');page.screenshot(path='/tmp/module-workshop-design-mobile.png');page.locator('#close-detail').click();page.locator('#pipeline-stage').select_option('NEEDS_ALIGNMENT');assert page.locator('.pipeline-row').count()==data['counts']['NEEDS_ALIGNMENT']
 for width in [320,390]:
  page.set_viewport_size(dict(width=width,height=844));assert page.evaluate('document.documentElement.scrollWidth<=innerWidth')
 page.locator('#library').scroll_into_view_if_needed();page.screenshot(path='/tmp/module-workshop-library-mobile.png');assert not errors,errors
 browser.close()
print(json.dumps(dict(mobileWidths=[390,320],desktopWidth=1280,combinedFilters=True,exactVersionFeedback=True,localDraftBackup=True,approvalNotSelfPromoted=True,jsErrors=errors,physicsRun=False)))
