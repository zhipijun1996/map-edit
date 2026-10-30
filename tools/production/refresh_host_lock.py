#!/usr/bin/env python3
"""Complete a pinned host lock against literal and formatted res:// references."""
import argparse, concurrent.futures, hashlib, json, re, sys, urllib.parse, urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from module_pipeline import library as l
from integration.install_host import install


def refresh(lock_file, cache, source=None):
    lock_file = Path(lock_file)
    cache = Path(cache)
    cache.mkdir(parents=True, exist_ok=True)
    lock = l.read(lock_file)
    install(lock_file, cache, source)
    repo = lock["repository"].removeprefix("https://github.com/")
    tree_file = cache / "host-git-tree.json"
    if not tree_file.exists():
        tree_file.write_bytes(
            urllib.request.urlopen(
                "https://api.github.com/repos/"
                + repo
                + "/git/trees/"
                + lock["commit"]
                + "?recursive=1",
                timeout=90,
            ).read()
        )
    raw = l.read(tree_file)
    if raw.get("truncated"):
        raise ValueError("host_git_tree_truncated")
    tree = {r["path"]: r for r in raw["tree"] if r["type"] == "blob"}
    extensions = {
        ".gd",
        ".tscn",
        ".tres",
        ".json",
        ".gdshader",
        ".png",
        ".svg",
        ".jpg",
        ".jpeg",
        ".webp",
        ".wav",
        ".ogg",
        ".otf",
        ".ttf",
        ".cfg",
        ".mp3",
        ".theme",
    }
    for iteration in range(8):
        needed = set()
        for name in lock["files"]:
            p = cache / name
            if p.suffix not in [".gd", ".tscn", ".tres", ".json", ".gdshader"]:
                continue
            for ref in re.findall(r"""["']res://([^"'\n]+)["']""", p.read_text()):
                prefix = ref.split("%")[0]
                if prefix in tree:
                    needed.add(prefix)
                elif prefix:
                    needed.update(
                        n
                        for n in tree
                        if n.startswith(prefix) and Path(n).suffix in extensions
                    )
        needed = sorted(n for n in needed if n not in lock["files"])
        if not needed:
            break

        def fetch(name):
            p = cache / name
            if not p.exists():
                data = urllib.request.urlopen(
                    "https://raw.githubusercontent.com/"
                    + repo
                    + "/"
                    + lock["commit"]
                    + "/"
                    + urllib.parse.quote(name),
                    timeout=90,
                ).read()
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_bytes(data)
            data = p.read_bytes()
            blob = hashlib.sha1(
                b"blob " + str(len(data)).encode() + b"\0" + data
            ).hexdigest()
            if blob != tree[name]["sha"]:
                raise ValueError("host_git_blob_mismatch:" + name)
            return name, hashlib.sha256(data).hexdigest()

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            for name, h in pool.map(fetch, needed):
                lock["files"][name] = h
        print(json.dumps(dict(iteration=iteration, added=len(needed))), flush=True)
    else:
        raise ValueError("host_dependency_closure_did_not_converge")
    l.write(lock_file, lock)
    return dict(profile=lock["id"], files=len(lock["files"]))


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lock", type=Path, required=True)
    p.add_argument("--cache", type=Path, required=True)
    p.add_argument("--source", type=Path)
    a = p.parse_args()
    print(json.dumps(refresh(a.lock, a.cache, a.source)))
