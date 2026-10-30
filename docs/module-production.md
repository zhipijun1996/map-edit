# Current Module production

The sole editable source is `modules/<stable-ID>/`. Read `record.json` first. An implemented ID has one `module.mapnote.json`; a design in development has one `design.json`. `compiled-content.json`, `module.tscn`, `godot-package.json`, `thumbnail.svg`, `modules/catalog.json` and workshop data are generated. `validation/` contains current offline test inputs and is excluded from runtime distribution. A withdrawn directory contains only its ID record.

The current state is generated into `modules/catalog.json.counts`; do not maintain another hand-edited keep/discard list. `review.decision` records design retention, `implementationApproval` records implementation review, `qualification` binds native route evidence, and `runtime.deliveryStatus` distinguishes runtime delivery. A kept design without implementation remains present and never enters a package. `mapReady` stays false until separate seam/map qualification exists.

## Commands

Run from the repository root using Linux, Python 3.11+, Node 18+ and `strace`. The exact Godot 4.7.2 binary is hash-checked or installed in the user cache. A verified host cache avoids repeated downloads.

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

`add` allocates a UUID-based stable ID unless `--id` names an already reserved design identity; an existing ID (including withdrawn) is rejected. Designs are sealed and rendered by the existing renderer. Implemented input must declare Foundation v2 objects, native runtime bindings and internal host anchors. Missing bindings/Cells fail rather than creating a placeholder. Replacing a design with implementation uses `update` under the same ID. Source updates invalidate implementation/route/portable evidence; re-approval never recreates physics evidence.

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
python3 -m module_pipeline build --version 1.0.0
```

Use a new SemVer when contents change. This creates `releases/map-edit-modules-1.0.0.zip`, `.zip.sha256` and metadata JSON. It validates source/index/version/dependency integrity, refuses an empty release, installs exact upstream host dependencies, extracts a candidate ZIP into a clean directory, imports/runs the pinned real Godot and audits file reads with `strace`. Matching current acceptance evidence can be reused; `--revalidate` forces fresh acceptance. `--host-source PATH` is only an installation cache: every selected host file is hashed and copied into the clean project. Runtime does not read that cache or the authoring checkout.

The manifest has a source commit and checksums for every included file. ZIP member order, timestamps and permissions are fixed. A repeated build of the same committed inputs/version yields identical bytes; an existing version cannot be replaced with different bytes. A release built from a source commit remains reproducible by checking out that commit. Generated evidence/status updates can be committed afterward without retroactively changing the release's source identity.

Only qualified retained modules enter delivery. Pending designs and explicit exclusion reasons appear in the delivery catalog; withdrawn items do not enter its module set. Runtime files, current Module JSON/data/scenes/thumbnails, integration examples and pinned dependency locks are included. Raw traces, historical rounds, videos, old Harness workspaces and unrelated reports are excluded. The package is generated content, not a second authoring library.
