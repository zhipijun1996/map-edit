# Current Module production

The sole editable source is `modules/<stable-ID>/`. Read `record.json` first. An implemented ID has one `module.mapnote.json`; a design in development has one `design.json`. `compiled-content.json`, `module.tscn`, `godot-package.json`, `thumbnail.svg`, `modules/catalog.json` and workshop data are generated. `validation/` contains current offline test inputs and is excluded from runtime distribution. A withdrawn directory contains only its ID record.

The current state is generated into `modules/catalog.json.counts`; do not maintain another hand-edited keep/discard list. `review.decision` records design retention, `implementationApproval` records implementation review, `qualification` binds native route evidence, and `runtime.deliveryStatus` distinguishes runtime delivery. A kept design without implementation remains present and never enters a package. `mapReady` stays false until separate seam/map qualification exists.

## Commands

Run from the repository root using Linux, Python 3.12+, Node 18+ and `strace`. The exact Godot 4.7.2 binary is hash-checked or installed in the user cache. A verified host cache avoids repeated downloads.

```sh
python3 -m module_pipeline add /path/to/design-or-module.json
python3 -m module_pipeline update STABLE_ID /path/to/revised-current-source.json
python3 -m module_pipeline review STABLE_ID --version sha256:CURRENT_VERSION --decision KEEP --note 'Exact version reviewed'
python3 -m module_pipeline qualify STABLE_ID --evidence /path/to/admission.json
python3 -m module_pipeline withdraw STABLE_ID --reason 'explicitly discarded' --replacement REPLACEMENT_ID
python3 -m module_pipeline index
npm run build:workshop
npm run check
npm run test:production
python3 -m module_pipeline validate-portable --host-source /path/to/locked-host
```

`add` allocates a UUID-based stable ID unless `--id` names an already reserved design identity; an existing ID (including withdrawn) is rejected. Designs are sealed and rendered by the existing renderer. Implemented input must declare Foundation v2 objects, native runtime bindings and internal host anchors. Missing bindings/Cells fail rather than creating a placeholder. Replacing a design with implementation uses `update` under the same ID. Updates invalidate implementation and portable approval. Gameplay or runtime-contract changes also invalidate route evidence; metadata-only changes may retain it through explicit content equivalence. Re-approval never recreates physics evidence.

All changes stage a complete next library, recompile affected content, regenerate its thumbnail and index, and validate before a single Linux `renameat2(RENAME_EXCHANGE)` directory exchange. A failed transaction leaves the prior library intact. Readers see a complete tree; browser catalog/hash mismatches during a refresh retain the prior snapshot and retry. Every ID has one version at rest. Manual changes to generated files are detected by checksums.

Withdrawal removes the source and runtime payload. Committed history is addressed by Git; uncommitted content is first saved in a content-addressed immutable `archives/modules/<ID>/<SHA>.zip`. A replacement is explicit. Builds iterate only current records, so old versions and withdrawn sources cannot be accidentally rediscovered.

## Changed-content qualification

Retain the existing native physics, fixed quality thresholds, causal validators and holdout discipline. Temporary experiment execution is distinct from the one editable source. Prepare exact current inputs at `modules/<ID>/validation/qualification/` (`module.mapnote.json`, `physics-input-cases.json`, `cases.json` and protocol/migration bindings). Run the existing `pcg.migration.physics` runner with current registered source/program/holdout inputs; it remains the native execution/verifier implementation. The retired migration catalog/promote CLI must not write the current library.

The admission JSON is a pointer to actual evidence, not a pass flag:

```json
{
  "schema": "map-edit/current-qualification-admission/v1",
  "id": "STABLE_ID",
  "sourceSha256": "CURRENT_MODULE_FILE_SHA256",
  "contentVersion": "sha256:CURRENT_CONTENT_VERSION",
  "report": {"path": "CURRENT_NATIVE_PHYSICS_REPORT", "sha256": "REPORT_SHA256"}
}
```

`qualify` calls the existing deep raw verifier: it hashes frozen source/input/execution bytes and re-applies causal, calibration, independent holdout, boundary/continuous-route and counterexample gates. Missing or mismatched inputs fail; an old report boolean cannot approve changed content. All declared routes must be covered. Native scoped qualification still requires portable acceptance before delivery. If the old runner lacks a Cell/adapter needed by a new design, keep that ID pending with a concrete gap; never label a preview or a single smoke test as full quality evidence.

