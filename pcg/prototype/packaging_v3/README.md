# Immutable base + small overlay preview

This helper keeps the already published 68,213,164-byte PCG-02 PCK unchanged. A
new independently identified primary PCK boots without game-specific preloads,
verifies the complete base SHA256, mounts it with `replace_files=false`, and then
loads the requested scene. The official 4.7.2 JavaScript/WASM/audio transport is
also shared at immutable existing URLs. No service worker is installed.

The `overlay_pack.py` writer emits unencrypted Godot format 4 and checks every
entry with the game's existing `tools/check_web_bundle.py::Pack`. Container
validity alone is not a runtime result: the browser proof must also pass.

```sh
python3 prototype/packaging_v3/overlay_pack.py \
  --extra-dir delivery/dynamic-v3/packaging-new-resources \
  --scene res://main_v3.tscn \
  --out delivery/dynamic-v3/packaging-new-build
```

`--extra-dir` mirrors `res://`: for example, `main_v3.gd`, `main_v3.tscn`,
`dynamic_context.gd`, and `modules_v3.json`. Use unique new script/scene paths;
an existing base `.gd.remap` can otherwise redirect a same-name plaintext script
to its old `.gdc`. New global `class_name` declarations additionally require the
fresh project `.godot/global_script_class_cache.cfg` in the overlay. Existing
base global classes and UIDs are available from the byte-identical copied cache.
Ordinary preload-by-path helper scripts do not require a new global class name.

Alternatively, pass `--full path/to/new-full-export.pck`: every new/changed entry
is copied by actual bytes, while unchanged entries remain in the base. The full
`project.binary` is deliberately excluded so startup uses the isolated bootstrap
settings instead of parsing the game scene before its assets are mounted. The
bootstrap settings preserve 1280×720, 60 physics Hz, GL Compatibility. The base
font is applied after mounting rather than duplicating its 1.5 MiB import.

The base pack is fetched with the official `Engine.preloadFile(url, '/base.pck')`
before `startGame()`. The browser's virtual filesystem file is read by Godot;
`ProjectSettings.load_resource_pack('/base.pck', false)` keeps all primary overlay
files authoritative. The base pack's project configuration is not reloaded.

Local same-origin verification does not modify any hosting folder:

```sh
python3 prototype/packaging_v3/serve_proof.py \
  --proof delivery/dynamic-v3/packaging-proof-v4 --port 8042
python3 prototype/packaging_v3/browser_proof.py \
  http://127.0.0.1:8042/ delivery/dynamic-v3/packaging-browser-new-check
```

The proof overrides `modules_v2.json` with first candidate ID
`overlay-proof-new-id`. A passing check requires that ID, all 20 base candidates,
the exact base-mount log, the new boot request, and a real replay-button input
reaching a safe stable exit. It does not prove new dynamic gameplay.

The V4 transport proof passed in Chromium with the real official Web engine:
20 base candidates loaded, first ID was independently overridden, Chinese font
rendered correctly, the real Replay button reached a six-frame stable exit, and
there were no page/engine errors. Evidence is in
`delivery/dynamic-v3/packaging-browser-v4/browser.json` and screenshots. This is
one candidate replay plus loading the 20-case list, not 20 gameplay replays.

The first actual browser attempt V3 mounted the base and replayed, but emitted a
SceneTree busy error because scene switching happened inside `_ready`. Its
failure receipt is preserved. V4 defers the mount/start function and removes the
error without changing the base or physics.

Current artifact status is recorded in each `overlay-manifest.json`; do not mark
`runtime_verified` until the actual corresponding browser result passes. The
initial 5-file bootstrap is 120,904 bytes; the passing V4 candidate-data override
proof is **254,000 bytes**, SHA256
`e6df9c7a079a1211dff833d447a4ce33a36b04a2539030f4f3fca2c01e8f47e3`.
No base PCK, published site, or 900 MiB guard is edited.

For publication, retain overlay SHA256 as its build identity, record immutable
base/engine dependencies with their full hashes, publish only the new small
files, and verify public overlay/base bytes plus the real new UI. A prior V2 URL
or this V2 packaging proof must not be presented as V3 gameplay evidence.
