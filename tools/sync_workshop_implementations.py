"""Read-only projection of existing implementation evidence; never implements or promotes Modules."""
from pathlib import Path
import argparse, concurrent.futures, hashlib, json, re, subprocess, tempfile, urllib.request
ROOT = Path(__file__).resolve().parents[1]
INDICES = ['first-40-v1', 'review-refresh-v1', '157-upper-block-v1', 'review-029-v1',
           'clarified-three-v1', 'review-031-v1', 'review-040-v1']

def sync(ref, pr):
    if not re.fullmatch(r'[a-f0-9]{40}', ref): raise ValueError('Use an immutable 40-character commit SHA')
    meta=json.loads(urllib.request.urlopen('https://api.github.com/repos/zhipijun1996/map-edit/pulls/'+str(pr),timeout=30).read())
    if meta['head']['sha']!=ref: raise ValueError('Use the actual PR head commit; inspect a moved head before refreshing')
    base = 'https://raw.githubusercontent.com/zhipijun1996/map-edit/'+ref+'/'
    def fetch(path, expected=None):
        if path.startswith('/') or '..' in Path(path).parts or not path.endswith('.json'): raise ValueError('unsafe source')
        raw = urllib.request.urlopen(base+path, timeout=30).read()
        if expected and hashlib.sha256(raw).hexdigest() != expected: raise ValueError('source SHA mismatch: '+path)
        return json.loads(raw)
    latest = {}; sources = []
    for name in INDICES:
        path = 'feedback/manual-review/implementation-results/'+name+'/index.json'
        d = fetch(path); sources.append(path)
        refs = [d['result']] if 'result' in d else [r['result'] for r in d.get('results', [])]
        for r in refs: latest[Path(r['path']).stem] = r
    def item(pair):
        id, r = pair; result = fetch(r['path'], r['sha256']); m = result.get('module') or {}
        doc = fetch(m['path'], m['sha256']) if m.get('path') and m.get('sha256') else None
        if doc:
            # Preserve original bytes as proof rather than re-serializing for the SHA comparison.
            assert doc['generationContract']['contentVersion'] == result['implementationVersion']
        return dict(reviewId=id, resultReference=r, result=result, document=doc)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: rows = list(pool.map(item, latest.items()))
    with tempfile.TemporaryDirectory(prefix='module-workshop-') as tmp:
        source = Path(tmp)/'import.json'; source.write_text(json.dumps(dict(ref=ref, repository='zhipijun1996/map-edit',
            pullRequest=pr, merged=meta['merged'], indices=sources, rows=rows), ensure_ascii=False))
        subprocess.run(['node', 'tools/build_module_workshop.mjs', '--import-snapshot', str(source)], cwd=ROOT, check=True)

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ref', required=True); p.add_argument('--pr', type=int, required=True)
    a = p.parse_args(); sync(a.ref, a.pr)
