import argparse, json, shutil, subprocess, sys, tempfile
from pathlib import Path
from . import library as l, package


def main():
    p = argparse.ArgumentParser(
        description="One current Module source library; atomic edits and versioned runtime delivery."
    )
    sub = p.add_subparsers(dest="command", required=True)
    for command in ["index", "check"]:
        sub.add_parser(command)
    add = sub.add_parser("add")
    add.add_argument("source", type=Path)
    add.add_argument("--id")
    add.add_argument("--thumbnail", type=Path)
    add.add_argument(
        "--loader", default="runtime/module_runtime/module_loader_v3-1d72f57d63dd.gd"
    )
    update = sub.add_parser("update")
    update.add_argument("id")
    update.add_argument("source", type=Path)
    withdraw = sub.add_parser("withdraw")
    withdraw.add_argument("id")
    withdraw.add_argument("--reason", required=True)
    withdraw.add_argument("--replacement")
    review = sub.add_parser("review")
    review.add_argument("id")
    review.add_argument("--version", required=True)
    review.add_argument("--decision", choices=["KEEP", "CHANGE"], required=True)
    review.add_argument("--note", required=True)
    qualify = sub.add_parser("qualify")
    qualify.add_argument("id")
    qualify.add_argument("--evidence", required=True, type=Path)
    verify = sub.add_parser("verify-package")
    verify.add_argument("folder", type=Path)
    for command in ["validate-portable", "build"]:
        b = sub.add_parser(command)
        b.add_argument("--godot")
        b.add_argument("--host-source", type=Path)
        b.add_argument("--work", type=Path)
        if command == "build":
            b.add_argument("--version", required=True)
            b.add_argument("--out", type=Path, default=l.ROOT / "releases")
            b.add_argument("--revalidate", action="store_true")
    args = p.parse_args()
    if args.command in ["index", "check"]:
        with l.transaction_lock():
            expected = l.build_catalog(write_index=args.command == "index")
        if args.command == "check" and expected != l.read(l.MODULES / "catalog.json"):
            raise ValueError("stale_catalog_run_module_pipeline_index")
        result = expected["counts"]
    elif args.command == "add":
        result = dict(id=l.add(args.source, args.id, args.loader, args.thumbnail))
    elif args.command == "update":
        result = dict(id=l.replace_source(args.id, args.source))
    elif args.command == "withdraw":
        result = dict(id=l.withdraw(args.id, args.reason, args.replacement))
    elif args.command == "review":

        def change():
            folder = l.MODULES / l.safe_id(args.id)
            r = l.read(folder / "record.json")
            if not r.get("source") or r["source"]["contentVersion"] != args.version:
                raise ValueError("review_must_bind_current_content_version")
            r["review"].update(
                decision=args.decision,
                implementationApproval=(
                    "not_implemented"
                    if r["source"]["kind"] == "design"
                    else "approved" if args.decision == "KEEP" else "needs_review"
                ),
                note=args.note,
                contentVersion=args.version,
            )
            if r["source"]["kind"] == "module":
                proof = r["runtime"].get("portableValidation") or {}
                valid = (
                    proof.get("runtimeFingerprint") == package.runtime_fingerprint()
                    and proof.get("sourceSha256") == r["source"]["sha256"]
                )
                r["runtime"]["deliveryStatus"] = (
                    "pending_review"
                    if args.decision == "CHANGE"
                    else (
                        "ready"
                        if valid
                        and r["qualification"].get("status") == "verified_scoped"
                        else "pending_portable_validation"
                    )
                )
            elif args.decision == "KEEP":
                r["gaps"] = [
                    v for v in r.get("gaps", []) if "has not received KEEP" not in v
                ]
            l.write(folder / "record.json", r)

        l.transaction(change)
        result = dict(id=args.id, decision=args.decision)
    elif args.command == "qualify":
        from .qualification import admit

        result = admit(args.id, args.evidence)
    elif args.command == "verify-package":
        result = package.verify(args.folder)
    else:
        from . import acceptance

        version = args.version if args.command == "build" else "0.0.0-validation"
        if not package.VERSION.fullmatch(version):
            raise ValueError("invalid_semver_package_version")
        commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=l.ROOT, text=True
        ).strip()
        if args.command == "build":
            with l.transaction_lock():
                package.assert_source_commit(commit)
        stage = Path(tempfile.mkdtemp(prefix="module-delivery-", dir=l.ROOT / "build"))
        candidate = stage / "candidate"
        archive = stage / "candidate.zip"
        try:
            package.stage(
                candidate, version, commit, False, strict_source=args.command == "build"
            )
            package.archive(candidate, archive)
            fingerprint = package.runtime_fingerprint()
            eligible = [r for _, r in l.records() if package.eligible(r)]
            cached = all(
                r["runtime"].get("deliveryStatus") == "ready"
                and r["runtime"].get("portableValidation", {}).get("runtimeFingerprint")
                == fingerprint
                and r["runtime"].get("portableValidation", {}).get("sourceSha256")
                == r["source"]["sha256"]
                for r in eligible
            )
            if args.command == "validate-portable" or args.revalidate or not cached:
                report, work = acceptance.run(
                    archive, args.godot, args.host_source, args.work
                )
                acceptance.certify(report)
                print(
                    json.dumps(
                        dict(
                            acceptance="passed",
                            modules=len(report["modules"]),
                            work=str(work),
                        ),
                        ensure_ascii=False,
                    ),
                    flush=True,
                )
            if args.command == "validate-portable":
                result = dict(status="verified", modules=len(eligible))
            else:
                final = stage / "final"
                entries, excluded = package.stage(
                    final, version, commit, True, strict_source=True
                )
                out = args.out / ("map-edit-modules-" + version + ".zip")
                temp_out = stage / "final.zip"
                digest = package.archive(final, temp_out)
                out.parent.mkdir(parents=True, exist_ok=True)
                if out.exists() and l.sha(out) != digest:
                    raise ValueError("immutable_package_version_conflict:" + str(out))
                if not out.exists():
                    shutil.copyfile(temp_out, out)
                checksum = out.with_suffix(out.suffix + ".sha256")
                checksum.write_text(digest + "  " + out.name + "\n")
                result = dict(
                    package=(
                        str(out.relative_to(l.ROOT))
                        if out.is_relative_to(l.ROOT)
                        else str(out)
                    ),
                    version=version,
                    sha256=digest,
                    sourceCommit=commit,
                    delivered=len(entries),
                    excluded=excluded,
                )
                l.write(out.with_suffix(".json"), result)
        finally:
            shutil.rmtree(stage)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, KeyError, subprocess.CalledProcessError) as error:
        print(
            json.dumps(dict(status="failed", reason=str(error)), ensure_ascii=False),
            file=sys.stderr,
        )
        raise SystemExit(2)
