# Isolated continuous-map Godot consumer

These adapters load inside the existing `pcg/prototype/godot` project and extend
its unchanged `runner_plains.gd` / `main_plains.gd`. They do not implement physics,
move the player, replenish movement resources, remove hazards, or rebuild the
world between component traversals. The pinned runtime source remains
`12f6cb006d7119598e3235f4ca4f7323e4c9d092`; this is not the latest formal game's
consumer. `map_observer.gd` requests actual coin transactions through the original
`SimpleRoomReward`, `RunWallet` and `DemoLifetime` services.

The input is the existing raw Plains case format plus `map_semantics`:

```json
{
  "checkpoints": [
    {"id":"entry","region":[60,390,40,60],"grounded":true,"kind":"fork","label":"ENTRY"},
    {"id":"return_entry","region":[60,390,40,60],"grounded":true,"kind":"return","label":"RETURN"}
  ],
  "required_checkpoints": ["entry","return_entry"],
  "seams": [{"id":"join-01","region":[650,390,60,60],"from":"fork.B","to":"ascent.entry","crossing_direction":"right"}],
  "required_seams": ["join-01"],
  "rewards": [{"id":"upper-cache","region":[250,250,60,60],"amount":12}],
  "required_rewards": ["upper-cache"],
  "required_bells": ["fork/lift_bell", "ascent/lift_bell"]
}
```

`required_checkpoints` is an ordered route requirement. Different IDs may refer
to the same spatial region to prove a later return. The initial actual entry is
observed before Router receives its first action, including immediate jumps.
A visit at spawn cannot
satisfy the later required step. Checkpoints and seams report the actual velocity,
resources, grounded state and dynamic clock. A required seam must have a real
adjacent-frame crossing of its center plane (or explicit `crossing_x`), within
the seam region, grounded on both sides, stable HP and no new damage or return.
Its complete `before` / `after` state is retained. Merely entering the seam region
does not count as crossing. This observation is not a universal port transfer
guarantee. The reward is claimed only at an actual
supported contact inside its region; a main route may leave `required_rewards`
empty. The original transaction service owns idempotence, stale and terminal
rejection. No reward item is inferred from a node's graph label.

Run from the repository root, using absolute paths for input/output and scripts:

```sh
pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 \
  --headless --path pcg/prototype/godot --fixed-fps 60 \
  --script /absolute/repo/pcg/map_directed/godot/map_runner.gd -- \
  --input=/absolute/cases.json --output=/absolute/results.json
```

The original batch completion marker and schema remain. Each result additionally
contains `map_validation`; final `ok` also requires its ordered checkpoints and
required reward transactions and actual `bell_open` events for `required_bells`.
Reaching the goal without the required mechanism interactions is not PASS.
All frames and original hazard/damage records are
preserved. This is a concrete-instance route result, not formal admission or a
proof for all inputs, phases, directions and player builds.

For interactive manual control:

```sh
DISPLAY=:103 pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64 \
  --path pcg/prototype/godot --resolution 1600x900 \
  --script /absolute/repo/pcg/map_directed/godot/map_boot.gd -- \
  --cases-json /absolute/replay_cases.json --case 0
```

The native scene supports A/D, Space and the original mouse-release shooting.
`--replay` consumes recorded real Router inputs. `--movie` implies replay and
quits after completion plus a declared one-second frozen completion hold; pass
`--trace-json /absolute/native-trace.json` to save the actual per-frame replay.
Use Godot's `--write-movie /absolute/movie.avi` before the `--` separator for
native rendering, then encode it without changing playback speed. Validate the
native trace against the corresponding headless concrete map result.

For a full-map PNG, use the same GUI command with:

```sh
--whole-map /absolute/whole-map.png --quit-after-capture
```

This freezes after startup and changes only the camera to fit the actual world
bounds. It never moves the player to obtain the screenshot. The output is an
actual rendered Godot world, not an abstract graph visualization.

Source freezing must explicitly include this directory: the existing
`PlainsEngine` source list does not automatically discover these external scripts.
The adapters do not alter `assemblyInterface` or turn the public contracts'
UNKNOWN seams, transforms or state guarantees into PASS.
