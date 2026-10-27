"""Assemble the current-only editor's static fetch closure, not an experiment tree.

python3 tools/build_editor_site.py --out dist
Historical generation Web assets retain their paths for video download links.
Godot source, raw physics, old module catalogs and PCG archives are excluded.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IMPORT = re.compile(r"(?:import|export)\s+(?:[^;\n]*?\s+from\s*)?['\"]([^'\"]+)['\"]")
WEB_SUFFIXES = {'.html', '.js', '.css', '.json', '.svg', '.png', '.jpg', '.jpeg', '.webp', '.gif',
                '.mp4', '.webm', '.ogg', '.mp3', '.wav', '.wasm', '.pck', '.zip', '.txt', '.md',
                '.ico', '.woff', '.woff2', '.ttf', '.otf', '.bin', '.data'}
EXCLUDED = {'__pycache__', '.godot', 'source_snapshot', 'capture-source', 'physics', 'raw', 'archives'}


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def relative(value):
    text = str(value).removeprefix('./')
    path = Path(text)
    if path.is_absolute() or '..' in path.parts or not text or any(c in text for c in ('?', '#', '\\')):
        raise ValueError('unsafe_web_asset:'+text)
    return path


def build(destination, include_history=True):
    destination = Path(destination).resolve()
    if destination.exists(): raise ValueError('web_output_must_be_new:'+str(destination))
    if destination == ROOT or ROOT.is_relative_to(destination): raise ValueError('unsafe_web_output')
    destination.mkdir(parents=True)
    copied = {}; fetches = []; pending = [Path('app.js')]
    def asset(name, expected=None, purpose='editor'):
        path = relative(name); source = ROOT/path
        if not source.is_file(): raise ValueError('missing_web_asset:'+str(path))
        if expected is not None and sha(source) != expected: raise ValueError('web_asset_sha_mismatch:'+str(path))
        target = destination/path
        if str(path) not in copied:
            target.parent.mkdir(parents=True, exist_ok=True)
            if purpose == 'historical_generation_web_asset':
                try: os.link(source, target)
                except OSError: shutil.copy2(source, target)
            else: shutil.copy2(source, target)
            copied[str(path)] = purpose
        return path
    asset('index.html'); asset('style.css')
    while pending:
        path = pending.pop()
        if str(path) in copied: continue
        asset(path)
        for specifier in IMPORT.findall((ROOT/path).read_text()):
            if specifier.startswith('.'):
                # Resolve repository-relative imports without treating cwd as a root.
                imported = (ROOT/path.parent/specifier.split('?', 1)[0]).resolve().relative_to(ROOT)
                pending.append(imported)
    catalog_path = asset('modules/catalog.json', purpose='current_catalog')
    catalog = json.loads((ROOT/catalog_path).read_text()); current_versions = {}
    for entry in catalog['modules']:
        document = asset(entry['file'], entry['contentSha256'], 'current_document')
        asset(entry['thumbnail'], purpose='current_thumbnail')
        current_versions[entry['moduleId']] = (entry['contentVersion'], entry['contentSha256'])
        fetches.extend([str(document), str(relative(entry['thumbnail']))])
        for reference in entry.get('cornerConfigurationReceipts', []):
            receipt_path = asset(reference['path'], reference['sha256'], 'corner_receipt')
            receipt = json.loads((ROOT/receipt_path).read_text())
            if receipt['baseContentVersion'] != entry['contentVersion'] or receipt['baseDocumentSha256'] != entry['contentSha256']:
                raise ValueError('web_corner_receipt_base_mismatch')
            fetches.append(str(receipt_path))
            for field in ('configuration', 'package'):
                target = asset(receipt[field]['path'], receipt[field]['sha256'], 'corner_'+field)
                fetches.append(str(target))
            target_thumbnail = relative(receipt['configuration']['path']).parent/'thumbnail.svg'
            if (ROOT/target_thumbnail).is_file(): asset(target_thumbnail, purpose='corner_thumbnail')
    aliases = ROOT/'modules/aliases.json'
    if aliases.is_file(): asset('modules/aliases.json', purpose='current_aliases')
    inventory_path = Path('pcg/migration/foundation-v1/corner-port-inventory-v1.json')
    if (ROOT/inventory_path).is_file():
        original = json.loads((ROOT/inventory_path).read_text())
        rows = [row for row in original.get('rows', []) if row.get('scope') == 'current'
                and current_versions.get(row.get('moduleDocumentId')) == (row.get('contentVersion'), row.get('documentSha256'))]
        inventory = {**original, 'rows': rows, 'counts': {'current': len(rows)},
                     'applicableOptions': sum(row.get('applicableOptions', 0) for row in rows),
                     'certifiedOptions': sum(row.get('certifiedOptions', 0) for row in rows),
                     'filteredForWeb': True, 'sourceSha256': sha(ROOT/inventory_path)}
        target = destination/inventory_path; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(inventory, ensure_ascii=False, indent=2)+'\n')
        copied[str(inventory_path)] = 'current_corner_assessment'
        fetches.append(str(inventory_path))
    for standard in ('MAP_FOUNDATION.md', 'MAP_GENERATION_GUIDE.md'):
        if (ROOT/standard).is_file(): asset(standard, purpose='standard')
    history = 0
    history_selection = 'omitted'
    if include_history:
        try:
            names = subprocess.check_output(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard', '--', 'generation'], cwd=ROOT)
            historical_paths = [ROOT/name for name in names.decode().split('\0') if name]
            history_selection = 'git_tracked_and_unignored_web_assets'
        except (OSError, subprocess.CalledProcessError):
            historical_paths = list((ROOT/'generation').rglob('*'))
            history_selection = 'source_archive_web_assets'
        for path in sorted(historical_paths):
            if (not path.is_file() or path.suffix.lower() not in WEB_SUFFIXES
                    or any(part in EXCLUDED for part in path.relative_to(ROOT/'generation').parts)
                    or path.name.endswith(('.input.json', '.output.json', '.raw.json'))): continue
            asset(path.relative_to(ROOT), purpose='historical_generation_web_asset'); history += 1
    (destination/'.nojekyll').touch()
    for path in fetches:
        if not (destination/path).is_file(): raise ValueError('missing_editor_fetch_target:'+path)
    if (destination/'library').exists() or (destination/'pcg/results').exists() or (destination/'pcg/archives').exists():
        raise ValueError('legacy_or_raw_tree_in_web_output')
    forbidden = [p for p in destination.rglob('*') if p.is_file() and
                 (p.name == 'project.godot' or p.suffix in ('.gd', '.tscn', '.tres', '.uid'))]
    if forbidden: raise ValueError('Godot_source_in_web_output:'+str(forbidden[0]))
    manifest = dict(schema='map-notes/current-editor-static-build/v1', catalogSha256=sha(ROOT/catalog_path),
        currentModules=len(catalog['modules']), assets=len(copied), historicalWebAssets=history,
        historicalAssetSelection=history_selection,
        editorFetchTargets=fetches, fetchClosureComplete=True, legacyCatalogsIncluded=False,
        rawPhysicsIncluded=False, godotProjectIncluded=False,
        files={name: {'purpose': purpose, 'sha256': sha(destination/name)} for name, purpose in copied.items()})
    (destination/'web-assets.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({k: v for k, v in manifest.items() if k not in ('files', 'editorFetchTargets')}, ensure_ascii=False))
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--out', type=Path, default=ROOT/'dist')
    parser.add_argument('--no-history', action='store_true')
    arguments = parser.parse_args(); build(arguments.out, not arguments.no_history)
