"""Focused frozen-output handoff checks; no generation, loading or certification."""

import argparse
import gzip
import hashlib
import json
import math
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
INVENTORY_FIELDS = [
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


def extract_inventory(reference, store, oldcat, *, current_host=False):
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
        for field in INVENTORY_FIELDS:
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
                if current_host:
                    status = "UNVERIFIED_CURRENT_HOST"
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
    if current_host:
        for rows in groups.values():
            for row in rows:
                row["role"] = instances[row["instance"]]["role"]
                row["evidence"][
                    "scope"
                ] = "Original module qualification only; current host execution/physics not certified by extraction."
    return index, groups, instances


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
    index, groups, instances = extract_inventory(reference, store, oldcat)
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


def validate_actual_store(reference, store, catalog, package):
    """Check complete inventory structure, not a second geometry transform."""
    refs = {instance["content_ref"] for instance in reference["instances"]}
    assert set(store) == refs, "ACTUAL_STORE_REFS_MISMATCH"
    for instance in reference["instances"]:
        entry = catalog[instance["module_id"]]
        compiled = json.loads(package.read(entry["compiled"]))
        content = store[instance["content_ref"]]
        assert isinstance(content, dict), "ACTUAL_CONTENT_NOT_OBJECT"
        fields = set(compiled) - {"ports", "routes"}
        assert set(content) == fields | {
            "coordinate_frame",
            "source_affine",
        }, "ACTUAL_CONTENT_FIELDS_MISMATCH"
        assert content["coordinate_frame"] == "owned_rectangle_pixels"
        assert (
            isinstance(content["source_affine"], list)
            and len(content["source_affine"]) == 6
        )
        assert "platforms" in fields and isinstance(compiled["platforms"], list)
        for field in fields:
            before, after = compiled[field], content[field]
            if isinstance(before, list):
                assert isinstance(after, list) and len(after) == len(before), (
                    instance["id"],
                    field,
                    "ACTUAL_ARRAY_LENGTH_MISMATCH",
                )
                # Export changes coordinates, not the array item/container type.
                for old_item, new_item in zip(before, after):
                    assert isinstance(new_item, type(old_item)) or (
                        isinstance(old_item, (int, float))
                        and not isinstance(old_item, bool)
                        and isinstance(new_item, (int, float))
                        and not isinstance(new_item, bool)
                    ), (instance["id"], field, "ACTUAL_ARRAY_ITEM_TYPE_MISMATCH")
                    if isinstance(old_item, list):
                        assert len(new_item) == len(
                            old_item
                        ), "ACTUAL_ARRAY_ITEM_LENGTH_MISMATCH"
                    if isinstance(old_item, dict):
                        old_keys, new_keys = set(old_item), set(new_item)
                        if old_item.get("trajectory_kind") == "clockwise_ellipse/v1":
                            # Original materialize may add/remove this sign on reflection.
                            old_keys.discard("ellipse_x_sign")
                            new_keys.discard("ellipse_x_sign")
                        assert new_keys == old_keys, "ACTUAL_OBJECT_FIELDS_MISMATCH"
            else:
                assert isinstance(after, type(before)) or (
                    isinstance(before, (int, float))
                    and not isinstance(before, bool)
                    and isinstance(after, (int, float))
                    and not isinstance(after, bool)
                ), (instance["id"], field, "ACTUAL_FIELD_TYPE_MISMATCH")
            complete_shape(before, after, field)
        assert all(
            number(v) for v in content["source_affine"]
        ), "ACTUAL_NONFINITE_AFFINE"
        metadata = {
            "schema",
            "source_sha256",
            "stable_id",
            "world_bounds",
            "entry_port",
            "exit_port",
            "coordinate_frame",
            "source_affine",
            "platforms",
            "one_way_platform_indices",
            "wall_platform_indices",
            "refresh_carrier_warmup_frames",
        }
        for field, value in content.items():
            assert field in INVENTORY_FIELDS or field in metadata or not value, (
                field,
                "ACTUAL_UNMODELED_NONEMPTY_CONTENT",
            )
        validate_local_refs(instance, content, entry)


def number(value):
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(value)
    )


