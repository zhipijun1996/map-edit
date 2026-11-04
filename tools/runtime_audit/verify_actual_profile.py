"""Replay the one producer and tamper its actual inputs; never run a host or SDK."""

import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from check_inputs import ROOT, sha, write

PRODUCER = ROOT / "tools/runtime_audit/check_930001.py"
BASE = "812e89050e062c866a5dd7e8c258e47d3897bc4d"
ORIGINAL_OUTPUTS = {
    "default": "3c79e25e5866b01ae9891f41bb8ce05da2178226a02591187454987d099aaaf9",
    "gears": "dfcab57baf961ed8a6f254f6a9ee176c66d1ab608fa888bef0f47059d7707f84",
}
ORIGINAL_CASES = [
    "result-sha",
    "result-schema",
    "request-fingerprint",
    "missing-content-ref",
    "orphan-content-ref",
    "missing-moving-field",
    "empty-moving-array",
    "missing-hazards-field",
    "unknown-content-field",
    "unknown-mechanism",
    "duplicate-instance",
    "duplicate-connection",
    "missing-endpoint-instance",
    "missing-endpoint-port",
    "content-version",
    "source-sha",
    "unknown-module",
    "protocol-payload-newline",
    "old-algorithm",
]
ADDED_CASES = [
    "bindings-fingerprint",
    "bindings-origin",
    "bindings-internal-edge",
    "bindings-spawn",
    "bindings-root",
    "bindings-body",
    "provider-vector",
    "provider-version",
    "snapshot-commit",
    "snapshot-source-digest",
    "snapshot-source-drift",
    "receipt-mismatch",
    "receipt-head",
    "harness-hash",
    "nested-target-array",
    "nested-vector-shape",
    "stable-local-id",
    "missing-port",
    "bad-seal-ref",
    "bad-route-reward",
    "invalid-permission",
    "missing-input-role",
    "input-path-escape",
    "missing-input-file",
]


def actual_command(inputs, profile, archive, out, equals=False):
    return [
        sys.executable,
        "-B",
        str(PRODUCER),
        *(
            ["--actual-profile=" + str(profile)]
            if equals
            else ["--actual-profile", str(profile)]
        ),
        "--inputs",
        str(inputs),
        "--zip110",
        str(archive),
        "--out",
        str(out),
    ]


def invoke(cmd, log):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=30)
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text(r.stdout + r.stderr)
    return r


