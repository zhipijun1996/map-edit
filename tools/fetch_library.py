"""Fetch pinned authoring data only, without downloading the game's large art history."""
import concurrent.futures
import json
import pathlib
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
COMMIT = (ROOT / 'library/source-commit.txt').read_text().strip()
rows = json.loads((ROOT / 'library/source/module-index.json').read_text())
rows += [r for r in json.loads((ROOT / 'library/source/generation-index.json').read_text()) if r['name'].endswith('.gd')]

def fetch(row):
    destination = ROOT / 'library/source' / row['path']
    if destination.exists():
        return
    url = f'https://raw.githubusercontent.com/zhipijun1996/gunman-rush/{COMMIT}/{row["path"]}'
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=45) as response:
                data = response.read()
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            return
        except Exception:
            if attempt == 2:
                raise
            time.sleep(1)

with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
    list(pool.map(fetch, rows))
print(f'Fetched {len(rows)} pinned source files at {COMMIT}')