def complete_shape(before, after, field):
    """Recursive completeness and stable references, never a coordinate transform."""
    identity_fields = {
        "id",
        "platform_id",
        "source_id",
        "surface_id",
        "definition",
        "ids",
        "targets",
        "enemy",
        "carrier",
        "actuator_id",
        "reward_id",
        "ferry_id",
        "mount",
        "latch_id",
        "one_way_platform_indices",
        "wall_platform_indices",
    }
    if field in identity_fields:
        assert before == after, (field, "ACTUAL_STABLE_REFERENCE_CHANGED")
    if isinstance(before, dict):
        assert isinstance(after, dict), "ACTUAL_NESTED_TYPE_MISMATCH"
        a, b = set(before), set(after)
        if before.get("trajectory_kind") == "clockwise_ellipse/v1":
            a.discard("ellipse_x_sign")
            b.discard("ellipse_x_sign")
            if "ellipse_x_sign" in after:
                assert number(after["ellipse_x_sign"]) and after["ellipse_x_sign"] in [
                    -1,
                    1,
                ]
        assert a == b, "ACTUAL_NESTED_FIELDS_MISMATCH"
        for key in a:
            complete_shape(before[key], after[key], key)
    elif isinstance(before, list):
        assert isinstance(after, list) and len(before) == len(
            after
        ), "ACTUAL_NESTED_ARRAY_MISMATCH"
        for a, b in zip(before, after):
            complete_shape(a, b, field)
    elif number(before):
        assert number(after), "ACTUAL_NESTED_NUMBER_MISMATCH"
    elif isinstance(before, str):
        alternatives = [before]
        if field in ["face", "targetFace", "return_access_side_policy"]:
            flipped = {
                "left": "right",
                "right": "left",
                "LEFT": "RIGHT",
                "RIGHT": "LEFT",
            }
            alternatives.append(flipped.get(before, before))
        assert after in alternatives, (field, "ACTUAL_LITERAL_CHANGED")
    else:
        assert type(after) is type(before), "ACTUAL_NESTED_TYPE_MISMATCH"


def validate_local_refs(instance, content, entry):
    port_ids = [p["id"] for p in instance["ports"]]
    assert len(port_ids) == len(set(port_ids)) and set(port_ids) == {
        p["id"] for p in entry["ports"]
    }, "ACTUAL_PORT_REFS_MISMATCH"
    assert all(
        p["permission"] in ["INPUT", "OUTPUT", "INOUT"] for p in instance["ports"]
    ), "ACTUAL_PORT_PERMISSION_INVALID"
    connected = instance["connected_port_ids"]
    assert len(connected) == len(set(connected)) and set(connected) <= set(
        port_ids
    ), "ACTUAL_CONNECTED_PORT_REFS_MISMATCH"
    sealed = [s["port_id"] for s in instance["seals"]]
    assert (
        len(sealed) == len(set(sealed))
        and set(sealed) <= set(port_ids)
        and not set(sealed) & set(connected)
    ), "ACTUAL_SEAL_REFS_MISMATCH"

    def ids(field, key):
        values = [row[key] for row in content.get(field, [])]
        assert len(values) == len(set(values)), (field, "ACTUAL_DUPLICATE_LOCAL_ID")
        return set(values)

    platforms = ids("moving_platforms", "platform_id")
    enemies = ids("enemies", "id")
    rewards = ids("reward_sites", "id") | ids("original_region_chests", "id")
    ids("latches", "id")
    for row in content.get("latches", []):
        if "ferry_id" in row:
            assert row["ferry_id"] in platforms, "ACTUAL_FERRY_REF_MISMATCH"
    for row in content.get("approved_hq_cells", []):
        if row["kind"] in ["group_motion", "native_one_way_carriers"]:
            assert (
                set(row.get("targets", row.get("ids", []))) <= platforms
            ), "ACTUAL_MOTION_REF_MISMATCH"
        if row["kind"] == "reward_pair":
            assert row["reward_id"] in rewards, "ACTUAL_REWARD_REF_MISMATCH"
    for row in content.get("refresh_carried_enemies", []):
        assert (
            row["enemy"] in enemies and row["carrier"] in platforms
        ), "ACTUAL_CARRIED_REF_MISMATCH"
    for row in content.get("thorns", []):
        n = row["platform_index"]
        assert (
            number(n) and int(n) == n and 0 <= n < len(content["platforms"])
        ), "ACTUAL_THORN_REF_MISMATCH"
    for route in instance["routes"]:
        assert (
            route["from_port"] in port_ids and route["to_port"] in port_ids
        ), "ACTUAL_ROUTE_PORT_REF_MISMATCH"
        assert (
            set(route["required_reward_ids"]) <= rewards
        ), "ACTUAL_ROUTE_REWARD_REF_MISMATCH"