def mutation(original, raw, case):
    result = copy.deepcopy(original)
    roles = {}
    expected = "AssertionError"
    store = result["content_store"]
    instances = result["map"]["instances"]
    first = instances[0]
    content = store[first["content_ref"]]
    connections = result["map"]["connections"]
    if case == "result-sha":
        result["metrics"]["negative_probe_only"] = True
        expected = "ACTUAL_INPUT_SHA_MISMATCH"
    elif case == "result-schema":
        result["schema"] = "wrong"
    elif case == "request-fingerprint":
        result["request_fingerprint"] = "0" * 64
    elif case == "missing-content-ref":
        store.pop(first["content_ref"])
        expected = "ACTUAL_STORE_REFS_MISMATCH"
    elif case == "orphan-content-ref":
        store["content/orphan.json"] = {}
        expected = "ACTUAL_STORE_REFS_MISMATCH"
    elif case == "missing-moving-field":
        content.pop("moving_platforms")
        expected = "ACTUAL_CONTENT_FIELDS_MISMATCH"
    elif case == "empty-moving-array":
        next(c for c in store.values() if c["moving_platforms"])[
            "moving_platforms"
        ] = []
        expected = "ACTUAL_ARRAY_LENGTH_MISMATCH"
    elif case == "missing-hazards-field":
        content.pop("hazards")
        expected = "ACTUAL_CONTENT_FIELDS_MISMATCH"
    elif case == "unknown-content-field":
        content["unexpected_component"] = []
        expected = "ACTUAL_CONTENT_FIELDS_MISMATCH"
    elif case == "unknown-mechanism":
        next(c for c in store.values() if c.get("latches"))["latches"][0][
            "kind"
        ] = "unregistered_mechanism"
    elif case == "duplicate-instance":
        instances.append(copy.deepcopy(first))
        expected = "DUPLICATE_ACTUAL_INSTANCE_ID"
    elif case == "duplicate-connection":
        connections.append(copy.deepcopy(connections[0]))
    elif case == "missing-endpoint-instance":
        connections[0]["a"]["instance_id"] = "does_not_exist"
        expected = "KeyError"
    elif case == "missing-endpoint-port":
        connections[0]["a"]["port_id"] = "does_not_exist"
    elif case == "content-version":
        first["content_version"] = "sha256:" + "0" * 64
    elif case == "source-sha":
        content["source_sha256"] = "0" * 64
    elif case == "unknown-module":
        first["module_id"] = "missing-module"
        expected = "KeyError"
    elif case == "old-algorithm":
        result["map"]["generator"]["algorithm"] = "stable-v2"
    elif case == "protocol-payload-newline":
        roles["protocol_payload"] = raw["protocol_payload"] + b"\n"
    elif case.startswith("bindings-"):
        b = json.loads(raw["host_bindings"])
        resolved = b["selection_resolution"]
        if case == "bindings-fingerprint":
            resolved["generation_input_fingerprint"] = "0" * 64
        elif case == "bindings-origin":
            resolved["instances"][0]["origin_blocks"][0] += 1
        elif case == "bindings-internal-edge":
            resolved["internal_connections"].append(copy.deepcopy(connections[0]))
        elif case == "bindings-spawn":
            resolved["spawn_world"][0] += 1
        elif case == "bindings-root":
            resolved["root_instance_id"] = "not-selected"
        elif case == "bindings-body":
            resolved["spawn_body_half"][0] += 1
        roles["host_bindings"] = json.dumps(b).encode()
    elif case.startswith("snapshot-"):
        s = json.loads(raw["host_source_snapshot"])
        if case == "snapshot-commit":
            s["commit"] = "0" * 40
        elif case == "snapshot-source-drift":
            s["after"]["README.md"] = "0" * 64
        elif case == "snapshot-source-digest":
            s["before"]["README.md"] = s["after"]["README.md"] = "0" * 64
        roles["host_source_snapshot"] = json.dumps(s).encode()
    elif case in ["provider-vector", "provider-version"]:
        provider = raw["host_provider"].replace(
            b"const ADAPTER_VERSION", b"const MISSING_ADAPTER_VERSION"
        )
        roles["host_provider"] = provider
        if case == "provider-version":
            s = json.loads(raw["host_source_snapshot"])
            path = "game/world/levels/providers/runtime_map_v2_provider.gd"
            s["before"][path] = s["after"][path] = sha(provider)
            roles["host_source_snapshot"] = json.dumps(s).encode()
    elif case in ["receipt-mismatch", "receipt-head", "harness-hash"]:
        e = json.loads(raw["validation_evidence"])
        if case == "harness-hash":
            e["harness_report"]["status"] = "failed"
        else:
            e["native_receipt"]["head"] = "0" * 40
            if case == "receipt-head":
                s = json.loads(raw["host_source_snapshot"])
                s["native_receipt"] = e["native_receipt"]
                roles["host_source_snapshot"] = json.dumps(s).encode()
        roles["validation_evidence"] = json.dumps(e).encode()
    elif case == "nested-target-array":
        next(
            v
            for c in store.values()
            for v in c.get("approved_hq_cells", [])
            if v["kind"] == "group_motion"
        )["targets"] = []
    elif case == "nested-vector-shape":
        next(c for c in store.values() if c["moving_platforms"])["moving_platforms"][0][
            "size"
        ].pop()
    elif case == "stable-local-id":
        next(c for c in store.values() if c["moving_platforms"])["moving_platforms"][0][
            "platform_id"
        ] = "new-id"
    elif case == "missing-port":
        first["ports"].pop()
    elif case == "bad-seal-ref":
        first["seals"][0]["port_id"] = "not-a-port"
    elif case == "bad-route-reward":
        next(r for i in instances for r in i["routes"])["required_reward_ids"].append(
            "not-a-reward"
        )
    elif case == "invalid-permission":
        first["ports"][0]["permission"] = "IN"
    elif case not in ["missing-input-role", "input-path-escape", "missing-input-file"]:
        raise ValueError(case)
    if case in ORIGINAL_CASES or case in [
        "nested-target-array",
        "nested-vector-shape",
        "stable-local-id",
        "missing-port",
        "bad-seal-ref",
        "bad-route-reward",
        "invalid-permission",
    ]:
        roles["result"] = json.dumps(result).encode()
    return roles, expected


