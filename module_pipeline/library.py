"""One current record per stable ID; atomic replacement and derived catalogs."""

import contextlib, copy, fcntl, hashlib, json, os, re, shutil, subprocess, tempfile
from pathlib import Path
from .bindings import evaluate

ROOT = Path(__file__).resolve().parents[1]
MODULES = ROOT / "modules"
SCHEMA = "map-edit/module-record/v1"
ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,159}$")


def read(p):
    return json.loads(Path(p).read_text())


def write(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    data = (
        json.dumps(value, ensure_ascii=False, sort_keys=False, indent=2) + "\n"
    ).encode()
    tmp = p.with_name(p.name + ".tmp")
    tmp.write_bytes(data)
    os.replace(tmp, p)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def normalize_numbers(v):
    if isinstance(v, float):
        rounded = round(v, 10)
        return int(rounded) if rounded.is_integer() else rounded
    if isinstance(v, list):
        return [normalize_numbers(x) for x in v]
    if isinstance(v, dict):
        return {k: normalize_numbers(x) for k, x in v.items()}
    return v


def digest(v):
    return hashlib.sha256(
        json.dumps(
            normalize_numbers(v),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode()
    ).hexdigest()


def safe_id(v):
    if not isinstance(v, str) or not ID.fullmatch(v):
        raise ValueError("invalid_stable_module_id:" + str(v))
    return v


def node(action, p, target=None):
    subprocess.run(
        [
            "node",
            str(ROOT / "tools/production/document.mjs"),
            action,
            str(p),
            *([str(target)] if target else []),
        ],
        check=True,
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
    )


def physical_data(doc):
    return evaluate(
        doc["generationContract"]["generation"]["parameters"]["runtimeBindings"], doc
    )


def compile_module(folder):
    folder = Path(folder)
    record = read(folder / "record.json")
    doc = read(folder / "module.mapnote.json")
    safe_id(record["id"])
    node("check", folder / "module.mapnote.json")
    if doc["id"] != record["id"]:
        raise ValueError("stable_id_document_mismatch:" + record["id"])
    data = physical_data(doc)
    bounds = doc["generationContract"]["space"]["bounds"]
    ports = doc["generationContract"]["ports"]
    stand = lambda p: (
        [p.get("stagingPosition", p["position"])[k] for k in ["x", "y"]]
        if isinstance(p.get("stagingPosition", p["position"]), dict)
        else p.get("stagingPosition", p["position"])
    )
    data.update(
        schema="pcg/compiled-module-content/v1",
        source_sha256=sha(folder / "module.mapnote.json"),
        stable_id=record["id"],
        ports=ports,
        world_bounds=[bounds[k] for k in ["x", "y", "w", "h"]],
        entry_port=evaluate(
            doc["generationContract"]["generation"]["parameters"]["nativeAnchors"][
                "entry"
            ],
            doc,
        ),
        exit_port=evaluate(
            doc["generationContract"]["generation"]["parameters"]["nativeAnchors"][
                "exit"
            ],
            doc,
        ),
    )
    write(folder / "compiled-content.json", data)
    loader = record["runtime"]["loader"]
    target = ROOT / loader
    if not target.is_file() or not target.resolve().is_relative_to(
        (ROOT / "runtime/module_runtime").resolve()
    ):
        raise ValueError("undeclared_runtime_loader:" + str(loader))
    relative = os.path.relpath(target, ROOT / "modules" / record["id"]).replace(
        os.sep, "/"
    )
    scene = (
        '[gd_scene load_steps=2 format=3]\n[ext_resource type="Script" path='
        + json.dumps(relative)
        + ' id="1"]\n[node name="Module" type="Node2D"]\nscript = ExtResource("1")\n'
    )
    (folder / "module.tscn").write_text(scene)
    manifest = dict(
        schema="map-edit/runtime-module/v1",
        stable_id=record["id"],
        contentVersion=doc["generationContract"]["contentVersion"],
        source=dict(module_sha256=sha(folder / "module.mapnote.json")),
        artifacts={
            "compiled-content.json": sha(folder / "compiled-content.json"),
            "module.tscn": sha(folder / "module.tscn"),
        },
        physicalSignature=digest(physical_data(doc)),
    )
    write(folder / "godot-package.json", manifest)
    node("thumbnail", folder / "module.mapnote.json", folder / "thumbnail.svg")
    record["source"] = dict(
        kind="module",
        file="module.mapnote.json",
        sha256=sha(folder / "module.mapnote.json"),
        contentVersion=doc["generationContract"]["contentVersion"],
    )
    record["runtime"]["thumbnailSha256"] = sha(folder / "thumbnail.svg")
    record["runtime"]["physicalSignature"] = manifest["physicalSignature"]
    record["runtime"]["compiledSha256"] = sha(folder / "compiled-content.json")
    write(folder / "record.json", record)
    return record


def records():
    result = []
    for folder in sorted(MODULES.iterdir()):
        if not folder.is_dir():
            continue
        p = folder / "record.json"
        if not p.exists():
            raise ValueError("unregistered_module_directory:" + folder.name)
        r = read(p)
        if r.get("schema") != SCHEMA or r.get("id") != folder.name:
            raise ValueError("invalid_module_record:" + str(p))
        safe_id(r["id"])
        if folder.is_symlink() or r.get("lifecycle") not in [
            "retained",
            "development",
            "withdrawn",
        ]:
            raise ValueError("invalid_current_lifecycle_or_symlink:" + r["id"])
        if r["lifecycle"] == "withdrawn" and any(
            p.name != "record.json" for p in folder.iterdir()
        ):
            raise ValueError("withdrawn_module_payload_must_be_removed:" + r["id"])
        if r.get("source") and r["source"].get("file") != {
            "module": "module.mapnote.json",
            "design": "design.json",
        }.get(r["source"].get("kind")):
            raise ValueError("invalid_current_source_path:" + r["id"])
        result.append((folder, r))
    return result


def build_catalog(write_index=True):
    from .package import runtime_fingerprint

    fingerprint = runtime_fingerprint()
    modules = []
    designs = []
    retired = []
    for folder, r in records():
        source = r.get("source")
        summary = dict(
            id=r["id"],
            title=r["title"],
            reviewId=r.get("reviewId"),
            lifecycle=r["lifecycle"],
            review=r["review"],
            record=f'./modules/{r["id"]}/record.json',
            recordSha256=sha(folder / "record.json"),
        )
        if r["lifecycle"] == "withdrawn":
            retired.append(
                summary
                | dict(
                    reason=r["withdrawal"]["reason"],
                    replacement=r["withdrawal"].get("replacement"),
                )
            )
            continue
        if (
            not source
            or not (folder / source["file"]).is_file()
            or sha(folder / source["file"]) != source["sha256"]
        ):
            raise ValueError("missing_or_changed_source:" + r["id"])
        if source["kind"] == "design":
            design = read(folder / source["file"])
            if (
                design.get("id") != r["id"]
                or design.get("designVersion") != source["contentVersion"]
            ):
                raise ValueError(
                    "current_design_identity_or_version_mismatch:" + r["id"]
                )
            designs.append(
                summary
                | dict(
                    file=f'./modules/{r["id"]}/{source["file"]}',
                    contentSha256=source["sha256"],
                    contentVersion=source["contentVersion"],
                    thumbnail=f'./modules/{r["id"]}/thumbnail.svg',
                    deliveryStatus="not_implemented",
                )
            )
            continue
        doc = read(folder / source["file"])
        g = doc["generationContract"]
        if doc["id"] != r["id"] or g["contentVersion"] != source["contentVersion"]:
            raise ValueError("current_source_version_mismatch:" + r["id"])
        node("check", folder / source["file"])
        data = read(folder / "compiled-content.json")
        expected = physical_data(doc)
        bounds = g["space"]["bounds"]
        anchors = g["generation"]["parameters"]["nativeAnchors"]
        metadata = dict(
            schema="pcg/compiled-module-content/v1",
            source_sha256=source["sha256"],
            stable_id=r["id"],
            ports=g["ports"],
            world_bounds=[bounds[k] for k in ["x", "y", "w", "h"]],
            entry_port=evaluate(anchors["entry"], doc),
            exit_port=evaluate(anchors["exit"], doc),
        )
        if data != expected | metadata:
            raise ValueError("stale_compiled_content:" + r["id"])
        manifest = read(folder / "godot-package.json")
        if (
            manifest.get("contentVersion") != source["contentVersion"]
            or manifest.get("source", {}).get("module_sha256") != source["sha256"]
        ):
            raise ValueError("runtime_manifest_source_mismatch:" + r["id"])
        for name, h in manifest["artifacts"].items():
            if not (folder / name).is_file() or sha(folder / name) != h:
                raise ValueError(
                    "runtime_artifact_hash_mismatch:" + r["id"] + ":" + name
                )
        if sha(folder / "thumbnail.svg") != r["runtime"].get("thumbnailSha256"):
            raise ValueError("stale_module_thumbnail:" + r["id"])
        if sha(folder / "compiled-content.json") != r["runtime"]["compiledSha256"]:
            raise ValueError("stale_compiled_hash:" + r["id"])
        q = r.get("qualification", {})
        qualified = q.get("status") == "verified_scoped" and q.get(
            "physicalSignature"
        ) == digest(expected)
        runtime_status = r["runtime"].get("deliveryStatus", "pending")
        portable = r["runtime"].get("portableValidation") or {}
        if runtime_status == "ready" and (
            portable.get("runtimeFingerprint") != fingerprint
            or portable.get("sourceSha256") != source["sha256"]
        ):
            runtime_status = "pending_portable_validation"
        modules.append(
            summary
            | dict(
                moduleId=doc["id"],
                aliases=r.get("aliases", []),
                contentVersion=g["contentVersion"],
                file=f'./modules/{r["id"]}/module.mapnote.json',
                thumbnail=f'./modules/{r["id"]}/thumbnail.svg',
                contentSha256=source["sha256"],
                portCount=len(g["ports"]),
                category=r.get("region", "通用"),
                sourceType="reviewed_current",
                capabilityRequirements=doc["capabilityRequirements"],
                difficulty=doc["difficulty"],
                humanReview=r["review"]["decision"],
                technicalStatus="passed_scoped" if qualified else "needs_validation",
                mapReady=False,
                deliveryStatus=runtime_status,
                foundation=g["foundation"],
                sceneOriginOffsetPixels=[
                    -g["space"]["bounds"]["x"] or 0,
                    -g["space"]["bounds"]["y"] or 0,
                ],
                ports=g["ports"],
                routes=g["routes"],
                cornerConfigurationReceipts=[],
                portConfigurations=r["runtime"].get("configurations", []),
                requiredNativeProfile=r["runtime"].get("hostProfile"),
                unresolved=r.get("gaps", []),
            )
        )
    value = dict(
        schema="map-notes/module-archive/v1",
        foundationVersion="1.0",
        foundationSpecificationVersion="1.2",
        updateRef="main",
        recordSchema=SCHEMA,
        modules=modules,
        designs=designs,
        withdrawn=retired,
        counts=dict(
            retained=len(modules) + len(designs),
            implemented=len(modules),
            developmentDesigns=len(designs),
            withdrawn=len(retired),
            deliverable=sum(v["deliveryStatus"] == "ready" for v in modules),
        ),
    )
    if write_index:
        write(MODULES / "catalog.json", value)
    return value


@contextlib.contextmanager
def transaction_lock():
    p = ROOT / "build/module-production.lock"
    p.parent.mkdir(exist_ok=True)
    with p.open("a+") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        yield


def transaction(change):
    """Compile and validate the entire next index before one Linux directory exchange.

    No reader can observe a half-replaced source/compiled/thumbnail/evidence set.
    The old tree remains intact until the exchange; exceptions leave it unchanged.
    """
    import ctypes

    global MODULES
    with transaction_lock():
        original = MODULES
        stage = Path(tempfile.mkdtemp(prefix="module-transaction-", dir=ROOT / "build"))
        next_tree = stage / "next"
        try:
            shutil.copytree(original, next_tree)
            MODULES = next_tree
            result = change()
            build_catalog()
            MODULES = original
            libc = ctypes.CDLL(None, use_errno=True)
            if not hasattr(libc, "renameat2"):
                raise RuntimeError("atomic_directory_exchange_requires_Linux_renameat2")
            if (
                libc.renameat2(
                    -100, os.fsencode(original), -100, os.fsencode(next_tree), 2
                )
                != 0
            ):
                code = ctypes.get_errno()
                raise OSError(code, os.strerror(code))
            return result
        finally:
            MODULES = original
            shutil.rmtree(stage)


def preserve_current(folder):
    """Git for committed state; an immutable content-addressed archive otherwise."""
    folder = Path(folder)
    identifier = folder.name
    committed = subprocess.run(
        ["git", "show", f"HEAD:modules/{identifier}/record.json"],
        cwd=ROOT,
        capture_output=True,
    )
    dirty = subprocess.run(
        [
            "git",
            "-c",
            "status.renames=false",
            "status",
            "--porcelain",
            "--",
            f"modules/{identifier}",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    if (
        committed.returncode == 0
        and committed.stdout == (folder / "record.json").read_bytes()
        and not dirty.stdout
    ):
        return dict(
            commit=subprocess.check_output(
                ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
            ).strip(),
            path=f"modules/{identifier}",
        )
    from .package import archive

    files = {
        p.relative_to(folder).as_posix(): sha(p)
        for p in folder.rglob("*")
        if p.is_file()
    }
    fingerprint = digest(files)
    out = ROOT / "archives/modules" / identifier / (fingerprint + ".zip")
    if not out.exists():
        archive(folder, out)
    import zipfile

    try:
        with zipfile.ZipFile(out) as z:
            if set(z.namelist()) != set(files) or any(
                hashlib.sha256(z.read(name)).hexdigest() != h
                for name, h in files.items()
            ):
                raise ValueError("immutable_module_archive_mismatch")
    except zipfile.BadZipFile as error:
        raise ValueError("immutable_module_archive_corrupt") from error
    return dict(file=out.relative_to(ROOT).as_posix(), sha256=sha(out))


def equivalent_runtime_revision(before, after):
    def contract(doc):
        value = copy.deepcopy(doc["generationContract"])
        value.pop("contentVersion", None)
        value.pop("visualization", None)
        if value.get("staticChecks"):
            value["staticChecks"].pop("contentVersion", None)
        return value

    return (
        before["objects"] == after["objects"]
        and before["capabilityRequirements"] == after["capabilityRequirements"]
        and before["difficulty"] == after["difficulty"]
        and contract(before) == contract(after)
    )


def replace_source(identifier, source):
    identifier = safe_id(identifier)
    source = Path(source).resolve()

    def change():
        folder = MODULES / identifier
        r = read(folder / "record.json")
        if r["lifecycle"] == "withdrawn":
            raise ValueError(
                "withdrawn_module_requires_new_identity_or_explicit_reviewed_reactivation"
            )
        kind = r["source"]["kind"]
        raw = read(source)
        old_record = copy.deepcopy(r)
        old_document = (
            read(folder / "module.mapnote.json") if kind == "module" else None
        )
        if raw.get("id") != identifier:
            if (
                raw.get("source", {}).get("moduleId") == identifier
                and raw.get("intent", {}).get("operation") == "modify_existing"
            ):
                raw["id"] = identifier
            else:
                raise ValueError("stable_id_document_mismatch")
        for key in [
            "baselineObjects",
            "baselineDifficulty",
            "baselineCapabilityRequirements",
        ]:
            raw.pop(key, None)
        if kind == "module":
            from .bindings import check_revision_bindings

            check_revision_bindings(read(folder / "module.mapnote.json"), raw)
        previous = preserve_current(folder)
        r.setdefault("history", {})["previousCurrent"] = previous
        if kind == "design" and raw.get("schema") == "pcg/module-design/v1":
            from .design import seal, render

            raw = seal(raw)
            write(folder / "design.json", raw)
            render(folder)
            r["source"].update(
                sha256=sha(folder / "design.json"), contentVersion=raw["designVersion"]
            )
            r["review"].update(
                decision="PENDING",
                implementationApproval="not_implemented",
                designVersion=raw["designVersion"],
            )
            write(folder / "record.json", r)
            return identifier
        if raw.get("id") != identifier:
            raise ValueError("stable_id_document_mismatch")
        write(folder / "module.mapnote.json", raw)
        node("refresh", folder / "module.mapnote.json")
        r["review"]["implementationApproval"] = "needs_review"
        r["qualification"] = dict(status="needs_requalification")
        r["runtime"].update(deliveryStatus="pending", portableValidation=None)
        # Existing receipts remain Git history; no stale certificate survives replacement.
        shutil.rmtree(folder / "validation/qualification", ignore_errors=True)
        if (folder / "validation/cases.json").exists():
            origin = (
                read(folder / "validation/origin.json")
                if (folder / "validation/origin.json").exists()
                else {}
            )
            origin.update(
                status="input_template_requires_current_source_check",
                previousSourceSha256=old_record["source"]["sha256"],
                note="Policy inputs retained for revision; not evidence for changed geometry. The native qualifier checks exact compiled Cell equality before admission.",
            )
            write(folder / "validation/origin.json", origin)
        if kind == "design":
            r["runtime"][
                "loader"
            ] = "runtime/module_runtime/module_loader_v3-1d72f57d63dd.gd"
            (folder / "design.json").unlink()
            r["lifecycle"] = "development"
        write(folder / "record.json", r)
        compile_module(folder)
        if (
            old_document is not None
            and old_record.get("qualification", {}).get("status") == "verified_scoped"
            and equivalent_runtime_revision(
                old_document, read(folder / "module.mapnote.json")
            )
        ):
            current = read(folder / "record.json")
            current["qualification"] = old_record["qualification"]
            current["qualification"]["metadataEquivalence"] = dict(
                previousContentVersion=old_record["source"]["contentVersion"],
                previousSourceSha256=old_record["source"]["sha256"],
                currentContentVersion=current["source"]["contentVersion"],
                currentSourceSha256=current["source"]["sha256"],
                rule="Exact objects, capabilities, difficulty and all runtime/interface contract fields unchanged; only document/provenance metadata normalized.",
            )
            write(folder / "record.json", current)
        return identifier

    return transaction(change)


def add(
    source,
    identifier=None,
    loader="runtime/module_runtime/module_loader_v3-1d72f57d63dd.gd",
    thumbnail=None,
):
    import uuid

    identifier = safe_id(identifier or "module-" + str(uuid.uuid4()))
    source = Path(source).resolve()

    def change():
        folder = MODULES / identifier
        if folder.exists():
            raise ValueError("stable_id_already_allocated:" + identifier)
        raw = read(source)
        folder.mkdir()
        design = raw.get("schema") == "pcg/module-design/v1"
        r = dict(
            schema=SCHEMA,
            id=identifier,
            title=raw.get("title", identifier),
            region=raw.get("region", "通用"),
            lifecycle="development",
            review=dict(
                decision="PENDING",
                implementationApproval="not_implemented" if design else "needs_review",
            ),
            source={},
            qualification=dict(
                status="not_implemented" if design else "needs_requalification"
            ),
            runtime=dict(
                loader=loader,
                deliveryStatus="not_implemented" if design else "pending",
                hostProfile="gunman-rush-native-12f6cb0",
                configurations=[],
            ),
            history={},
            gaps=["Await exact-version review and scoped native qualification."],
        )
        if design:
            if raw.get("id") != identifier:
                raw["id"] = identifier
            from .design import seal, render

            raw = seal(raw)
            write(folder / "design.json", raw)
            r["source"] = dict(
                kind="design",
                file="design.json",
                sha256=sha(folder / "design.json"),
                contentVersion=raw.get("designVersion", "UNKNOWN"),
            )
            render(folder)
            write(folder / "record.json", r)
        else:
            raw["id"] = identifier
            raw["intent"] = dict(
                operation="new_module", notes="Current stable-ID development source."
            )
            raw.setdefault("source", {}).update(
                repository="zhipijun1996/map-edit",
                path=f"modules/{identifier}/module.mapnote.json",
                moduleId=identifier,
            )
            raw["source"].setdefault(
                "integration",
                dict(
                    isIntegrated=False,
                    reason="Development; runtime and Map qualification pending.",
                ),
            )
            write(folder / "module.mapnote.json", raw)
            node("refresh", folder / "module.mapnote.json")
            write(folder / "record.json", r)
            compile_module(folder)
        return identifier

    return transaction(change)


def withdraw(identifier, reason, replacement=None):
    identifier = safe_id(identifier)
    if not reason:
        raise ValueError("withdrawal_reason_required")

    def change():
        folder = MODULES / identifier
        r = read(folder / "record.json")
        if replacement:
            safe_id(replacement)
            other = read(MODULES / replacement / "record.json")
            if other["lifecycle"] == "withdrawn" or replacement == identifier:
                raise ValueError("invalid_replacement")
        if r["lifecycle"] == "withdrawn":
            return identifier
        recovery = preserve_current(folder)
        r.setdefault("history", {})[
            "withdrawalArchive" if "file" in recovery else "withdrawalSource"
        ] = recovery
        r["lifecycle"] = "withdrawn"
        r["withdrawal"] = dict(reason=reason, replacement=replacement)
        r["source"] = None
        r["runtime"] = dict(deliveryStatus="withdrawn")
        r["qualification"] = dict(status="withdrawn")
        for p in folder.iterdir():
            if p.is_dir():
                shutil.rmtree(p)
            else:
                p.unlink()
        write(folder / "record.json", r)
        return identifier

    return transaction(change)