def bind_host_records(data, profile, reference, store, fingerprint):
    """Bind recorded host facts. This does not attest Git custody or execute Godot."""
    bindings = json.loads(data["host_bindings"])
    snapshot = json.loads(data["host_source_snapshot"])
    evidence = json.loads(data["validation_evidence"])
    provider = data["host_provider"].decode("utf-8")
    assert snapshot["schema"] == "gunman-rush/actual-source-snapshot/v1"
    assert snapshot["commit"] == profile["host_commit"], "ACTUAL_HOST_COMMIT_MISMATCH"
    assert snapshot["before"] == snapshot["after"], "ACTUAL_SOURCE_VECTOR_CHANGED"
    provider_path = "game/world/levels/providers/runtime_map_v2_provider.gd"
    assert snapshot["before"][provider_path] == sha(
        data["host_provider"]
    ), "ACTUAL_PROVIDER_VECTOR_MISMATCH"
    version = re.search(r'const ADAPTER_VERSION\s*:=\s*"([^"\n]+)"', provider)
    assert version, "ACTUAL_PROVIDER_VERSION_MISSING"
    receipt = evidence["native_receipt"]
    assert receipt == snapshot["native_receipt"], "ACTUAL_EXECUTION_RECEIPT_MISMATCH"
    # Encodings of these Python-produced host receipts, checked against the
    # original f6 raw report and decompressed source vectors. This is unrelated
    # to the GDScript Protocol payload, whose raw bytes are never regenerated.
    report_bytes = (
        json.dumps(evidence["harness_report"], ensure_ascii=False, indent=2) + "\n"
    ).encode()
    assert (
        sha(report_bytes) == evidence["harness_report_sha256"]
    ), "ACTUAL_HARNESS_REPORT_HASH_MISMATCH"
    for side in ["before", "after"]:
        vector_bytes = (
            json.dumps(snapshot[side], sort_keys=True, indent=2, ensure_ascii=True)
            + "\n"
        ).encode()
        assert (
            sha(vector_bytes) == receipt["source_" + side + "_sha256"]
        ), "ACTUAL_SOURCE_VECTOR_DIGEST_MISMATCH"
    assert (
        receipt["head"]
        == profile["host_commit"]
        == evidence["harness_report"]["commit"]
    ), "ACTUAL_EXECUTION_COMMIT_MISMATCH"
    assert (
        receipt["source_equal"] is True
        and receipt["source_before_sha256"] == receipt["source_after_sha256"]
    ), "ACTUAL_EXECUTION_SOURCE_MISMATCH"
    assert (
        receipt["before_files"] == len(snapshot["before"]) == receipt["after_files"]
    ), "ACTUAL_EXECUTION_VECTOR_COUNT_MISMATCH"
    assert receipt.get("changed_paths", []) == [], "ACTUAL_EXECUTION_SOURCE_MISMATCH"
    assert evidence["scope"] and re.fullmatch(
        r"[0-9a-f]{64}", evidence["harness_report_sha256"]
    )
    # Keep passed/failed/unverified receipt facts; no check result upgrades any row.
    checks = evidence["harness_report"]["checks"]
    assert len({c["id"] for c in checks}) == len(
        checks
    ), "ACTUAL_DUPLICATE_EVIDENCE_CHECK"
    assert (
        bindings["schema"] == "gunman-rush/runtime-map-bindings/v1"
        and bindings["version"]
    )
    resolution = bindings["selection_resolution"]
    assert (
        resolution["generation_input_fingerprint"] == fingerprint
    ), "ACTUAL_BINDING_FINGERPRINT_MISMATCH"
    instances = {i["id"]: i for i in reference["instances"]}
    selected = bindings["selected_instances"]
    assert (
        selected
        and len(set(selected)) == len(selected)
        and set(selected) <= instances.keys()
    ), "ACTUAL_BINDING_SELECTION_MISMATCH"
    resolved = resolution["instances"]
    assert len(resolved) == len(selected) and {
        r["instance_id"] for r in resolved
    } == set(selected), "ACTUAL_BINDING_SELECTION_MISMATCH"
    for row in resolved:
        actual = instances[row["instance_id"]]
        assert all(
            row[k] == actual[k]
            for k in [
                "module_id",
                "content_version",
                "role",
                "origin_blocks",
                "transform",
            ]
        ), "ACTUAL_BINDING_INSTANCE_MISMATCH"
    expected_edges = [
        e
        for e in reference["connections"]
        if e["a"]["instance_id"] in selected and e["b"]["instance_id"] in selected
    ]
    actual_edges = resolution["internal_connections"]
    assert len(actual_edges) == len(expected_edges) and {
        e["id"]: e for e in actual_edges
    } == {e["id"]: e for e in expected_edges}, "ACTUAL_BINDING_TOPOLOGY_MISMATCH"
    root = resolution["root_instance_id"]
    assert root in selected, "ACTUAL_BINDING_ROOT_MISMATCH"
    recipe = bindings["selection_recipe"]
    assert all(
        recipe["root"][k] == instances[root][k]
        for k in ["module_id", "content_version", "role"]
    ), "ACTUAL_BINDING_RECIPE_MISMATCH"
    assert recipe["expected_internal_edges"] == len(
        expected_edges
    ), "ACTUAL_BINDING_TOPOLOGY_MISMATCH"
    rule = bindings["spawn_rule"]
    n = resolution["spawn_platform_index"]
    assert (
        number(n)
        and int(n) == n
        and 0 <= n < len(store[instances[root]["content_ref"]]["platforms"])
    ), "ACTUAL_BINDING_SPAWN_REF_MISMATCH"
    assert rule["platform_index"] == n
    local, world, half = (
        resolution["spawn_local"],
        resolution["spawn_world"],
        resolution["spawn_body_half"],
    )
    assert all(
        isinstance(p, list) and len(p) == 2 and all(number(v) for v in p)
        for p in [local, world, half]
    ), "ACTUAL_BINDING_SPAWN_INVALID"
    assert all(v > 0 for v in half) and bindings["spawns"]["seam"] == world
    assert (
        half
        == json.loads(data["provenance"])["request"]["player"][
            "clearance_half_extents_pixels"
        ]
    ), "ACTUAL_BINDING_BODY_MISMATCH"
    assert world == [
        instances[root]["origin_blocks"][k] * 128 + local[k] for k in range(2)
    ], "ACTUAL_BINDING_SPAWN_MISMATCH"
    # Observe the exact Provider guards; admission is weaker than compatibility.
    empty = re.search(r"const EMPTY_FIELDS:.*?= \[(.*?)\]", provider)
    fields = re.search(r"const CONTENT_FIELDS:.*?= \[(.*?)\]", provider)
    assert empty and fields, "ACTUAL_PROVIDER_GUARDS_MISSING"
    return dict(
        dataPresence="COMPLETE_STRUCTURE_AND_REFERENCES_CHECKED_NOT_NUMERIC_GEOMETRY_EQUIVALENCE",
        provider=dict(
            sha256=sha(data["host_provider"]),
            adapterVersion=version.group(1),
            explicitlyEmptyFields=re.findall(r'"([^\"]+)"', empty.group(1)),
            knownFields=re.findall(r'"([^\"]+)"', fields.group(1)),
            scope="Locked source guard observation only; no Provider/Godot invocation.",
        ),
        execution=dict(
            hostCommit=profile["host_commit"],
            receipt=receipt,
            scope=evidence["scope"],
            checks=[{k: c[k] for k in ["id", "status", "exit_code"]} for c in checks],
            rowCertification="UNVERIFIED_CURRENT_HOST",
            reportedHarnessReportSha256=evidence["harness_report_sha256"],
        ),
        resolvedSelection=dict(
            instanceIds=selected,
            root=root,
            internalConnectionIds=[e["id"] for e in expected_edges],
        ),
        trustBoundary="Checks the supplied records' consistency. Immutable upstream custody supplies host provenance; a caller who forges and re-locks every record is not independently attested by this offline extractor.",
    )


