"""Deterministic, versioned distribution from the one current source library."""

import hashlib, json, re, shutil, subprocess, zipfile
from pathlib import Path
from . import library as l
from . import exports

FILES = (
    "module.mapnote.json",
    "compiled-content.json",
    "module.tscn",
    "godot-package.json",
    "thumbnail.svg",
)
VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[a-zA-Z0-9.-]+)?$")


def runtime_fingerprint():
    return l.digest(
        {
            p.relative_to(l.ROOT).as_posix(): l.sha(p)
            for parent in ["runtime", "integration"]
            for p in sorted((l.ROOT / parent).rglob("*"))
            if p.is_file() and "__pycache__" not in p.parts
        }
    )


def eligible(r):
    return (
        r["lifecycle"] != "withdrawn"
        and r.get("source", {}).get("kind") == "module"
        and r["review"].get("decision") == "KEEP"
        and r["review"].get("implementationApproval") == "approved"
        and r.get("qualification", {}).get("status") == "verified_scoped"
        and r["qualification"].get("physicalSignature")
        == r["runtime"].get("physicalSignature")
    )


SOURCE_INPUTS = [
    "modules",
    "runtime",
    "integration",
    "module_pipeline",
    "tools/production",
    "module-contract.js",
    "module-contract-render.js",
    "docs/module-package-consumers.md",
]


def assert_source_commit(commit):
    if (
        subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=l.ROOT, text=True
        ).strip()
        != commit
    ):
        raise ValueError("source_commit_changed_during_build")
    status = (
        subprocess.check_output(
            [
                "git",
                "-c",
                "status.renames=false",
                "status",
                "--porcelain",
                "-z",
                "--untracked-files=all",
                "--",
                *SOURCE_INPUTS,
            ],
            cwd=l.ROOT,
        )
        .decode()
        .split("\0")
    )
    for entry in status:
        if not entry:
            continue
        name = entry[3:]
        if name == "modules/catalog.json":
            continue
        if (
            name.startswith("modules/")
            and name.endswith("/record.json")
            and entry[:2] in [" M", "M ", "MM"]
        ):
            previous = subprocess.run(
                ["git", "show", commit + ":" + name], cwd=l.ROOT, capture_output=True
            )
            if previous.returncode == 0:
                a = json.loads(previous.stdout)
                b = l.read(l.ROOT / name)
                for record in [a, b]:
                    record.get("runtime", {}).pop("deliveryStatus", None)
                    record.get("runtime", {}).pop("portableValidation", None)
                if a == b:
                    continue
        raise ValueError(
            "commit_current_production_inputs_before_versioned_build:" + name
        )


def stage(target, version, source_commit, ready_only=True, strict_source=False):
    with l.transaction_lock():
        if strict_source:
            assert_source_commit(source_commit)
        return _stage(target, version, source_commit, ready_only)


