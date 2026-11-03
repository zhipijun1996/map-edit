"""Read-only, commit-pinned downstream source/locked-host comparison (requires gh)."""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from check_inputs import checked_zip, sha, write

GAME = "30e36c9abe223f26e666ceaf796e3fe9cb58e10f"
MAPGEN = "178c40164c2f7371ce1c8a56cde658e84a4f42c2"
GEN_FILES = [
    "mapgen/assembly.py",
    "mapgen/geometry.py",
    "mapgen/export.py",
    "mapgen/library.py",
    "profiles/stable-v2.json",
    "examples/request-930001.json",
]
GAME_FILES = [
    "config/player_tuning.json",
    "game/player/player_controller.gd",
    "game/player/player.tscn",
    "game/combat/damage/frame_damage_policy.gd",
    "game/world/state/demo_lifetime.gd",
    "game/economy/shops/run_wallet.gd",
    "game/world/components/shot_latch.gd",
    "game/rewards/grants/simple_room_reward.gd",
    "game/rewards/offers/simple_reward_definition.gd",
]


def api(path):
    return json.loads(subprocess.check_output(["gh", "api", path]))


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def tree(repo, commit):
    root = api(f"repos/zhipijun1996/{repo}/git/commits/{commit}")["tree"]["sha"]
    result = api(f"repos/zhipijun1996/{repo}/git/trees/{root}?recursive=1")
    assert not result.get("truncated"), "TRUNCATED_TREE"
    return root, {x["path"]: x["sha"] for x in result["tree"] if x["type"] == "blob"}


def sources(repo, commit, paths, blobs, folder):
    hashes = {}
    for name in paths:
        data = subprocess.check_output(
            [
                "gh",
                "api",
                "-H",
                "Accept: application/vnd.github.raw+json",
                f"repos/zhipijun1996/{repo}/contents/{name}?ref={commit}",
            ]
        )
        assert git_blob(data) == blobs[name], name
        target = folder / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        hashes[name] = sha(data)
    return hashes


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip", type=Path, required=True)
    p.add_argument("--sha256", required=True)
    p.add_argument("--native-cache", type=Path, required=True)
    p.add_argument("--api-cache", type=Path, required=True)
    p.add_argument(
        "--sources",
        type=Path,
        required=True,
        help="External audit scratch directory; never a production source tree",
    )
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    z, _ = checked_zip(a.zip, a.sha256)
    game_root, game = tree("gunman-rush", GAME)
    gen_root, gen = tree("map-gen", MAPGEN)
    rows = []
    for name, cache in [
        ("host-lock.json", a.native_cache),
        ("host-lock-current-game.json", a.api_cache),
    ]:
        lock = json.loads(z.read("runtime/" + name))
        same, changed = [], []
        for path, digest in lock["files"].items():
            data = (cache / path).read_bytes()
            assert sha(data) == digest, "LOCKED_CACHE_MISMATCH:" + path
            blob = git_blob(data)
            if game.get(path) == blob:
                same.append(path)
            else:
                changed.append(
                    dict(path=path, currentGitBlob=game.get(path), lockedGitBlob=blob)
                )
        rows.append(
            dict(
                lock=name,
                lockedCommit=lock["commit"],
                currentGameCommit=GAME,
                byteIdenticalFiles=len(same),
                changedOrAbsentFiles=changed,
                cacheMissingFiles=[],
                scope="Git blob byte comparison only; changed bytes do not imply API incompatibility, identical subset does not certify a whole game.",
            )
        )
    gen_hashes = sources("map-gen", MAPGEN, GEN_FILES, gen, a.sources / "map-gen")
    game_hashes = sources(
        "gunman-rush", GAME, GAME_FILES, game, a.sources / "gunman-rush"
    )
    write(
        a.out,
        dict(
            mapGenCommit=MAPGEN,
            mapGenTree=gen_root,
            mapGenReadOnlySourceSha256=gen_hashes,
            gameCommit=GAME,
            gameTree=game_root,
            currentGameReadOnlySourceSha256=game_hashes,
            hostLockComparison=rows,
        ),
    )
    print(
        json.dumps(
            dict(
                gameCommit=GAME,
                mapGenCommit=MAPGEN,
                verifiedSourceFiles=len(gen_hashes) + len(game_hashes),
                locks=len(rows),
            )
        )
    )


if __name__ == "__main__":
    main()