def run(a):
    a.work.mkdir(exist_ok=False)
    inputs = a.work / "inputs"
    shutil.copytree(a.inputs, inputs)
    before = {
        str(p.relative_to(a.inputs)): sha(p.read_bytes())
        for p in a.inputs.rglob("*")
        if p.is_file()
    }
    positive = []
    negatives = []
    for name in ["default", "gears"]:
        profile = json.loads((inputs / (name + "-profile.json")).read_text())
        raw = {
            role: (inputs / row["path"]).read_bytes()
            for role, row in profile["files"].items()
        }
        original = json.loads(raw["result"])
        out = a.work / (name + "-output")
        r = invoke(
            actual_command(
                inputs,
                inputs / (name + "-profile.json"),
                a.zip110,
                out,
                equals=name == "gears",
            ),
            a.work / "logs" / (name + "-positive.log"),
        )
        assert r.returncode == 0, r.stderr
        data = json.loads((out / "mechanism-coverage.json").read_text())
        comparison = copy.deepcopy(data)
        comparison.pop("assessment")
        control = sha(
            (json.dumps(comparison, ensure_ascii=False, indent=2) + "\n").encode()
        )
        assert control == ORIGINAL_OUTPUTS[name], (name, "upstream inventory changed")
        assert all(
            row["hostStatus"] == "UNVERIFIED_CURRENT_HOST"
            for rows in data["groups"].values()
            for row in rows
        )
        positive.append(
            dict(
                profile=name,
                instances=len(data["interfaceCoverage"]["instances"]),
                connections=len(data["interfaceCoverage"]["connections"]),
                groups=len(data["groups"]),
                objects=sum(len(v) for v in data["groups"].values()),
                upstreamInventorySha256=control,
                upstreamInventoryUnchanged=True,
                outputSha256=sha((out / "mechanism-coverage.json").read_bytes()),
                allRowsUnverified=True,
            )
        )
        for case in ORIGINAL_CASES + ADDED_CASES:
            key = name + "-" + case
            folder = inputs / "probes" / key
            folder.mkdir(parents=True)
            lock = copy.deepcopy(profile)
            changes, expected = mutation(original, raw, case)
            for role, b in changes.items():
                path = folder / (role + ".json")
                path.write_bytes(b)
                old_hash = lock["files"][role]["sha256"]
                lock["files"][role] = {
                    "path": str(path.relative_to(inputs)),
                    "sha256": (
                        old_hash
                        if case == "result-sha" and role == "result"
                        else sha(b)
                    ),
                }
            if case == "missing-input-role":
                lock["files"].pop("validation_evidence")
            if case == "input-path-escape":
                lock["files"]["result"]["path"] = "../outside.json"
            if case == "missing-input-file":
                lock["files"]["result"]["path"] = "missing.json"
                expected = "FileNotFoundError"
            file = folder / "profile.json"
            write(file, lock)
            out = a.work / "rejected" / key
            r = invoke(
                actual_command(inputs, file, a.zip110, out),
                a.work / "logs" / (key + ".log"),
            )
            assert r.returncode != 0 and expected in r.stderr and not out.exists(), (
                key,
                r.stdout,
                r.stderr,
            )
            negatives.append(
                dict(
                    profile=name,
                    case=case,
                    origin=(
                        "upstream38"
                        if case in ORIGINAL_CASES
                        else "added_binding_and_completeness"
                    ),
                    exitCode=r.returncode,
                    expectedErrorSeen=True,
                    noOutput=True,
                    lastError=r.stderr.strip().splitlines()[-1],
                )
            )
    # CLI/output guards must preserve existing output, including the old freeze.
    guards = []
    for label, target in [
        ("existing-output", a.work / "default-output"),
        ("old-frozen-output", ROOT / "evidence/runtime-integration-930001"),
    ]:
        initial = {
            str(p.relative_to(target)): sha(p.read_bytes())
            for p in target.rglob("*")
            if p.is_file()
        }
        r = invoke(
            actual_command(inputs, inputs / "default-profile.json", a.zip110, target),
            a.work / "logs" / (label + ".log"),
        )
        assert r.returncode != 0 and initial == {
            str(p.relative_to(target)): sha(p.read_bytes())
            for p in target.rglob("*")
            if p.is_file()
        }
        guards.append(dict(case=label, rejected=True, existingFilesUnchanged=True))
    assert before == {
        str(p.relative_to(a.inputs)): sha(p.read_bytes())
        for p in a.inputs.rglob("*")
        if p.is_file()
    }
    compatibility = None
    if a.legacy_inputs:
        baseline = a.work / "original_930001.py"
        baseline.write_bytes(
            subprocess.check_output(
                ["git", "show", BASE + ":tools/runtime_audit/check_930001.py"], cwd=ROOT
            )
        )
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "tools/runtime_audit")
        for label, producer in [("original", baseline), ("adopted", PRODUCER)]:
            out = a.work / ("legacy-" + label)
            cmd = [
                sys.executable,
                "-B",
                str(producer),
                "--inputs",
                str(a.legacy_inputs),
                "--zip110",
                str(a.zip110),
                "--zip111",
                str(a.zip111),
                "--out",
                str(out),
            ]
            r = subprocess.run(
                cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=30
            )
            assert r.returncode == 0, r.stderr
        original = a.work / "legacy-original"
        current = a.work / "legacy-adopted"
        names = sorted(
            str(p.relative_to(original)) for p in original.rglob("*") if p.is_file()
        )
        assert len(names) == 10
        for name in names:
            assert (
                (original / name).read_bytes()
                == (current / name).read_bytes()
                == (ROOT / "evidence/runtime-integration-930001" / name).read_bytes()
            ), name
        old_neg = []
        for kind in ["missing", "tampered"]:
            altered = a.work / ("legacy-" + kind)
            shutil.copytree(a.legacy_inputs, altered)
            file = (
                altered / "mapgen/reference_package/fixtures/success/content/M35.json"
            )
            if kind == "missing":
                file.unlink()
            else:
                doc = json.loads(file.read_text())
                doc["platforms"][0][1] += 1
                file.write_text(json.dumps(doc))
            for label, producer in [("original", baseline), ("adopted", PRODUCER)]:
                out = a.work / ("legacy-reject-" + kind + "-" + label)
                cmd = [
                    sys.executable,
                    "-B",
                    str(producer),
                    "--inputs",
                    str(altered),
                    "--zip110",
                    str(a.zip110),
                    "--zip111",
                    str(a.zip111),
                    "--out",
                    str(out),
                ]
                r = subprocess.run(
                    cmd, cwd=ROOT, env=env, capture_output=True, text=True, timeout=30
                )
                assert r.returncode != 0 and not out.exists()
                old_neg.append(
                    dict(producer=label, case=kind, rejected=True, noOutput=True)
                )
        compatibility = dict(
            base=BASE,
            inputs=43,
            outputs=names,
            allTenByteIdentical=True,
            originalAndAdoptedMissingTampered=old_neg,
        )
    report = dict(
        producerSha256=sha(PRODUCER.read_bytes()),
        positive=positive,
        negative=negatives,
        outputGuards=guards,
        originalInputsUnchanged=True,
        legacyCompatibility=compatibility,
        scope="Producer tests only. No host/SDK/Godot execution and no row certification.",
    )
    write(a.work / "verification.json", report)
    print(
        json.dumps(
            dict(
                positive=len(positive),
                upstreamNegatives=sum(r["origin"] == "upstream38" for r in negatives),
                addedNegatives=sum(r["origin"] != "upstream38" for r in negatives),
                outputGuards=len(guards),
                oldTenOutputsEqual=bool(compatibility),
            )
        )
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inputs", type=Path, required=True)
    p.add_argument("--zip110", type=Path, required=True)
    p.add_argument("--work", type=Path, required=True)
    p.add_argument("--legacy-inputs", type=Path)
    p.add_argument("--zip111", type=Path)
    a = p.parse_args()
    if bool(a.legacy_inputs) != bool(a.zip111):
        p.error("--legacy-inputs and --zip111 are paired")
    run(a)