## Versioned package

Commit source/tool/runtime changes before release. Build with:

```sh
python3 -m module_pipeline build --version 1.1.0
```

Use a new SemVer when contents change. This creates `releases/map-edit-modules-1.1.0.zip`, `.zip.sha256` and metadata JSON. It validates source/index/version/dependency integrity, refuses an empty release, installs exact upstream host dependencies, extracts a candidate ZIP into a clean directory, imports/runs the pinned real Godot and audits file reads with `strace`. Matching current acceptance evidence can be reused; `--revalidate` forces fresh acceptance. `--host-source PATH` is only an installation cache: every selected host file is hashed and copied into the clean project. Runtime does not read that cache or the authoring checkout.

The manifest has a source commit and checksums for every included file. ZIP member order, timestamps and permissions are fixed. A repeated build of the same committed inputs/version yields identical bytes; an existing version cannot be replaced with different bytes. A release built from a source commit remains reproducible by checking out that commit. Generated evidence/status updates can be committed afterward without retroactively changing the release's source identity.

Only qualified retained modules enter delivery. Pending designs and explicit exclusion reasons appear in the delivery catalog; withdrawn items do not enter its module set. Runtime files, current Module JSON/data/scenes/thumbnails, integration examples and pinned dependency locks are included. Raw traces, historical rounds, videos, old Harness workspaces and unrelated reports are excluded. The package is generated content, not a second authoring library.

To extend a pinned shared host dependency closure, use `python3 tools/production/refresh_host_lock.py --lock runtime/host-lock.json --cache /path/to/host-cache --source /path/to/locked-game-checkout`. It resolves literal/formatted resource prefixes against the fixed upstream Git tree, checks Git blob identities and writes explicit SHA256 entries. Changing a host lock or runtime adapter invalidates portable acceptance; old physical route evidence remains tied to its original host profile.

Editor copies now declare `modify_existing`; `update` resolves their local draft ID back to the explicit stable `source.moduleId` and removes inline baseline copies. Changes silently ignored by an unchanged native binding (for example a rock/platform type switch or unbound motion timing) fail with an object/field-specific error. Update the native binding/adapter explicitly, then qualify the changed behavior. Pure document metadata changes with byte-equivalent objects and an identical runtime/interface contract keep their old physics evidence through an explicit version-equivalence attestation; they still require implementation review and a fresh portable binding check.

The native verifier also checks canonical case Cells against the current compiled source before accepting evidence. Additional test-neighbor platforms must be outside the owned rectangle and explicitly declared in the admission's `testNeighborFixtures`, keyed by route ID. They are carried as route validation requirements and never inserted into a module scene. The three-enemy and relay-lift upper-exit cases retain their respective original external upper-platform conditions; arbitrary upper seams are not certified by those fixtures.

Current input policy templates stay under `validation/cases.json` after an update and are explicitly marked as needing a current-source check. Old frozen qualification working copies are removed from the current source. Editing never silently discards the retained input policy, and a stale template cannot qualify different compiled Cells.

## Required export rules for future production

Every build exports all existing native `reward_sites` verbatim and associates them through the existing Route `resourceProfile.requiredRewards`. Missing route metadata may be projected only from exact qualified canonical inputs, never guessed from geography. Unknown associations produce the generated `reward-association-gaps.json` and an identically generated release sidecar, not deleted modules or rewards. New source revisions must keep these native IDs and declare route requirements in their existing native case fields or Route profile.

Do not add `allow_mirror_x`, a mirror eligibility blacklist, mirrored module copies, or a full-Port connection whitelist. `runtime.configurations` / exported `configurations` retain tested witness scope only. map-gen mirrors complete content/Ports/Routes, chooses Port subsets, installs unused-Port gear closures and checks remaining routes. Preserve UNKNOWN for untested placements. This does not loosen physical evidence. Use `purpose` for explicit Boss purpose; derive `entryPortIds` from directed route starts and initial ingress permissions for every Module, without a second Boss route contract. These rules are enforced by the exporter, package verifier and focused production tests.