def _stage(target, version, source_commit, ready_only=True):
    target = Path(target)
    target.mkdir(parents=True, exist_ok=False)
    index = l.build_catalog()
    entries = []
    excluded = []
    fingerprint = runtime_fingerprint()
    for folder, r in l.records():
        if (
            not eligible(r)
            or ready_only
            and (
                r["runtime"]["deliveryStatus"] != "ready"
                or r["runtime"].get("portableValidation", {}).get("runtimeFingerprint")
                != fingerprint
                or r["runtime"].get("portableValidation", {}).get("sourceSha256")
                != r["source"]["sha256"]
            )
        ):
            if r["lifecycle"] != "withdrawn":
                excluded.append(
                    dict(
                        id=r["id"],
                        reason=r.get("gaps")
                        or [
                            "Current source lacks matching review, physical or portable-runtime qualification."
                        ],
                    )
                )
            continue
        dest = target / "modules" / r["id"]
        dest.mkdir(parents=True)
        for name in FILES:
            shutil.copyfile(folder / name, dest / name)
        doc = l.read(folder / "module.mapnote.json")
        g = doc["generationContract"]
        b = g["space"]["bounds"]
        block = g["foundation"]["blockSize"]
        ports = g["ports"]
        compiled = l.read(folder / "compiled-content.json")
        projected = exports.project_routes(folder, doc, r, compiled)
        routes = []
        for rid in r["qualification"]["routeIds"]:
            route = next((v for v in projected if v["id"] == rid), None)
            if route is None:
                raise ValueError("qualified_route_missing:" + r["id"] + ":" + rid)
            routes.append(
                route
                | dict(
                    validation=dict(
                        status="passed_scoped",
                        kind="original_native_route_qualification",
                        physicalSignature=r["qualification"]["physicalSignature"],
                        originalReportSha256=r["qualification"]["originalReportSha256"],
                        availableAbilities=r["qualification"]
                        .get("availableAbilitiesByRoute", {})
                        .get(rid, route.get("requiredAbilities", [])),
                        testNeighborFixtures=r["qualification"]
                        .get("testNeighborFixtures", {})
                        .get(rid, []),
                        scope="Independently initialized local route; arbitrary seams, alternate configurations, minimal capabilities and chaining remain UNKNOWN.",
                    )
                )
            )
        entry = dict(
            id=r["id"],
            aliases=r.get("aliases", []),
            title=r["title"],
            contentVersion=r["source"]["contentVersion"],
            sourceSha256=r["source"]["sha256"],
            region=r.get("region"),
            purpose=exports.purpose(doc, folder),
            reward_sites=compiled.get("reward_sites", []),
            entryPortIds=exports.entry_port_ids(ports, routes),
            blockSize=block,
            sizeBlocks=[
                g["foundation"]["widthBlocks"],
                g["foundation"]["heightBlocks"],
            ],
            bounds=b,
            sceneOriginOffsetPixels=[-b["x"] or 0, -b["y"] or 0],
            ports=ports,
            routes=routes,
            capabilityRequirements=doc["capabilityRequirements"],
            configurations=[
                {k: v for k, v in c.items() if k != "mirrorX"}
                for c in r["runtime"]["configurations"]
            ],
            initialConfiguration=dict(
                nativeTuning=l.read(folder / "compiled-content.json").get(
                    "original_tuning_profile"
                ),
                nativeFixture=l.read(folder / "compiled-content.json").get(
                    "original_fixture_profile"
                ),
                requirementsByRoute={
                    v["id"]: v.get("initialConditions", {}) for v in routes
                },
            ),
            scene=f'modules/{r["id"]}/module.tscn',
            compiled=f'modules/{r["id"]}/compiled-content.json',
            hostProfile=r["runtime"]["hostProfile"],
            requiredServices=["policy", "lifetime", "wallet"]
            + (
                ["meta"]
                if any(
                    v.get("kind") == "note"
                    for v in l.read(folder / "compiled-content.json").get(
                        "original_pickups", []
                    )
                )
                or l.read(folder / "compiled-content.json").get(
                    "original_region_chests"
                )
                else []
            )
            + (
                ["region_state"]
                if l.read(folder / "compiled-content.json").get(
                    "original_region_chests"
                )
                else []
            ),
            mapReady=False,
            qualification=r["qualification"],
            qualificationEvidence=r.get("history", {}).get(
                "qualificationEvidence",
                r.get("history", {}).get("currentQualificationEvidence"),
            ),
            actorBody=dict(
                shape=g["space"]["actorBody"]["shape"],
                size=g["space"]["actorBody"]["size"],
                hostScene="res://scenes/player/player.tscn",
            ),
            portableValidation=r["runtime"].get("portableValidation"),
        )
        entries.append(entry)
    if not entries:
        raise ValueError("empty_delivery_is_forbidden")
    for parent in ["runtime", "integration"]:
        shutil.copytree(
            l.ROOT / parent,
            target / parent,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    # Internal migration provenance is Git-addressed in the source records; runtime needs only the resolved graph.
    old = l.read(target / "runtime/module_runtime/index.json")
    l.write(
        target / "runtime/module_runtime/index.json",
        dict(
            schema=old["schema"],
            files={
                n: {k: v for k, v in d.items() if k != "sourcePath"}
                for n, d in old["files"].items()
            },
            hostResourceReferences=old["hostResourceReferences"],
        ),
    )
    for name in [
        "portable-runtime.json",
        "current-game-api.json",
        "map-gen-interface.json",
        "reward-claim-validation.json",
    ]:
        evidence = l.ROOT / "evidence/module-production" / name
        if evidence.exists():
            (target / "evidence/module-production").mkdir(parents=True, exist_ok=True)
            shutil.copyfile(evidence, target / "evidence/module-production" / name)
    readme = l.ROOT / "docs/module-package-consumers.md"
    if readme.exists():
        shutil.copyfile(readme, target / "README.md")
    l.write(target / "reward-association-gaps.json", exports.reward_gaps(entries))
    l.write(
        target / "catalog.json",
        dict(
            schema="map-edit/delivery-catalog/v1",
            packageVersion=version,
            modules=entries,
            excluded=excluded,
            counts=dict(delivered=len(entries), excluded=len(excluded)),
            configurationsPolicy="configurations describe original certification witnesses, not generation eligibility. map-gen mirrors complete content/Ports/routes, selects any Port subset, adds gear closures to unused Ports and checks remaining routes. New placements remain UNKNOWN until checked; original certification scope is unchanged.",
        ),
    )
    l.write(
        target / "manifest.json",
        dict(
            schema="map-edit/module-package/v1",
            version=version,
            source=dict(
                repository="https://github.com/zhipijun1996/map-edit",
                commit=source_commit,
                recordSchema=l.SCHEMA,
            ),
            foundation=dict(
                specificationVersion="1.2",
                modelVersion="1.0",
                generationContractVersion=2,
            ),
            runtimeFingerprint=fingerprint,
            requiredProjectSettings={
                "physics/common/physics_ticks_per_second": 60,
                "rendering/renderer/rendering_method": "gl_compatibility",
            },
            hostDependency="runtime/host-lock.json",
            hostProfiles=[
                dict(
                    file="runtime/host-lock.json",
                    qualification="native_scoped_routes_and_portable_runtime",
                ),
                dict(
                    file="runtime/host-lock-current-game.json",
                    qualification="current_game_api_integration_only; full route requalification pending",
                ),
            ],
            modules=len(entries),
            files={
                p.relative_to(target).as_posix(): l.sha(p)
                for p in sorted(target.rglob("*"))
                if p.is_file()
            },
        ),
    )
    verify(target)
    return entries, excluded


def verify(target):
    target = Path(target)
    manifest = l.read(target / "manifest.json")
    expected = manifest["files"]
    actual = {
        p.relative_to(target).as_posix() for p in target.rglob("*") if p.is_file()
    } - {"manifest.json"}
    # Godot writes import/UID caches beside existing resources after installation.
    actual = {
        n
        for n in actual
        if not (
            n.endswith(".uid")
            and n[:-4] in expected
            or n.endswith(".import")
            and n[:-7] in expected
        )
    }
    if actual != set(expected):
        raise ValueError(
            "package_file_set_mismatch:" + str(sorted(actual ^ set(expected)))
        )
    for rel, digest in expected.items():
        if Path(rel).is_absolute() or ".." in Path(rel).parts:
            raise ValueError("unsafe_package_path:" + rel)
        if l.sha(target / rel) != digest:
            raise ValueError("package_checksum_mismatch:" + rel)
    ids = set()
    lock = l.read(target / "runtime/host-lock.json")
    host = set(lock["files"])
    for entry in l.read(target / "catalog.json")["modules"]:
        if entry["id"] in ids:
            raise ValueError("duplicate_delivery_id:" + entry["id"])
        ids.add(entry["id"])
        compiled = l.read(target / "modules" / entry["id"] / "compiled-content.json")
        if any(
            k in entry
            for k in [
                "mirrorX",
                "allow_mirror_x",
                "allowedTransforms",
                "closures",
                "relocations",
            ]
        ):
            raise ValueError("obsolete_generation_gate:" + entry["id"])
        if entry.get("reward_sites") != compiled.get("reward_sites", []):
            raise ValueError("incomplete_reward_sites:" + entry["id"])
        rewards = entry["reward_sites"]
        reward_ids = [r["id"] for r in rewards]
        if len(reward_ids) != len(set(reward_ids)) or any(
            not all(k in r for k in ["id", "position", "region", "amount"])
            for r in rewards
        ):
            raise ValueError("invalid_reward_sites:" + entry["id"])
        for route in entry["routes"]:
            required = route.get("resourceProfile", {}).get("requiredRewards", [])
            if (
                not isinstance(required, list)
                or len(required) != len(set(required))
                or not set(required) <= set(reward_ids)
            ):
                raise ValueError(
                    "unknown_required_reward:" + entry["id"] + ":" + route["id"]
                )
        if entry.get("entryPortIds") != exports.entry_port_ids(
            entry["ports"], entry["routes"]
        ):
            raise ValueError("invalid_entry_ports:" + entry["id"])
        d = l.read(target / "modules" / entry["id"] / "module.mapnote.json")
        m = l.read(target / "modules" / entry["id"] / "godot-package.json")
        if (
            d["id"] != entry["id"]
            or d["generationContract"]["contentVersion"] != entry["contentVersion"]
            or m["contentVersion"] != entry["contentVersion"]
        ):
            raise ValueError("delivery_version_mismatch:" + entry["id"])
        if (
            l.sha(target / "modules" / entry["id"] / "module.mapnote.json")
            != entry["sourceSha256"]
        ):
            raise ValueError("delivery_source_mismatch:" + entry["id"])
    catalog = l.read(target / "catalog.json")
    if l.read(target / "reward-association-gaps.json") != exports.reward_gaps(
        catalog["modules"]
    ):
        raise ValueError("stale_reward_association_audit")
    imports = re.compile(
        r"(?:\bextends\s*|\b(?:preload|load)\s*\(\s*)[\"']([^\"']+)[\"']"
    )
    resources = re.compile(r"[\"']res://([^\"']+)[\"']")
    for path in (
        list((target / "runtime/module_runtime").glob("*.gd"))
        + list((target / "modules").glob("*/module.tscn"))
        + list((target / "integration").glob("*.gd"))
        + list((target / "integration").glob("*.tscn"))
    ):
        raw = path.read_text()
        refs = imports.findall(raw)
        if path.suffix == ".tscn":
            refs += re.findall(r'path="([^"\n]+)"', raw)
        for ref in refs:
            if ref.startswith("res://"):
                if ref[6:] not in host and not any(h.startswith(ref[6:]) for h in host):
                    raise ValueError("undeclared_host_dependency:" + ref)
            elif ref.startswith(("http:", "https:", "/")):
                raise ValueError("nonportable_runtime_dependency:" + ref)
            else:
                resolved = (path.parent / ref).resolve()
                if (
                    not resolved.is_relative_to(target.resolve())
                    or not resolved.exists()
                ):
                    raise ValueError(
                        "missing_or_escaping_dependency:"
                        + str(path.relative_to(target))
                        + ":"
                        + ref
                    )
        for ref in resources.findall(raw):
            if ref not in host and not any(h.startswith(ref) for h in host):
                raise ValueError("undeclared_host_resource:" + ref)
    runtime_index = l.read(target / "runtime/module_runtime/index.json")
    for name, entry in runtime_index["files"].items():
        file = target / "runtime/module_runtime" / name
        if not file.is_file() or l.sha(file) != entry["sha256"]:
            raise ValueError("runtime_graph_hash_mismatch:" + name)
    return dict(modules=len(ids), files=len(expected))


def archive(folder, out):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        raise ValueError("immutable_package_version_exists:" + str(out))
    tmp = out.with_suffix(".tmp")
    try:
        with zipfile.ZipFile(
            tmp, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as z:
            for p in sorted(Path(folder).rglob("*")):
                if p.is_file():
                    info = zipfile.ZipInfo(
                        p.relative_to(folder).as_posix(),
                        date_time=(2026, 1, 1, 0, 0, 0),
                    )
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    z.writestr(info, p.read_bytes())
        tmp.replace(out)
    finally:
        if tmp.exists():
            tmp.unlink()
    return l.sha(out)
