"""Read-only check against map-gen's existing doubled-coordinate Port model."""

import argparse, importlib.util, json, sys
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from integration.map_gen_reader import (
    read_library,
    validate_placement,
    routes_for_abilities,
)


def check(bundle, model_file):
    templates = read_library(bundle)
    spec = importlib.util.spec_from_file_location("readonly_mapgen_model", model_file)
    model = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(model)
    catalog = json.loads((bundle / "catalog.json").read_text())
    entries = {e["id"]: e for e in catalog["modules"]}
    checks = 0
    for mid, t in templates.items():
        e = entries[mid]
        assert t["reward_sites"] == e["reward_sites"]
        assert "allow_mirror_x" not in t and "allowed_configurations" not in t
        all_ids = [p["id"] for p in t["ports"]]
        selected = all_ids[:1]
        assert (
            validate_placement(t, selected, mirror=True, closures=all_ids[1:]) == "base"
        )
        for mirror in [False, True]:
            placed = model.placed_ports(t, 7, -3, mirror)
            for p in e["ports"]:
                xy = p["position"]
                local = [
                    (xy[i] - e["bounds"][k]) / e["blockSize"]
                    for i, k in enumerate(["x", "y"])
                ]
                if mirror:
                    local[0] = e["sizeBlocks"][0] - local[0]
                expected = [2 * ([7, -3][i] + local[i]) for i in [0, 1]]
                assert placed[p["id"]]["world2"] == expected, (mid, p["id"], mirror)
                checks += 1
        if t["routes"]:
            route = t["routes"][0]
            profile = t["initial_configuration"].get("nativeFixture") or t[
                "initial_configuration"
            ].get("nativeTuning")
            usable = routes_for_abilities(
                t,
                route["required_abilities"],
                profile.get("id") if profile else None,
                connected_port_ids=selected,
                mirror=True,
            )
            assert all(
                r["validation"]["status"] == "UNKNOWN"
                and r["from_port"] in selected
                and r["to_port"] in selected
                for r in usable
            )
    return dict(
        schema="map-edit/map-gen-interface-acceptance/v1",
        passed=True,
        modules=len(templates),
        ports=sum(len(e["ports"]) for e in entries.values()),
        directedRoutes=sum(len(e["routes"]) for e in entries.values()),
        originalAndMirroredPortCoordinateChecks=checks,
        partialPortsAndMirrorAccepted=True,
        perModuleMirrorEligibilitySwitch=False,
        newConfigurationsRemainUnknown=True,
        consumerRepositoryModified=False,
        wholeMapCertification=False,
        wholeContentMirrorRuntimeCertification=False,
    )


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--package", required=True, type=Path)
    p.add_argument("--model", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    p.add_argument("--consumer-commit", required=True)
    a = p.parse_args()
    r = check(a.package, a.model)
    r["readOnlyConsumerCommit"] = a.consumer_commit
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(r, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(r))
