"""Focused frozen-output handoff checks; no generation, loading or certification."""

import argparse
import gzip
import hashlib
import json
import re
import zipfile
from collections import defaultdict
from pathlib import Path

from check_inputs import ROOT, sha, write
from geometry import excluded_centers, fully_blocked_claim_region

LOCK = ROOT / "evidence/runtime-integration-930001/frozen-input-lock.json"
ZIP110 = "5ad5a7871941b2c1ffa759b18f7b1e80f2fe7e571b72f95d1e0ef26031f08723"
ZIP111 = "a806f8feb10e8a10f20014913afba49e9036be21d33c00618cfc86367ac993c6"
GAME = "e7d703f47c97f09bd5c5d48e24f0a400c958ad40"
GEN = "93c5221a9708d079c2864f3c14b415e81bb5de07"
SEMANTICS = {
    "linear_ferry": (
        "双向线性中心轨迹，停留/行程/初相，默认随模块时钟；不能套椭圆字段。",
        ["player_motor", "module_clock", "lifetime"],
    ),
    "clockwise_ellipse/v1": (
        "椭圆中心/半径/周期/x_sign，保持物化镜像后的方向。",
        ["player_motor", "module_clock", "lifetime"],
    ),
    "closed_polyline_loop/v1": (
        "按原闭合折线及周期运动；carrier 可由指定铃启停，不重置相位。",
        ["player_motor", "module_clock", "lifetime", "projectiles"],
    ),
    "hazards": (
        "源危险矩形；1.1.0 接触发射器默认 ENVIRONMENT 1HP/0.7s，非实体平台。",
        ["player_health", "policy", "lifetime"],
    ),
    "thorns": (
        "按 platform_index/face/offset/length/depth 绑定实际平台表面，默认原生接触伤害。",
        ["player_health", "policy", "lifetime"],
    ),
    "saws": (
        "origin+travel*sin(TAU*(clock/period+phase))；圆锯扫掠接触、独立脉冲去重。",
        ["player_motor", "player_health", "policy", "lifetime", "module_clock"],
    ),
    "safe_lesson": (
        "原生弹丸命中风铃开启实体门；open_seconds=0 为永久开。",
        ["projectiles", "player", "lifetime"],
    ),
    "timed_gate": (
        "open_seconds 定时开门，保留 return_access 与任意侧接收语义。",
        ["projectiles", "player", "lifetime", "module_clock"],
    ),
    "toggle_ferry": (
        "射铃切换目标 carrier 的 running 状态，保留 motion_clock。",
        ["projectiles", "player", "lifetime", "module_clock"],
    ),
    "native_one_way_carriers": (
        "仅 ids 指定的移动体 CollisionShape 为可穿，不能由固定台索引代替。",
        ["player_motor", "module_clock", "lifetime"],
    ),
    "group_motion": (
        "一项有效射击原子切换 targets 运行状态，保留各自时钟；access 是额外接收铃。",
        ["projectiles", "player", "lifetime", "module_clock"],
    ),
    "reward_pair": (
        "指定 reward_id 真正 COMMITTED 且金额>0 后切换两扇门；初始开口、延迟防夹和保存恢复均保留。",
        ["player", "lifetime", "wallet", "reward_commit", "module_state"],
    ),
    "enemies": (
        "definition 指定原种类；本地放置ID/初始冷却/命中回充/击败/接触时序保持。",
        ["player", "policy", "lifetime", "enemy_factory", "projectiles"],
    ),
    "refresh_carried_enemies": (
        "enemy 引用已有敌人、carrier 引用已有平台，不额外生成怪；warmup=2 只初始化位移观察样本。",
        ["player", "policy", "lifetime", "enemy_factory", "module_clock"],
    ),
    "hooks": (
        "kind=bounce 是原生反弹果，不是固定悬挂锚；保留 source_id 与反弹/恢复语义。",
        ["player_traversal", "lifetime"],
    ),
    "reward_sites": (
        "玩家落地且中心在 region 时调用原生领取；position 是展示点，amount 是现有金币数。",
        ["player_motor", "player_health", "wallet", "lifetime", "module_state"],
    ),
    "original_region_chests": (
        "原区域宝箱 tier/resources/领取状态；M29 同时有coin和note，不能当 reward_sites 金币箱。",
        ["player", "wallet", "lifetime", "meta_progression", "region_state"],
    ),
}


def pinned_zip(path, digest):
    assert sha(path.read_bytes()) == digest, "ZIP_SHA_MISMATCH_BEFORE_PARSE"
    return zipfile.ZipFile(path)


