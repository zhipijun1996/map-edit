"""Project existing Cells and route evidence; never infer rewards from geometry."""

import copy
from . import library as l
from .qualification import verify_case_geometry


def project_routes(folder, doc, record, compiled):
    sites = compiled.get("reward_sites", [])
    cases = []
    admitted = folder / "validation/qualification/physics-input-cases.json"
    case_file = (
        admitted
        if record.get("history", {}).get("currentQualificationEvidence")
        and admitted.is_file()
        else folder / "validation/cases.json"
    )
    if sites and case_file.is_file():
        cases = l.read(case_file)["cases"]
        verify_case_geometry(
            doc, cases, record["qualification"].get("testNeighborFixtures", {})
        )
    routes = copy.deepcopy(doc["generationContract"]["routes"])
    for route in routes:
        profile = route.setdefault("resourceProfile", {})
        witnesses = [
            c for c in cases if c.get("route_spec", {}).get("id") == route["id"]
        ]
        declared = [c["required_rewards"] for c in witnesses if "required_rewards" in c]
        if declared and any(v != declared[0] for v in declared):
            raise ValueError(
                "conflicting_reward_witnesses:" + record["id"] + ":" + route["id"]
            )
        if "requiredRewards" in profile:
            if declared and profile["requiredRewards"] != declared[0]:
                raise ValueError(
                    "route_reward_evidence_mismatch:" + record["id"] + ":" + route["id"]
                )
        elif declared:
            profile["requiredRewards"] = copy.deepcopy(declared[0])
        elif not sites:
            profile["requiredRewards"] = []
    return routes


def purpose(doc, folder):
    if doc.get("purpose"):
        return doc["purpose"]
    path = folder / "validation/cases.json"
    families = (
        {v.get("family") for v in l.read(path)["cases"]} if path.is_file() else set()
    )
    # These are existing native family names, not guesses from a title or ID.
    if "original-game-plains_boss_arena" in families:
        return "boss_arena"
    if "original-game-boss_approach" in families:
        return "boss_approach"
    return doc.get("summary", doc.get("title"))


def entry_port_ids(ports, routes):
    ingress = {p["id"] for p in ports if p["permission"] != "OUTPUT"}
    return sorted({r["from"] for r in routes} & ingress)


def reward_gaps(entries):
    gaps = []
    for entry in entries:
        sites = {r["id"] for r in entry["reward_sites"]}
        linked = {
            rid
            for r in entry["routes"]
            for rid in r.get("resourceProfile", {}).get("requiredRewards", [])
        }
        unknown = (
            [
                r["id"]
                for r in entry["routes"]
                if "requiredRewards" not in r.get("resourceProfile", {})
            ]
            if sites
            else []
        )
        if sites - linked or unknown:
            gaps.append(
                dict(
                    id=entry["id"],
                    title=entry["title"],
                    rewardIdsWithoutConfirmedRoute=sorted(sites - linked),
                    routesWithoutRewardAssociation=unknown,
                    reason="No retained qualified route explicitly requires these rewards. Empty requiredRewards does not prove an optional reward is uncollectible; no association is invented. Module and rewards remain in the package.",
                )
            )
    return dict(
        schema="map-edit/reward-association-audit/v1",
        modulesWithRewards=sum(bool(e["reward_sites"]) for e in entries),
        rewardSites=sum(len(e["reward_sites"]) for e in entries),
        modulesWithGaps=len(gaps),
        modules=gaps,
    )
