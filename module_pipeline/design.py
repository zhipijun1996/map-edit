"""Use the existing design renderer, with version-bound current-source output."""

import hashlib, json, shutil, subprocess, tempfile
from pathlib import Path
from . import library as l


def seal(doc):
    if doc.get("schema") != "pcg/module-design/v1":
        raise ValueError("unsupported_design_schema")
    b = doc["bounds"]
    size = doc.get("blockSize", 128)
    if size != 128:
        raise ValueError("design_renderer_currently_requires_128px_blocks")
    if b["w"] <= 0 or b["h"] <= 0 or b["w"] % size or b["h"] % size:
        raise ValueError("design_requires_complete_blocks")
    ids = set()
    for p in doc["ports"]:
        if p["id"] in ids:
            raise ValueError("duplicate_design_port")
        ids.add(p["id"])
        x, y = p["position"]
        face = p["face"]
        edge = x if face in ["LEFT", "RIGHT"] else y
        along = y - b["y"] if face in ["LEFT", "RIGHT"] else x - b["x"]
        if (
            edge
            != {
                "LEFT": b["x"],
                "RIGHT": b["x"] + b["w"],
                "TOP": b["y"],
                "BOTTOM": b["y"] + b["h"],
            }[face]
            or along <= 0
            or along >= (b["h"] if face in ["LEFT", "RIGHT"] else b["w"])
            or abs(along / size - 0.5 - round(along / size - 0.5)) > 1e-7
        ):
            raise ValueError("invalid_design_block_port")
    if any(r["from"] not in ids or r["to"] not in ids for r in doc["intendedRoutes"]):
        raise ValueError("unknown_design_route_port")
    doc["designVersion"] = (
        "sha256:"
        + hashlib.sha256(
            json.dumps(
                {k: v for k, v in doc.items() if k != "designVersion"},
                sort_keys=True,
                ensure_ascii=False,
                separators=(",", ":"),
            ).encode()
        ).hexdigest()
    )
    return doc


def render(folder):
    folder = Path(folder)
    doc = l.read(folder / "design.json")
    stage = Path(tempfile.mkdtemp(prefix="design-render-", dir=l.ROOT / "build"))
    try:
        l.write(
            stage / "input.json",
            dict(
                rows=[
                    dict(
                        source=str((folder / "design.json").resolve()),
                        moduleId=doc["id"],
                        reviewId=doc.get("reviewId", doc["id"]),
                        title=doc["title"],
                        summary=doc.get("summary", ""),
                        sourceSha256=l.sha(folder / "design.json"),
                    )
                ]
            ),
        )
        subprocess.run(
            [
                "python3",
                str(l.ROOT / "tools/production/render_design.py"),
                "--manifest",
                str(stage / "input.json"),
                "--out",
                str(stage / "rendered"),
                "--draft",
                "--svg-only",
            ],
            check=True,
            cwd=l.ROOT,
        )
        shutil.copyfile(
            stage / "rendered" / (str(doc.get("reviewId", doc["id"])) + ".svg"),
            folder / "thumbnail.svg",
        )
    finally:
        shutil.rmtree(stage)
