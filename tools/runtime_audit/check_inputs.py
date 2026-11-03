"""Read-only comparison of current main and an explicitly hash-pinned Module ZIP."""

import argparse, copy, gzip, hashlib, importlib.util, io, json, posixpath, re, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
META = {
    "schema",
    "source_sha256",
    "stable_id",
    "ports",
    "world_bounds",
    "entry_port",
    "exit_port",
}
TARGETS = [
    "generated-75b420621682d36fc3b7262784c347f0acea7e55422f7e0abaebbc285fa89198",
    "idea-0363f85c-16c0-4b5f-b3b0-461335608db7-enemies-2",
    "idea-0363f85c-16c0-4b5f-b3b0-461335608db7-enemies-3",
    "idea-96ba6bf1-9b60-470a-9128-54ae7ea44af3",
    "idea-orbit-choice-001",
]
SAMPLES = ["game-plains-ferry-gears", "game-plains-windchime-lesson"]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def read(p):
    return json.loads(Path(p).read_text())


def write(p, v):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(v, ensure_ascii=False, indent=2) + "\n")


def same(a, b):
    if (
        isinstance(a, (int, float))
        and not isinstance(a, bool)
        and isinstance(b, (int, float))
    ):
        return abs(a - b) < 1e-7
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(same(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(same(a[k], b[k]) for k in a)
    return a == b


def checked_zip(path, expected):
    data = Path(path).read_bytes()
    if sha(data) != expected:
        raise ValueError("ZIP_SHA256_MISMATCH_BEFORE_READING")
    z = zipfile.ZipFile(io.BytesIO(data))
    names = z.namelist()
    if len(names) != len(set(names)) or any(
        Path(n).is_absolute() or ".." in Path(n).parts or "\\" in n for n in names
    ):
        raise ValueError("unsafe_or_duplicate_zip_path")
    m = json.loads(z.read("manifest.json"))
    if set(names) - {"manifest.json"} != set(m["files"]):
        raise ValueError("manifest_file_set_mismatch")
    for n, h in m["files"].items():
        if sha(z.read(n)) != h:
            raise ValueError("manifest_hash_mismatch:" + n)
    return z, m


def dependencies(z, manifest):
    locks = [
        json.loads(z.read(n))["files"]
        for n in ["runtime/host-lock.json", "runtime/host-lock-current-game.json"]
    ]
    refs = []
    pattern = r"""(?:\b(?:preload|load)\(\s*["']([^"']+)["']\s*\)|\bextends\s+["']([^"']+)["']|\bpath\s*=\s*["']([^"']+)["'])"""
    for name in z.namelist():
        if not name.endswith((".gd", ".tscn", ".tres")):
            continue
        for match in re.finditer(pattern, z.read(name).decode()):
            ref = next(x for x in match.groups() if x is not None)
            if ref.startswith("res://"):
                target = ref[6:]
                assert all(target in lock for lock in locks), (name, ref)
                kind = "both_host_locks"
            else:
                assert not ref.startswith("/"), (name, ref)
                target = posixpath.normpath(
                    posixpath.join(posixpath.dirname(name), ref)
                )
                assert target in manifest["files"], (name, ref)
                kind = "manifest"
            refs.append(
                dict(source=name, reference=ref, resolved=target, declaredBy=kind)
            )
    dynamic = [
        "resources/enemies/plains_sentry.tres",
        "resources/enemies/plains_charger.tres",
    ]
    for target in dynamic:
        assert all(target in lock for lock in locks), target
    return dict(
        staticReferences=refs,
        checkedDynamicEnemyResources=dynamic,
        scope="Literal load/preload/extends/scene paths plus the inspected plains enemy resource allowlist; not an arbitrary-code dynamic dependency proof. Host transitive resources remain in the full hashed host locks.",
    )


def later_claims(folder, entries):
    assert (
        sha((folder / "reward-claim-validation.json").read_bytes())
        == "baf28c8f04639b829b7ecb1172a55f5600f9fa0dc8b388e49da19175434961d8"
    )
    r = read(folder / "reward-claim-validation.json")
    m = read(folder / "manifest.json")
    assert (
        sha((folder / "manifest.json").read_bytes()) == r["archive"]["manifestSha256"]
    )
    chunks = []
    for part in m["parts"]:
        raw = (folder / part["file"]).read_bytes()
        assert sha(raw) == part["sha256"]
        chunks.append(raw)
    raw = b"".join(chunks)
    assert sha(raw) == m["archive_sha256"]
    z = zipfile.ZipFile(io.BytesIO(raw))
    index = json.loads(z.read("PCG-ARCHIVE-INDEX.json"))

    def member(path):
        item = index[path]
        data = z.read(item.get("archive_entry", path))
        assert sha(data) == item["sha256"]
        return data

    results = []
    for row in r["rows"]:
        p = row["evidence"]
        binding = json.loads(member(p["sourceBindingArchivePath"]))
        assert (
            binding["engine_sha256"] == r["engineSha256"]
            and binding["game_source_commit"] == r["nativeHostCommit"]
            and binding["protected_mismatches"] == 0
        )
        blob = gzip.decompress(member(p["archivePath"]))
        assert sha(blob) == p["raw_output_sha256"]
        raw = json.loads(blob)["results"][p["index"]]
        case = json.loads(member(p["inputArchivePath"]))["cases"][p["index"]]
        data = entries[row["id"]]["_compiled"]
        count = len(data["platforms"])
        assert same(data["platforms"], case["platforms"][:count])
        for key, value in data.items():
            if key in META or key in ["platforms", "one_way_platform_indices"]:
                continue
            assert same(
                value, case.get(key, [] if isinstance(value, list) else None)
            ), (row["id"], key)
        assert [
            i for i in case.get("one_way_platform_indices", []) if i < count
        ] == data["one_way_platform_indices"]
        bounds = entries[row["id"]]["bounds"]
        for x, y, w, h in case["platforms"][count:]:
            assert not (
                x < bounds["x"] + bounds["w"]
                and x + w > bounds["x"]
                and y < bounds["y"] + bounds["h"]
                and y + h > bounds["y"]
            )
        claims = [
            e
            for e in raw["workshop"]["events"]
            if e.get("type") == "chest_claim" and e.get("accepted")
        ]
        required = set(case["required_rewards"])
        assert (
            required <= {e["id"] for e in claims}
            and raw["workshop"]["coins"] >= case["expected_reward"]
            and raw["ok"]
            and raw["hp"] == 5
            and not raw["returns"]
        )
        f = max(e["frame"] for e in claims if e["id"] in required)
        probe = case["migration_probe"]
        nx, ny = probe["normal"]
        bx, by = probe["boundary"]
        half = 12 if nx else 18
        exits = [
            b["frame"]
            for a, b in zip(raw["frames"], raw["frames"][1:])
            if b["frame"] > f
            and (a["x"] - bx) * nx + (a["y"] - by) * ny < half
            and (b["x"] - bx) * nx + (b["y"] - by) * ny >= half
        ]
        assert exits
        results.append(
            dict(
                id=row["id"],
                routeId=row["routeId"],
                claimFrame=f,
                subsequentFullBodyExitFrame=exits[0],
                amount=raw["workshop"]["coins"],
                ownedCellsMatchHistorical110=True,
                archivePath=p["archivePath"],
                rawSha256=p["raw_output_sha256"],
            )
        )
    return dict(
        sourceCommit="c2e23fec3ec424a7b8e41552bbe2c4ed2a6c8afd",
        reportSha256=sha((folder / "reward-claim-validation.json").read_bytes()),
        archiveSha256=m["archive_sha256"],
        verifiedRawCases=results,
        scope="Later unmerged evidence on equivalent owned native Cells; NOT a declaration or certification retroactively added to historical 1.1.0 or current main.",
    )


def run(args):
    subprocess.run(
        ["git", "diff", "--exit-code", args.main_commit, "--", "modules/"],
        cwd=ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
    )
    z, manifest = checked_zip(args.zip, args.sha256)
    write(args.out / "dependency-checks.json", dependencies(z, manifest))
    catalog = json.loads(z.read("catalog.json"))
    old = {e["id"]: copy.deepcopy(e) for e in catalog["modules"]}
    main = read(ROOT / "modules/catalog.json")
    current = {e["id"]: e for e in main["modules"]}
    assert len(current) == len(main["modules"])
    if len(old) != len(catalog["modules"]):
        raise ValueError("duplicate_stable_id")
    diffs = []
    hashes = []
    documents = []
    for mid, e in old.items():
        e["_compiled"] = json.loads(z.read(e["compiled"]))
        docpath = "modules/" + mid + "/module.mapnote.json"
        doc = json.loads(z.read(docpath))
        assert sha(z.read(docpath)) == e["sourceSha256"]
        assert e["_compiled"]["source_sha256"] == e["sourceSha256"]
        assert e["_compiled"]["stable_id"] == mid
        assert doc["generationContract"]["contentVersion"] == e["contentVersion"]
        assert doc["id"] == mid
        e["_document"] = doc
        assert e["sceneOriginOffsetPixels"] == [-e["bounds"]["x"], -e["bounds"]["y"]]
        for route in e["routes"]:
            assert route["from"] in {p["id"] for p in e["ports"]} and route["to"] in {
                p["id"] for p in e["ports"]
            }
        if mid in current:
            c = current[mid]
            p = ROOT / c["file"]
            d = read(p)
            compiled = read(p.parent / "compiled-content.json")
            keys = sorted(
                k
                for k in set(compiled) | set(e["_compiled"])
                if k not in META and not same(compiled.get(k), e["_compiled"].get(k))
            )
            diffs.append(
                dict(
                    id=mid,
                    mainContentVersion=c["contentVersion"],
                    packageContentVersion=e["contentVersion"],
                    mainDocumentId=d["id"],
                    packageDocumentId=doc["id"],
                    sameDocumentBytes=sha(p.read_bytes()) == e["sourceSha256"],
                    changedNativeKeys=keys,
                    nativeCellsEquivalent=not keys,
                    mainBounds=d["generationContract"]["space"]["bounds"],
                    packageBounds=e["bounds"],
                    mainOffset=c["sceneOriginOffsetPixels"],
                    packageOffset=e["sceneOriginOffsetPixels"],
                    mainCompiledWorldBounds=compiled.get("world_bounds"),
                )
            )
    for mid, e in current.items():
        path = ROOT / e["file"]
        d = read(path)
        assert (
            sha(path.read_bytes()) == e["contentSha256"]
            and d["generationContract"]["contentVersion"] == e["contentVersion"]
        )
        m = read(path.parent / "godot-package.json")
        bad = [
            name
            for name, h in m["artifacts"].items()
            if not (path.parent / name).is_file()
            or sha((path.parent / name).read_bytes()) != h
        ]
        assert not bad, (mid, bad)
        assert sha(path.read_bytes()) == m["source"]["module_sha256"]
        compiled = read(path.parent / "compiled-content.json")
        assert compiled["source_sha256"] == e["contentSha256"]
        assert compiled["stable_id"] == mid
        hashes.append(dict(id=mid, artifactFiles=len(m["artifacts"]), hashesMatch=True))
        documents.append(str(path))
    # Reuse the actual current-main document validator for both baselines, without rebuilding catalog.
    with tempfile.TemporaryDirectory(prefix="readiness-documents-") as temporary:
        job = Path(temporary) / "document-paths.json"
        jobs = [dict(file=p, baseline="main") for p in documents]
        for mid in old:
            p = Path(temporary) / "modules" / mid / "module.mapnote.json"
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_bytes(z.read("modules/" + mid + "/module.mapnote.json"))
            jobs.append(dict(file=str(p), baseline="historical-1.1.0"))
        write(job, jobs)
        r = subprocess.run(
            ["node", str(ROOT / "tools/runtime_audit/check_documents.mjs"), str(job)],
            capture_output=True,
            text=True,
            check=True,
        )
        write(args.out / "document-validation.json", json.loads(r.stdout))
    # Existing legacy verifier may require an installed original runtime. Record limitations honestly.
    from pcg.migration.godot_package import verify_package, audit_cases

    legacy = []
    for mid in SAMPLES:
        folder = ROOT / "modules" / mid
        try:
            result = verify_package(folder, require_loaded=False)
            legacy.append(dict(id=mid, result=result))
        except (OSError, ValueError) as error:
            legacy.append(
                dict(
                    id=mid,
                    verifierError=str(error),
                    classification="Verifier requires original external host installation; not evidence of bad Module geometry.",
                )
            )
        try:
            cases = read(folder / "cases.json")
            cases = cases["cases"] if isinstance(cases, dict) else cases
            _, geometry = audit_cases(read(folder / "module.mapnote.json"), cases)
            legacy[-1]["directGeometryAudit"] = geometry
        except (OSError, ValueError) as error:
            legacy[-1]["directGeometryError"] = str(error)
    for mid in SAMPLES:
        target = args.out / "samples/package-1.1.0" / (mid + ".compiled.json")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(z.read(old[mid]["compiled"]))
    runtime = {
        n: manifest["files"][n]
        for n in manifest["files"]
        if n.startswith(("runtime/", "integration/"))
    }
    fp = sha(
        json.dumps(
            runtime, sort_keys=True, separators=(",", ":"), ensure_ascii=False
        ).encode()
    )
    reconstructed = False
    if args.authored_runtime_index:
        authored = read(args.authored_runtime_index)
        for name, item in authored["files"].items():
            assert sha(z.read("runtime/module_runtime/" + name)) == item["sha256"]
        authored_hashes = dict(runtime)
        authored_hashes["runtime/module_runtime/index.json"] = sha(
            args.authored_runtime_index.read_bytes()
        )
        reconstructed = (
            sha(
                json.dumps(
                    authored_hashes,
                    sort_keys=True,
                    separators=(",", ":"),
                    ensure_ascii=False,
                ).encode()
            )
            == manifest["runtimeFingerprint"]
        )
        assert reconstructed, "authoring_runtime_fingerprint_mismatch"
    reward = []
    for mid in TARGETS:
        e = old[mid]
        reward.append(
            dict(
                id=mid,
                inCurrentMainCatalog=mid in current,
                packageContentVersion=e["contentVersion"],
                sites=e["reward_sites"],
                requiredRewardsByRoute={
                    r["id"]: r.get("resourceProfile", {}).get("requiredRewards")
                    for r in e["routes"]
                },
                qualificationEvidence=e.get("qualificationEvidence"),
                abilitiesByRoute={
                    r["id"]: r["validation"]["availableAbilities"] for r in e["routes"]
                },
            )
        )
    diff = dict(
        mainCommit=args.main_commit,
        mainCatalogSchema=main["schema"],
        mainUpdateRef=main["updateRef"],
        mainCount=len(current),
        packageVersion=manifest["version"],
        packageSourceCommit=manifest["source"]["commit"],
        packageCount=len(old),
        intersection=len(current.keys() & old.keys()),
        mainOnly=sorted(current.keys() - old.keys()),
        packageOnly=sorted(old.keys() - current.keys()),
        differentContentVersions=sum(
            d["mainContentVersion"] != d["packageContentVersion"] for d in diffs
        ),
        nativeEquivalentCommon=sum(d["nativeCellsEquivalent"] for d in diffs),
        common=diffs,
    )
    write(args.out / "baseline-diff.json", diff)
    write(
        args.out / "delivery-scope.json",
        dict(
            packageVersion=manifest["version"],
            modules=len(old),
            explicitRoutes=sum(len(e["routes"]) for e in old.values()),
            mapReadyTrue=sum(e["mapReady"] is True for e in old.values()),
            mapReadyFalse=sum(e["mapReady"] is False for e in old.values()),
            verifiedScoped=sum(
                e["qualification"]["status"] == "verified_scoped" for e in old.values()
            ),
            configurations=[
                dict(
                    id=e["id"],
                    contentVersion=e["contentVersion"],
                    configurations=e["configurations"],
                    initialConfiguration=e["initialConfiguration"],
                    originalScope=e["qualification"].get("originalScope"),
                )
                for e in old.values()
            ],
            scope="Preserves declared witness scope. A generation candidate is not a physics-certified configuration; mapReady=false is not upgraded by this audit.",
        ),
    )
    write(args.out / "main-hash-checks.json", hashes)
    write(args.out / "legacy-verifier.json", legacy)
    write(args.out / "reward-baseline.json", reward)
    if args.later_evidence:
        write(
            args.out / "later-reward-evidence-check.json",
            later_claims(args.later_evidence, old),
        )
    summary = dict(
        zipSha256=args.sha256,
        zipBytes=args.zip.stat().st_size,
        verifiedPackageFiles=len(manifest["files"]),
        mainCatalogEntries=len(current),
        packageEntries=len(old),
        mainArtifactFilesVerified=sum(h["artifactFiles"] for h in hashes),
        uniqueIds=True,
        allSourceHashesAndVersionsMatch=True,
        mainSourceCommit=args.main_commit,
        manifest=manifest | {"files": "See original manifest inside checked ZIP"},
        publishedRuntimeGraphHash=fp,
        authoringRuntimeFingerprintRecomputed=reconstructed,
        reason="Published runtime index strips sourcePath provenance; manifest fingerprint describes authored runtime tree.",
        hostLocks={
            n: dict(
                id=v["id"],
                commit=v["commit"],
                files=len(v["files"]),
                sha256=sha(z.read(n)),
            )
            for n in ["runtime/host-lock.json", "runtime/host-lock-current-game.json"]
            for v in [json.loads(z.read(n))]
        },
    )
    write(args.out / "input-checks.json", summary)
    print(
        json.dumps({k: v for k, v in diff.items() if k != "common"}, ensure_ascii=False)
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip", type=Path, required=True)
    p.add_argument("--sha256", required=True)
    p.add_argument("--main-commit", required=True)
    p.add_argument("--later-evidence", type=Path)
    p.add_argument("--authored-runtime-index", type=Path)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    run(a)
