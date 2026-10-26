# Plains50 enemy-world content

Eight new spatial-demand candidates reuse four existing causal relationships. They add no movement ability or newly claimed action family. Original `production_loop`, Godot actors/Cells, calibration policy, counterexample handling, standard export and persistent CandidateLibrary remain authoritative. All eight are two-port, entry→exit scoped candidates; reverse, continuous retry and map seams remain UNKNOWN.

The two interfaces are concrete authored demands, not a blind external generalization test: attack-relay has two exposed ingress/corridor lengths; absorber-bell has two actual bell/gate/receiver distances; live enemy occupancy has two ingress/receiver distances; displacement has230/180-unit entry drops. At most four control choices per interface and two rule revisions were used. Geometry/control changes require new evidence.

`rules_v1.py` and `probe_v1.py` preserve28 first-stage probes. `rules_v2.py` repairs relay visibility and binds actual reward transaction regions to moved rewards. The original source-bound errors and repair are recorded in `pcg/feedback/workshop/plains50-enemy-pilot-v1.json`; old source snapshots and all failed trials remain in raw results. There is no copied or reset enemy health, physics bypass, or fabricated human approval.

From repository root:

```sh
# Generate or retrieve exact two-interface requirements through the original loop.
python3 -m pcg.prototype.creative_batches.plains50_enemy.produce_v2 --name-prefix workshop-plains50-enemy-reuse-check
# One family can be selected with --recipe attack-relay (or the other three names).
# Existing exact library matches reuse evidence without new physics.

# Fresh-process retrieval of all eight, wrong-demand rejection and publication.
# Uses an immutable output directory; run once in a fresh restored checkout.
python3 -m pcg.prototype.creative_batches.plains50_enemy.audit_v1
```

Physical experiment reproduction uses `produce_v2.py` in a fresh worktree before restoring enrolled candidates; names must be fresh and the original Godot runtime must be available. The exact source, input, commands, output and failures are under `pcg/results/workshop-plains50-enemy-probe-v1-*` and `pcg/results/workshop-plains50-enemy-r2-*`.

Strict representative recording uses `record_v1.py <recipe> --display :112`; it creates a new immutable output directory. Do not run it over existing media. The unchanged native scene `pcg/prototype/creative_batches/enemy_world/main_v2.tscn` installs the real attack/occupancy Cells and also supports manual play. The default workshop scene cannot install these special bindings.

No human has reviewed these eight candidates. The current Codex subagent has inspected one sampled frame from each of the four representative films; complete subjective video review is pending. Representative films are real1×native60Hz replays, not human playtests.

## Unified fifty-item catalog launcher

```sh
python3 -m pcg.prototype.creative_batches.plains50_catalog --list
python3 -m pcg.prototype.creative_batches.plains50_catalog --play P01
python3 -m pcg.prototype.creative_batches.plains50_catalog --play P41 --route reward
python3 -m pcg.prototype.creative_batches.plains50_catalog --play P01 --replay
```

Use the actual IDs/routes displayed by `--list`; the examples above depend on the aggregate manifest. `--manifest` can point to this folder's `catalog-fixture-v1.json` for the eight enemy-world entries. Multiport entries require an explicit route. `--quit-after 4` limits startup smoke by wall-clock seconds and uses Dummy audio; it does not assert a human playtest or new physics validation. Original record, document and cases byte hashes plus bound scene hash are checked before launching an unchanged case copy in a fresh results directory.