def contains(rect, point):
    # Open forbidden interior. Boundary tangency is not certified by this audit.
    x, y, w, h = rect
    px, py = point
    return x < px < x + w and y < py < y + h


def closure_examples():
    region = [300, -10, 80, 56]
    body = [24, 36]
    stand = [320, 14]
    cases = []
    for name, seal in [
        ("actual_M24_C_seal", [256, 0, 128, 32]),
        ("partial_region_overlap_but_original_station_clear", [384, 0, 128, 32]),
        ("thin_cap_region_not_fully_blocked_but_station_blocked", [256, 0, 128, 4]),
        ("vertical_separation_original_station_clear", [256, 64, 128, 32]),
    ]:
        expanded = excluded_centers(seal, body)
        cases.append(
            dict(
                name=name,
                claimRegion=region,
                actorBody=body,
                seal=seal,
                forbiddenCenterRect=expanded,
                entireRegionExcluded=fully_blocked_claim_region(region, seal, body),
                originalStation=stand,
                originalStationExcluded=contains(expanded, stand),
                scope="Static counterexample only. Original actual-cap case has prior native evidence; synthetic caps are not new module configurations or route qualifications.",
            )
        )
    assert [
        (x["entireRegionExcluded"], x["originalStationExcluded"]) for x in cases
    ] == [(True, True), (False, False), (False, True), (False, False)]
    return cases


