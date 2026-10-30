# Module package integration

The ZIP is generated from the single map-edit Module library. Unzip it into `res://module_pack/` in a Godot host, or read its top-level `catalog.json` from map-gen. Never edit it as another source library. Pin the package version and SHA256 in downstream project configuration.

`manifest.json` records package/schema/Foundation/source versions and checksums for every included file. Foundation specification 1.2, Foundation model 1.0 and generationContract v2 are separate version numbers. `catalog.json.modules` contains stable IDs, current content versions, aliases, region/use, Block size, rectangular footprint, source bounds/origin offset, actual scoped directed routes, ability and initial configuration requirements, explicitly allowed configurations, runtime scenes and evidence references. Designs excluded from runtime have specific reasons in `catalog.json.excluded`.

This release allows identity orientation and translated placement with every listed Port connected, using `original-all-ports`. It does not authorize mirrors, corner relocations, closures or other connected-Port subsets. Public Port permissions describe the initial state; mechanism changes do not grant an initially forbidden ingress. Local scoped routes are not arbitrary seam/chaining or whole-map certification. Capability sets in validation are witnessed configurations; minimum required abilities and additional-ability monotonicity remain unknown.

## Dependencies and clean installation

No player scene, original game engine, historical game project or experiment workspace is embedded in the ZIP. Shared actor/Cell/assets are installed by hash from the upstream game commit in the lock. Python's standard library is sufficient for the installer:

```sh
python3 module_pack/integration/install_host.py --target /path/to/godot-project
```

The default lock is `runtime/host-lock.json`: the native `12f6cb006d7119598e3235f4ca4f7323e4c9d092` profile used by scoped route qualification. It is a bounded dependency closure, not the complete game repository. `--source /path/to/host-checkout-or-cache` copies only declared, hash-matching files; omission downloads exact upstream files. Conflicting installed versions and missing/changed files fail explicitly. The copied project works after the cache is unavailable. Godot 4.7.2 stable is the validated engine; see the engine SHA in the lock and acceptance evidence.

`runtime/host-lock-current-game.json` declares the read-only checked game head `5f55716a838a754a938997920ff18cb3b17452b5`. This profile has native scene/collision/mechanism/reward/external-player API integration checks. Full route/robustness qualification on that newer host is still pending; the original route evidence remains tied to the native profile. To inspect/install that explicitly chosen compatibility profile:

```sh
python3 module_pack/integration/install_host.py --lock module_pack/runtime/host-lock-current-game.json --target /path/to/current-game
```

When integrating into an existing game, keep its own `project.godot`, player, lifetime and services. The installer verifies matching existing files and refuses silent overwrites of incompatible files. Do not create duplicate global game classes inside the package. Old fixture source path strings inside legacy metadata are immutable provenance labels; portable profile verification uses the package's `runtime/player-profiles.json`, not those former files.

## map-gen reader

The read-only checked map-gen commit is `c2ac2c3625f659364b187592c836c5ff2bceb892`. Its current Python prototype has no released package-import API. `integration/map_gen_reader.py` supplies a bounded adapter to its `prototype.model` template/Port conventions:

```python
from map_gen_reader import read_library, validate_placement, routes_for_abilities
library = read_library('/path/to/unzipped-package')
template = library['b31-n06-fourport-two-low-ingress']
configuration = validate_placement(template, [p['id'] for p in template['ports']])
usable_routes = routes_for_abilities(template, {'jump', 'recoil'})
# prototype.model.placed_ports(template, origin_x, origin_y, mirror=False)
```

Insert these templates after importing the model; do not call the prototype's `generate.prepare_library()`, which overwrites `LIB` with placeholders. The adapter maps `shot_recoil` to its `recoil` spelling; it preserves `wall_climb` rather than pretending the prototype supports it. Only exact witnessed ability sets are returned. The existing prototype generator assumes closure/mirror behavior; it must call `validate_placement` for each accepted placement and reject unsupported configurations before exporting. Uncertified partial connections cannot be enabled merely because that prototype has a solid-cap helper. The package does not change the downstream algorithm repository.

Port `local2` coordinates are doubled Block coordinates relative to the owned rectangle's top-left. At integer Block origin `(x,y)`, `world2 = 2*(x,y) + local2`. Matching still requires opposite faces, equal surfaces, initial permissions and a separately verified seam.

## Main game loader and external player

```gdscript
const ModuleRegistry=preload("res://module_pack/integration/module_registry.gd")
var registry=ModuleRegistry.new()

func load_generated_room(existing_player: PlayerController, world: Node2D, services: Dictionary) -> void:
    var opened: Dictionary=registry.open("res://module_pack")
    assert(opened.ok)
    # Derive from the saved map/node identity; never use the current array index.
    var stable_instance_id="run-42/map-node-17"
    var result: Dictionary=registry.instantiate_module(
        "b31-n06-fourport-two-low-ingress", stable_instance_id,
        Vector2i(7,-3), world, existing_player, services)
    assert(result.ok)
    var port: Dictionary=result.instance.world_port("A")
    print(port.position)

# services must contain the host-owned policy: FrameDamagePolicy,
# lifetime: DemoLifetime and wallet: RunWallet. Native Note/region-chest
# consumers also require meta: MetaProgression and region_state: PlainsRegionState.
```

The registry takes a Block origin for the owned rectangle, not an old editor-canvas origin. `instance.position = world.to_local(originBlocks*blockSize + sceneOriginOffsetPixels)`; `sceneOriginOffsetPixels = -bounds.position`. `world_port()` returns true global boundary positions. Parent transforms must be translation-only. Duplicate live instance IDs and uncertified configurations fail. Save the module ID, exact content/package version, stable instance ID, origin and configuration with the generated map.

The host creates/configures its existing player once before binding. Binding never spawns another player, applies a tuning profile or refills resources. Read each entry's `initialConfiguration`: when a native fixture/profile is required, configure the actor at initial creation using the declared native profile and `runtime/module_runtime/native_profile_v5-eeef5b9dc854.gd.initialize_once`; passing a mismatched existing actor fails. Do not initialize that profile at a room seam. The helper verifies the package's exact profile declaration and rejects initialization after the player's first tick.

Enemy/damage identities and reward transactions are namespaced by stable instance ID. Multiple instances share the supplied native damage policy and wallet while retaining independent enemy targets. Unload through `registry.unload(instance_id)` and wait for the queued node to exit before reusing that live ID. Cleanup releases only that instance's native damage registrations; shared player resources stay with the host. Saved per-module mechanism/enemy state and arbitrary room chaining are host integration work, not supplied whole-game persistence.

## Verification

`evidence/module-production/portable-runtime.json` binds the current source hashes, runtime fingerprint, pinned host and engine. Acceptance imports real scenes in a clean extracted project, checks every module's collision shapes/one-way flags and translated Ports, binds the external actor without resource resets, exercises actual body collision, native projectile-to-bell delivery and idempotent native reward grants, and checks independent shared instances. `strace` verifies no runtime reads from the authoring repository or former experiment/fixture paths. Latest-game API compatibility is reported separately. Historical physical qualification is addressed by immutable Git/archive references, never by missing local experiment folders.