def run_actual_profile(a):
    """Explicit locked host-result inventory; not a new compatibility verdict."""
    profile = json.loads(a.actual_profile.read_text())
    assert profile["profile"] == "actual-0.4.0", "UNKNOWN_ACTUAL_PROFILE"
    assert re.fullmatch(r"[0-9a-f]{40}", profile["host_commit"])
    assert re.fullmatch(r"[0-9a-f]{40}", profile["mapgen_commit"])
    assert (
        profile["generation_package_sha256"]
        == "7aa3f0e573675c3bb41e2a2a5b23254c4005bb8eaef9756535e3a6480988d778"
    )
    required = {
        "result",
        "provenance",
        "host_bindings",
        "protocol_payload",
        "host_provider",
        "host_source_snapshot",
        "validation_evidence",
    }
    assert set(profile["files"]) == required, "ACTUAL_INPUT_ROLES_MISMATCH"
    output = a.out.resolve()
    frozen = (ROOT / "evidence/runtime-integration-930001").resolve()
    assert output != frozen and frozen not in output.parents, "REFUSE_FROZEN_OUTPUT"
    assert not a.out.exists(), "ACTUAL_OUTPUT_MUST_BE_NEW"
    data = {}
    for role, row in profile["files"].items():
        relative = Path(row["path"])
        assert not relative.is_absolute() and ".." not in relative.parts
        path = (a.inputs / relative).resolve()
        assert path.is_relative_to(a.inputs.resolve()), "ACTUAL_INPUT_OUTSIDE_ROOT"
        raw = path.read_bytes()
        assert sha(raw) == row["sha256"], (role, "ACTUAL_INPUT_SHA_MISMATCH")
        data[role] = raw
    result = json.loads(data["result"])
    provenance = json.loads(data["provenance"])
    assert (
        result["status"] == "PASS" and result["schema"] == "mapgen/generation-result/v1"
    )
    assert provenance["kind"] == "generated_memory", "NOT_ACTUAL_HOST_MEMORY_SOURCE"
    implementation = "mapgen/gdscript-candidate-0.4.0"
    algorithm = "stable-v3-reward-space"
    assert (
        provenance["implementation"] == implementation
        and provenance["algorithm"] == algorithm
    )
    assert (
        provenance["module_archive"]["sha256"] == ZIP110
        and provenance["module_archive"]["version"] == "1.1.0"
    )
    assert (
        provenance["algorithm_package"]["zip_sha256"]
        == profile["generation_package_sha256"]
    )
    assert (
        provenance["algorithm_package"]["source_commit"]
        == "b21c889077ec97eb11a210d0ceab4fbddd862e48"
    )
    assert provenance["algorithm_package"]["release_head"] == profile["mapgen_commit"]
    # Exact bytes emitted by the ORIGINAL GDScript DATA.canonical call. Never
    # reimplement its numeric/canonical rules in this Python audit producer.
    fingerprint = sha(data["protocol_payload"])
    assert (
        fingerprint
        == provenance["expected_request_fingerprint"]
        == result["request_fingerprint"]
    )
    assert json.loads(data["protocol_payload"]) == {
        "request": provenance["request"],
        "config": provenance["config"],
        "library_sha256": ZIP110,
        "implementation": implementation,
    }
    reference, store = result["map"], result["content_store"]
    assert reference["schema"] == "mapgen/runtime-map/v2"
    assert reference["seed"] == provenance["request"]["seed"]
    assert reference["generator"]["implementation"] == implementation
    assert reference["generator"]["algorithm"] == algorithm
    assert reference["generator"]["request_fingerprint"] == fingerprint
    assert (
        reference["module_package"]["sha256"] == ZIP110
        and reference["module_package"]["version"] == "1.1.0"
    )
    instances = {i["id"]: i for i in reference["instances"]}
    assert len(instances) == len(reference["instances"]), "DUPLICATE_ACTUAL_INSTANCE_ID"
    assert len({c["id"] for c in reference["connections"]}) == len(
        reference["connections"]
    )
    for edge in reference["connections"]:
        for end in (edge["a"], edge["b"]):
            instance = instances[end["instance_id"]]
            assert end["port_id"] in {p["id"] for p in instance["ports"]}
    with pinned_zip(a.zip110, ZIP110) as package:
        catalog = {
            e["id"]: e for e in json.loads(package.read("catalog.json"))["modules"]
        }
        validate_actual_store(reference, store, catalog, package)
        index, groups, instances = extract_inventory(
            reference, store, catalog, current_host=True
        )
    assessment = bind_host_records(data, profile, reference, store, fingerprint)
    admission = {}
    for kind, rows in groups.items():
        field = rows[0]["fieldPath"].split("[")[0]
        if field not in assessment["provider"]["knownFields"]:
            status = "FIELD_NOT_IN_LOCKED_PROVIDER_ALLOWLIST"
        elif field in assessment["provider"]["explicitlyEmptyFields"] or (
            field == "approved_hq_cells"
            and "approved_hq_cells: unsupported nonempty content"
            in data["host_provider"].decode()
        ):
            status = "REQUIRES_EMPTY_IN_LOCKED_PROVIDER"
        else:
            status = "FIELD_AVAILABLE_SUBSEQUENT_CONVERSION_AND_EXECUTION_NOT_CHECKED"
        admission[kind] = dict(
            field=field,
            observation=status,
            currentHostExecution="UNVERIFIED_CURRENT_HOST",
        )
    assessment["adapterObservationsByGroup"] = admission
    # Preserve complete local instance/port/connection context. Across versions
    # consumers must match module_id+content_version+role+topology, not M IDs.
    coverage = dict(
        hostCommit=profile["host_commit"],
        mapGenCommit=profile["mapgen_commit"],
        modulePackageVersion="1.1.0",
        moduleIndex=index,
        groups=groups,
        interfaceCoverage=dict(
            anchors=reference["anchors"],
            instances=reference["instances"],
            connections=reference["connections"],
        ),
        hostBindings=json.loads(data["host_bindings"]),
        source="actual locked host result; extraction only; all current host statuses UNVERIFIED",
        inputProfile=profile,
        inputProfileSha256=sha(a.actual_profile.read_bytes()),
        resultReceiptSha256=sha(data["result"]),
        generationInputFingerprint=fingerprint,
        validationEvidence=dict(
            source=profile["files"]["validation_evidence"],
            status="UNVERIFIED_NOT_INTERPRETED",
        ),
        hostSourceSnapshot=dict(
            source=profile["files"]["host_source_snapshot"],
            status="LOCKED_BYTES_NOT_COMMIT_ATTESTATION",
        ),
        assessment=assessment,
    )
    write(a.out / "mechanism-coverage.json", coverage)
    print(
        json.dumps(
            dict(
                instances=len(instances),
                uniqueModules=len(index),
                connections=len(reference["connections"]),
                groups={k: len(v) for k, v in groups.items()},
                scope="inventory_only_not_host_certification",
            )
        )
    )


# The old CLI, guards, output paths and default behavior below are unchanged.
if __name__ == "__main__":
    import sys

    if any(
        arg == "--actual-profile" or arg.startswith("--actual-profile=")
        for arg in sys.argv[1:]
    ):
        actual = argparse.ArgumentParser(
            description="Explicit 0.4 host-result inventory; no generation or certification"
        )
        actual.add_argument("--actual-profile", required=True, type=Path)
        actual.add_argument("--inputs", required=True, type=Path)
        actual.add_argument("--zip110", required=True, type=Path)
        actual.add_argument("--out", required=True, type=Path)
        run_actual_profile(actual.parse_args())
        raise SystemExit(0)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inputs", required=True, type=Path)
    p.add_argument("--zip110", required=True, type=Path)
    p.add_argument("--zip111", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    run(p.parse_args())