def run(a):
    receipts = json.loads(LOCK.read_text())
    for r in receipts:
        folder = "game" if r["repository"] == "gunman-rush" else "mapgen"
        data = (a.inputs / folder / r["path"]).read_bytes()
        assert sha(data) == r["sha256"], r["path"]
        assert (
            hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
            == r["gitBlob"]
        ), r["path"]
    p = a.inputs / "mapgen/reference_package/fixtures/success"
    reference = json.loads((p / "map.json").read_text())
    store = json.loads((p / "content_store.json").read_text())
    candidate = json.loads(
        gzip.decompress(
            (
                a.inputs
                / "mapgen/validation/godot-candidate-0.3.0/replay-precision/validation-930001/actual.json.gz"
            ).read_bytes()
        )
    )["result"]
    assert candidate["status"] == "PASS" and candidate["content_store"] == store
    assert {k: v for k, v in reference.items() if k not in ["map_id", "generator"]} == {
        k: v for k, v in candidate["map"].items() if k not in ["map_id", "generator"]
    }
    assert (
        a.inputs / "game/resources/levels/mapgen_host_v2_01/map.json"
    ).read_bytes() == (p / "map.json").read_bytes()
    assert (
        reference["seed"] == 930001
        and len(reference["instances"]) == 46
        and len(reference["connections"]) == 55
    )
    assert reference["module_package"]["sha256"] == ZIP110
    z = pinned_zip(a.zip110, ZIP110)
    new = pinned_zip(a.zip111, ZIP111)
    oldcat = {e["id"]: e for e in json.loads(z.read("catalog.json"))["modules"]}
    newcat = {e["id"]: e for e in json.loads(new.read("catalog.json"))["modules"]}
    provider = (
        a.inputs / "game/game/world/levels/providers/runtime_map_v2_provider.gd"
    ).read_text()
    assert "const EMPTY_FIELDS:" in provider and '!= "clockwise_ellipse/v1"' in provider
    empty = re.search(r"const EMPTY_FIELDS:.*?= \[(.*?)\]", provider).group(1)
    blocked_fields = re.findall(r'"([^"]+)"', empty)
    index = {}
    groups = defaultdict(list)
    instances = {i["id"]: i for i in reference["instances"]}
    for i in reference["instances"]:
        c = store[i["content_ref"]]
        e = oldcat[i["module_id"]]
        assert (
            i["content_version"] == e["contentVersion"]
            and c["source_sha256"] == e["sourceSha256"]
            and c["stable_id"] == i["module_id"]
        )
        index.setdefault(
            i["module_id"],
            dict(
                contentVersion=i["content_version"],
                instances=[],
                sourceCompiled=e["compiled"],
                sourceSha256=e["sourceSha256"],
                qualification=e["qualification"],
                qualificationEvidence=e["qualificationEvidence"],
                portableValidation=e["portableValidation"],
            ),
        )["instances"].append(i["id"])
        fields = [
            "moving_platforms",
            "hazards",
            "thorns",
            "saws",
            "latches",
            "approved_hq_cells",
            "enemies",
            "refresh_carried_enemies",
            "hooks",
            "reward_sites",
            "original_region_chests",
        ]
        for field in fields:
            for n, value in enumerate(c.get(field, [])):
                if field == "moving_platforms":
                    kind = value.get("trajectory_kind", "linear_ferry")
                elif field == "approved_hq_cells":
                    kind = value["kind"]
                elif field == "latches":
                    kind = value.get("kind", "timed_gate")
                else:
                    kind = field
                assert kind in SEMANTICS, (i["id"], field, kind)
                status = "UNSUPPORTED_BY_PROVIDER"
                if kind == "clockwise_ellipse/v1":
                    status = "SCHEMA_SUPPORTED; ONLY_M16_IN_EXECUTED_SLICE"
                semantics, services = SEMANTICS[kind]
                ids = (
                    {
                        k: v
                        for k, v in value.items()
                        if k
                        in [
                            "id",
                            "source_id",
                            "surface_id",
                            "platform_id",
                            "ferry_id",
                            "actuator_id",
                            "reward_id",
                            "carrier",
                            "enemy",
                            "targets",
                            "ids",
                            "platform_index",
                        ]
                    }
                    if isinstance(value, dict)
                    else {"nativeDerivedId": "danger_" + str(n)}
                )
                if field == "thorns":
                    ids["platformRect"] = c["platforms"][value["platform_index"]]
                if field == "refresh_carried_enemies":
                    ids["warmupFrames"] = c["refresh_carrier_warmup_frames"]
                groups[kind].append(
                    dict(
                        instance=i["id"],
                        moduleId=i["module_id"],
                        contentVersion=i["content_version"],
                        contentRef=i["content_ref"],
                        fieldPath=f"{field}[{n}]",
                        value=value,
                        relatedObjectIds=ids,
                        semantic=semantics,
                        requiredServices=services,
                        declaredServices=i["required_services"],
                        hostStatus=status,
                        evidence=dict(
                            moduleQualificationReport=e["qualification"][
                                "originalReportSha256"
                            ],
                            portableReport=e["portableValidation"]["report"],
                            scope="Original source/locked-host evidence; generated transform/seal/neighbor and PR127 adapter execution not certified.",
                        ),
                    )
                )
    for instance in ["M01", "M24", "M35"]:
        i = instances[instance]
        c = store[i["content_ref"]]
        e = oldcat[i["module_id"]]
        raw = json.loads(z.read(e["compiled"]))
        offset = e["sceneOriginOffsetPixels"]
        assert not i["transform"]["mirror_x"] and c["source_affine"] == [
            1,
            0,
            0,
            1,
            *offset,
        ]
        for field in ["platforms", "hazards"]:
            assert c[field] == [
                [v[0] + offset[0], v[1] + offset[1], v[2], v[3]] for v in raw[field]
            ]
        for field in ["moving_platforms", "saws", "latches"]:
            assert len(raw[field]) == len(c[field]), (instance, field)
            for before, after in zip(raw[field], c[field]):
                for k in ["start", "finish", "origin", "bell"]:
                    if k in before:
                        assert after[k] == [
                            before[k][0] + offset[0],
                            before[k][1] + offset[1],
                        ]
                for k in ["gate", "paired_gate"]:
                    if k in before:
                        assert after[k] == [
                            before[k][0] + offset[0],
                            before[k][1] + offset[1],
                            *before[k][2:],
                        ]
                for k in [
                    "travel",
                    "size",
                    "period",
                    "initial_phase",
                    "travel_duration",
                    "dwell_duration",
                    "damage",
                    "contact_interval",
                    "open_seconds",
                ]:
                    if k in before:
                        assert before[k] == after[k]
        write(a.out / "focus" / f"{instance}.instance.json", i)
        # Preserve original frozen file bytes, never reserialize candidate JSON as that file.
        data = (p / i["content_ref"]).read_bytes()
        assert json.loads(data) == c
        target = a.out / "focus" / f"{instance}.content.json"
        target.write_bytes(data)
    assert oldcat.keys() == newcat.keys()
    changed = []
    for mid, b in oldcat.items():
        n = newcat[mid]
        before = json.loads(z.read(b["compiled"]))
        after = json.loads(new.read(n["compiled"]))
        assert {k: v for k, v in before.items() if k != "source_sha256"} == {
            k: v for k, v in after.items() if k != "source_sha256"
        }, mid
        if b["contentVersion"] != n["contentVersion"]:
            routes = []
            assert len(b["routes"]) == len(n["routes"]), mid
            for br, nr in zip(b["routes"], n["routes"]):
                assert br["id"] == nr["id"], mid
                if br["resourceProfile"] != nr["resourceProfile"]:
                    routes.append(
                        dict(
                            routeId=br["id"],
                            before=br["resourceProfile"],
                            after=nr["resourceProfile"],
                        )
                    )
            changed.append(
                dict(
                    moduleId=mid,
                    before=b["contentVersion"],
                    after=n["contentVersion"],
                    sourceShaBefore=b["sourceSha256"],
                    sourceShaAfter=n["sourceSha256"],
                    rewardRouteChanges=routes,
                    instancesIn930001=index.get(mid, {}).get("instances", []),
                )
            )
    assert len(changed) == 5
    runtime = [n for n in z.namelist() if n.startswith(("runtime/", "integration/"))]
    assert all(z.read(n) == new.read(n) for n in runtime)
    migration = dict(
        oldPackageSha256=ZIP110,
        newPackageSha256=ZIP111,
        oldManifest=json.loads(z.read("manifest.json"))
        | {"files": "omitted; immutable ZIP manifest"},
        newManifest=json.loads(new.read("manifest.json"))
        | {"files": "omitted; immutable ZIP manifest"},
        sameModuleSet=True,
        all115NativePayloadsEqualExceptSourceHash=True,
        runtimeIntegrationFilesUnchanged=len(runtime),
        changedVersions=changed,
        changedFiles=[
            n for n in z.namelist() if n in new.namelist() and z.read(n) != new.read(n)
        ],
        addedFiles=sorted(set(new.namelist()) - set(z.namelist())),
        oldGaps=json.loads(z.read("reward-association-gaps.json")),
        newGaps=json.loads(new.read("reward-association-gaps.json")),
    )
    write(a.out / "migration-110-111.json", migration)
    write(
        a.out / "mechanism-coverage.json",
        dict(
            hostCommit=GAME,
            mapGenCommit=GEN,
            modulePackageVersion="1.1.0",
            moduleIndex=index,
            groups=groups,
            hostRejectedNonemptyFields=blocked_fields,
            interfaceCoverage=dict(
                anchors=reference["anchors"],
                seals=[
                    dict(instance=i["id"], seal=s)
                    for i in reference["instances"]
                    for s in i["seals"]
                ],
                oneWayConnections=[
                    c
                    for c in reference["connections"]
                    if c["surface"] == "ONE_WAY_PLATFORM"
                ],
                nonInoutPorts=[
                    dict(
                        instance=i["id"],
                        port=p,
                        connected=p["id"] in i["connected_port_ids"],
                    )
                    for i in reference["instances"]
                    for p in i["ports"]
                    if p["permission"] != "INOUT"
                ],
                scope="Static platforms and seal shapes are accepted only within the existing controlled slice. ONE_WAY_PLATFORM internal seams are rejected. The two legal INPUT ports are both unused/sealed; they do not themselves reject the current connection graph. Boss/spawn still require host bindings.",
            ),
            source="complete frozen 930001; no runtime generation or host adapter execution",
        ),
    )
    write(a.out / "m24-rule-cases.json", closure_examples())
    focus = [
        dict(
            instance=i,
            contentSha256=sha((a.out / "focus" / f"{i}.content.json").read_bytes()),
            contentVersion=instances[i]["content_version"],
        )
        for i in ["M01", "M24", "M35"]
    ]
    write(
        a.out / "frozen-checks.json",
        dict(
            pr78Base="2ec243842567a56a49b84fc93ce4aa750b11ff5f",
            hostCommit=GAME,
            mapGenCommit=GEN,
            verifiedReadOnlyInputs=len(receipts),
            referenceMapSha256=sha((p / "map.json").read_bytes()),
            referenceMapId=reference["map_id"],
            candidateMapId=candidate["map"]["map_id"],
            referenceGenerator=reference["generator"],
            candidateGenerator=candidate["map"]["generator"],
            completeContentStoreEqual=True,
            mapEqualExceptMapIdAndGenerator=True,
            hostFrozenMapBytesEqual=True,
            instances=46,
            uniqueModuleVersions=len(index),
            connections=55,
            mechanismObjectCounts={k: len(v) for k, v in groups.items()},
            focus=focus,
            scope="Static data/source comparison and geometric counterexamples only. Reuses PR78 native observations; no new host compatibility certification.",
        ),
    )
    print(
        json.dumps(
            dict(
                instances=46,
                uniqueModules=len(index),
                groups={k: len(v) for k, v in groups.items()},
                changedVersions=len(changed),
            ),
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inputs", required=True, type=Path)
    p.add_argument("--zip110", required=True, type=Path)
    p.add_argument("--zip111", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    run(p.parse_args())
