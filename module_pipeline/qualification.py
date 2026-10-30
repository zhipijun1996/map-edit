"""Admit changed content only after re-deriving existing native quality evidence.

A caller-authored pass flag is insufficient. The original verifier hashes raw
executions and re-applies route, holdout, boundary and causal acceptance gates.
"""

from pathlib import Path
from . import library as l


def verify_case_geometry(doc, cases, declared_neighbors=None):
    """The raw native executions must use this Module's actual compiled Cells."""
    from .bindings import equal

    data = l.physical_data(doc)
    bounds = doc["generationContract"]["space"]["bounds"]
    fixtures = {}
    for case in cases:
        route = case["route_spec"]["id"]
        native = data["platforms"]
        actual = case.get("platforms", [])
        if len(actual) < len(native) or not equal(actual[: len(native)], native):
            raise ValueError(
                "qualification_case_geometry_mismatch:" + route + ":platforms"
            )
        extra = actual[len(native) :]
        for x, y, w, h in extra:
            if (
                x < bounds["x"] + bounds["w"]
                and x + w > bounds["x"]
                and y < bounds["y"] + bounds["h"]
                and y + h > bounds["y"]
            ):
                raise ValueError("qualification_fixture_overlaps_owned_space:" + route)
        own_flags = [
            int(i)
            for i in case.get("one_way_platform_indices", [])
            if int(i) < len(native)
        ]
        if own_flags != data.get("one_way_platform_indices", []):
            raise ValueError(
                "qualification_case_geometry_mismatch:"
                + route
                + ":one_way_platform_indices"
            )
        if extra:
            fixtures[route] = extra
        for key, value in data.items():
            if key in ["platforms", "one_way_platform_indices"]:
                continue
            if not equal(case.get(key, [] if isinstance(value, list) else None), value):
                raise ValueError(
                    "qualification_case_geometry_mismatch:" + route + ":" + key
                )
    if declared_neighbors is not None and not equal(fixtures, declared_neighbors):
        raise ValueError("qualification_neighbor_fixture_declaration_mismatch")
    return fixtures


def admit(identifier, evidence):
    identifier = l.safe_id(identifier)
    folder = l.MODULES / identifier
    r = l.read(folder / "record.json")
    request = l.read(evidence)
    if r.get("source", {}).get("kind") != "module":
        raise ValueError("implemented_current_module_required")
    if (
        request.get("schema") != "map-edit/current-qualification-admission/v1"
        or request.get("id") != identifier
    ):
        raise ValueError("current_qualification_admission_required")
    if (
        request.get("sourceSha256") != r["source"]["sha256"]
        or request.get("contentVersion") != r["source"]["contentVersion"]
    ):
        raise ValueError("qualification_does_not_bind_current_source")
    working = (folder / "validation/qualification").resolve()
    if (
        not (working / "module.mapnote.json").is_file()
        or l.sha(working / "module.mapnote.json") != r["source"]["sha256"]
    ):
        raise ValueError("missing_exact_current_qualification_working_inputs")
    doc = l.read(folder / "module.mapnote.json")
    cases = l.read(working / "physics-input-cases.json")["cases"]
    neighbors = verify_case_geometry(
        doc, cases, request.get("testNeighborFixtures", {})
    )
    # These are the existing independent physics/causal verifiers, not a replacement simulation.
    from pcg.migration import physics, core

    proof = request["report"]
    report = physics.verify_report(working, proof, deep=True)
    if report.get("passed") is not True:
        raise ValueError("native_quality_report_failed")
    doc = l.read(folder / "module.mapnote.json")
    routes = {v["id"] for v in doc["generationContract"]["routes"]}
    if routes != {v["routeId"] for v in report["routes"]} or not all(
        v["passed"] for v in report["routes"]
    ):
        raise ValueError("incomplete_native_route_qualification")
    cases = l.read(working / "physics-input-cases.json")["cases"]
    caps = {c["route_spec"]["id"]: c["capabilities"] for c in cases}

    def change():
        current = l.MODULES / identifier
        record = l.read(current / "record.json")
        if record["source"]["sha256"] != request["sourceSha256"]:
            raise ValueError("source_changed_during_qualification")
        record["qualification"] = dict(
            status="verified_scoped",
            physicalSignature=record["runtime"]["physicalSignature"],
            routeIds=sorted(routes),
            availableAbilitiesByRoute=caps,
            originalReportSha256=proof["sha256"],
            actualAttempts=report["actualAttempts"],
            testNeighborFixtures=neighbors,
            scope="Existing native full quality verifier re-derived actual current raw executions; arbitrary Map seams/configurations remain UNKNOWN.",
        )
        record["runtime"].update(
            deliveryStatus="pending_portable_validation",
            portableValidation=None,
            configurations=[
                dict(
                    id="original-all-ports",
                    orientation="identity",
                    mirrorX=False,
                    connectedPortIds=[
                        p["id"] for p in doc["generationContract"]["ports"]
                    ],
                    relocations=[],
                    closures=[],
                    routeIds=sorted(routes),
                )
            ],
        )
        record["gaps"] = []
        record.setdefault("history", {})["currentQualificationEvidence"] = proof
        l.write(current / "record.json", record)

    l.transaction(change)
    return dict(
        id=identifier, status="verified_scoped", portableValidation="still_required"
    )
