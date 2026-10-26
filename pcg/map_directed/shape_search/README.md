# Real-shape spatial search, isolated experiment v1

This extends PR #1's existing canonical Module reader, Mission/Exploration
graph, direct-contact assembler, exact-geometry audit, Router pilot and Godot
Harness. It does not replace production generation.

`catalog.load` reloads eight actual Macro documents and their source-bound
physics trajectories. It removes all old placements before handing candidates
to `search`. Only two terminal banks have finite, pre-authored width/height
variants; action cores are not stretched. Reflections preserve gravity. A
variant whose saw sweep leaves its declared core is rejected before search.
New variants remain UNKNOWN for general reuse and are not production entries.

`search.search` is a bounded deterministic CSP. It prioritizes nodes that close
existing cycles, aligns actual local ports, checks normals and body apertures,
then tests collider unions, closed doors, saw sweeps and sampled body-action
clearances. One-way surfaces retain their different collision semantics.
Shared landings may overlap only when both ports explicitly own the same seam.
An AABB is not the shape. No corridor/floor is synthesized by the Map layer.

The current motion relation requires a grounded dock, recovered air shot,
zero cooldown and speed <= 1. The actual whole-world pilot checks these on
every Module entry; it never refills resources or relocates the actor.
This first prototype does not solve arbitrary high-speed airborne port
relations. Parent trajectory samples are a conservative screening aid, not a
physical proof for changed shapes. Fresh continuous whole-map tests are final.

`protocol.json` fixes calibration/evaluation Seeds, variants, search budget,
selection rule and independent perturbations. No held-out failure may be used
to select a replacement Seed or repair that same held-out batch. All failed
builds, calibration attempts and their actual source snapshots are retained.

Run from repository root after restoring the existing ecosystem archive:

```sh
python -m unittest pcg.map_directed.tests.test_shape_search -v
python -m pcg.map_directed.shape_search.run --name shape-my-new-run --seed shape-eval-0 --held
python -m pcg.map_directed.direct_join.record --run pcg/results/shape-my-new-run --index 2 --out generation/maps/shape-my-new-movie --renderer pcg/map_directed/shape_search/visual.gd
```

The recorder needs the existing Xvfb display and frozen official engine. The
native video is compared frame by frame against its specific physical run.
`web_build` extends the existing formal overlay packer, adding current main's
grounded scenery, local composition, lighting and foreground closure. All are
read-only consumers of actual terrain and keep-clear data.

The fixed two-loop graph is deliberately constant in this experiment. Mirror,
bank size and bank height changes must not be presented as new exploration
topologies. Same-catalog AABB and shape-only ablations test feasibility and
constraint contribution; they cannot establish human enjoyment. Historic
19-Macro runs and the formal game differ in content budget and are context,
not fair physical-time controls. Human quality approval remains outstanding.

Frozen inputs and output recovery: restore `shape-search-calibration-v1`,
`shape-search-source-v1`, and `shape-search-results-v1` with the existing
`pcg/tools/restore_archive.py`. The base runtime and parent source catalog
also require the existing `godot-runtime-v1` and `content-ecosystem-v1` archives.
Large transient PCK files are removed locally only after exact archive and
public-byte verification; restoring the results archive restores those bytes.
Media copies are under `pcg/results/shape-search-review-payload-v1/shape-search-v1`.

To reconstruct missing native presentation additions, take the corresponding
`physics/source_snapshot` and `physics/source_binding.json` from eval0 in the
source archive. For each `source_files` entry, verify the snapshot SHA, copy
only missing files to `pcg/<relative path>`, and reject an existing different
file. This includes the exact source images/audio and `.import` metadata.
Then run the official Godot import once. Never overwrite changed protected
sources or substitute a different runtime baseline to make a replay pass.
See `docs/l4-mapgen/real-shape-search-v1.md` for the complete negative result,
paired controls, archive identities and public deliverables.
