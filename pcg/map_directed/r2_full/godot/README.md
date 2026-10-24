# Complete-R2 input-only headless consumer

`r2_runner.gd` extends the existing pinned `runner_plains.gd` fixture and original
Node scheduling. The short-module runner, original motion/resource components
and the earlier single-fork experiment are unchanged. This consumer accepts an
explicit long-map budget of at most 36,000 physical ticks.

Use the existing raw Plains case geometry and basic capabilities, plus:

```json
{
  "map_budget_ticks": 18000,
  "extra_script": "/absolute/path/to/state_extra.gd",
  "pilot_program": [{
    "id": "e7-jump-01",
    "edge_id": "e7",
    "kind": "jump",
    "budget_ticks": 360,
    "target": {
      "position": [400, 250],
      "region": [388, 245, 24, 10],
      "support_indices": [32],
      "grounded": true,
      "stable_ticks": 3
    }
  }]
}
```

Coordinates denote actual player-body center positions, not feet. Supports are
global indices in this concrete case's `platforms` array. At arrival, all three
actual left/center/right foot rays must hit the specified support set with upward
normals; XY region, grounded state and low actual velocity must also remain
valid for the declared stable ticks. The collision body's actual shape supplies
the ray offsets.

- `walk` steers using the original Router axis.
- `jump` submits one original jump and a later jump_release, using the actual
  tuning for its default hold duration. Optional `hold_ticks` is explicit.
- `drop` submits original drop_through; if the actor actually lands on an
  intermediate one-way floor above the target, it may repeat within the same
  leg budget, at most `maximum_drop_attempts` (default8, maximum16). It cannot
  fall through solid floors or manufacture support.
- `module` uses the existing finite `control_plan` interpreter, with original
  aim/phase queries and noise handling. Optional `entry` may declare a region,
  support set, grounded condition, required_air_shots and maximum_shot_cooldown.
  On a leg change only input-policy bookkeeping is reset; world clocks, doors,
  position, velocities and action resources are preserved.

Cell legs are bounded to360 ticks; explicit module legs retain the original
maximum3600. Every leg also consumes the one global map budget. Failure records
the leg ID, edge ID, expected target and actual state. A wrong-floor landing is
not an arrival. Landing partly on the target platform can continue to its safe
center; successful arrival still requires full foot support.

The optional extra instance is produced by `make_extra(case)`, overridable by a
subclass, or by the explicit `extra_script` path. Its hooks are:

```text
setup(case, world, controller, context)
before_leg(leg, actual_state) -> {ok, reason}     # optional
capture(frame, actual_frame_state)              # optional; may return event delta
report() -> {ok, ...}                           # final additional requirements
```

Without an extra, `extra_required=true` is rejected. Gate/reward state is not
invented by the pilot. An extra must use the actual supported runtime services
and record its own scoped evidence.

From the repository root:

```sh
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 \
  --headless --path pcg/prototype/godot --fixed-fps 60 \
  --script /absolute/repo/pcg/map_directed/r2_full/godot/r2_runner.gd -- \
  --input=/absolute/cases.json --output=/absolute/results.json
```

The original batch completion marker remains for the existing Engine adapter.
Each result includes `pilot.legs` start/end actual states, `pilot.failure`, the
extra's final report, original damage and Cell records, and complete Router-input
frames. Per-frame Cell events are deltas; cumulative leg and mechanism histories
are only emitted once at the end. This avoids copying an entire exploration
history into every physics frame.

Freeze this directory and the chosen extra script in the owning experiment's
source snapshot. A map policy pass proves only that actual tested route, entry
state and phase in the one instantiated full world. Other directions, unvisited
edges, arbitrary states, player fun and production eligibility remain separate.
