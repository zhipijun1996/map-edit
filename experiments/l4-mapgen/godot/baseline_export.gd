extends SceneTree
## Read-only baseline exporter. Run with the real game as --path and this
## absolute external --script; all artifacts belong to map-edit, never res://.
## Generation/validation timings are measured separately from JSON and IO.

const EXPORT_VERSION := "map-edit/l4-mapgen/baseline-export/v1"
const PROFILES := ["plains", "forest_v15", "forest_v18"]
const SOURCE_PATHS := [
	"project.godot", "config/player_tuning.json", "resources/player/traversal.tres",
	"scripts/demo/demo_app.gd", "scripts/player/player_tuning.gd",
	"scripts/run/run_random_stream.gd", "scripts/run/plains_region_campaign.gd",
	"scripts/generation/plains_region_generator.gd",
	"scripts/generation/plains_exploration_topology.gd",
	"scripts/generation/plains_route_recipes.gd",
	"scripts/generation/plains_root_bell_encounter_v2.gd",
	"scripts/generation/plains_root_bell_encounter_v3.gd",
	"scripts/generation/thorn_forest_region_generator.gd",
	"scripts/generation/thorn_forest_region_v2_v10.gd",
	"scripts/generation/thorn_forest_region_v2.gd",
	"scripts/generation/thorn_forest_region_v2_v13.gd",
	"scripts/generation/thorn_forest_region_v2_v14.gd",
	"scripts/generation/thorn_forest_region_v2_v15.gd",
	"scripts/generation/thorn_forest_region_v2_v18.gd",
	"scripts/generation/forest_exploration_network.gd",
	"scripts/generation/forest_exploration_place_embedding.gd",
	"scripts/generation/forest_exploration_places.gd",
	"scripts/generation/forest_bible_v2_layout.gd",
]

var output_dir := ""
var seed_count := 10
var seed_prefix := "l4-baseline"
var requested_profiles: Array[String] = ["plains", "forest_v15", "forest_v18"]
var requested_maps: Array[int] = [1, 2]
var expected_source_commit := ""
var failures: Array[String] = []
var report: Dictionary = {}

func _initialize() -> void:
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--output-dir="):
			output_dir = arg.trim_prefix("--output-dir=")
		elif arg.begins_with("--seed-count="):
			seed_count = int(arg.trim_prefix("--seed-count="))
		elif arg.begins_with("--seed-prefix="):
			seed_prefix = arg.trim_prefix("--seed-prefix=")
		elif arg.begins_with("--profiles="):
			requested_profiles.clear()
			for profile: String in arg.trim_prefix("--profiles=").split(","):
				requested_profiles.append(profile)
		elif arg.begins_with("--maps="):
			requested_maps.clear()
			for map_text: String in arg.trim_prefix("--maps=").split(","):
				requested_maps.append(int(map_text))
		elif arg.begins_with("--source-commit="):
			expected_source_commit = arg.trim_prefix("--source-commit=")
		else:
			failures.append("Unknown argument: " + arg)
	run.call_deferred()

func run() -> void:
	var game_root := ProjectSettings.globalize_path("res://").simplify_path()
	if not output_dir.is_absolute_path() or output_dir.begins_with("res://"):
		failures.append("--output-dir must be an absolute filesystem path outside the game")
	else:
		output_dir = output_dir.simplify_path()
		if output_dir == game_root or output_dir.begins_with(game_root.trim_suffix("/") + "/"):
			failures.append("Output inside game project is forbidden")
		if DirAccess.dir_exists_absolute(output_dir) or FileAccess.file_exists(output_dir):
			failures.append("Fresh output directory required; existing artifacts are never overwritten")
	if seed_count < 1 or seed_count > 100 or seed_prefix.is_empty():
		failures.append("Require 1..100 seeds and a nonempty seed prefix")
	if requested_profiles.is_empty() or requested_maps.is_empty():
		failures.append("Profiles/maps must not be empty")
	var unique_profiles: Dictionary = {}
	for profile: String in requested_profiles:
		if profile not in PROFILES or unique_profiles.has(profile): failures.append("Invalid/duplicate profile: " + profile)
		unique_profiles[profile] = true
	var unique_maps: Dictionary = {}
	for index: int in requested_maps:
		if index not in [1, 2] or unique_maps.has(index): failures.append("Invalid/duplicate map: " + str(index))
		unique_maps[index] = true
	if not failures.is_empty():
		printerr(JSON.stringify({"export_version":EXPORT_VERSION,"failures":failures}))
		quit(1)
		return
	if DirAccess.make_dir_recursive_absolute(output_dir) != OK:
		printerr("Cannot create external artifact directory: " + output_dir)
		quit(1)
		return
	var git_output: Array = []
	var git_exit := OS.execute("git", PackedStringArray(["-C", game_root, "rev-parse", "HEAD"]), git_output)
	var source_commit := str(git_output[0]).strip_edges() if git_exit == 0 and not git_output.is_empty() else ""
	if source_commit.is_empty(): failures.append("Could not read actual game Git source commit")
	if not expected_source_commit.is_empty() and source_commit != expected_source_commit:
		failures.append("Actual source differs from --source-commit")
	var source_before := _source_inventory()
	report = {
		"export_version":EXPORT_VERSION,
		"scope":"actual_complete_generator_generate_and_separate_validate; no_scene_assembly_or_Motor_playability",
		"engine":Engine.get_version_info(), "game_root":game_root,
		"source_repository":"https://github.com/zhipijun1996/gunman-rush",
		"source_commit":source_commit,"requested_source_commit":expected_source_commit,
		"exporter_sha256":FileAccess.get_sha256(get_script().resource_path),
		"seed_count":seed_count,"seed_prefix":seed_prefix,
		"raw_manifest_policy":"keep seed index 00 on both maps per profile; all rows retain timing/counts/hash/parameters",
		"profiles":requested_profiles,"maps":requested_maps,
		"sources_before":source_before,"rows":[],"failures":failures,
		"timing_policy":{
			"clock":"Time.get_ticks_usec monotonic; milliseconds",
			"generate":"public generate call including its own internal validation/reconstruction",
			"validate":"additional public validation call on returned manifest",
			"json":"JSON.stringify raw manifest only; file IO excluded",
			"roundtrip_validate":"public validate after JSON.parse_string; separate from generate",
			"cold_start":"no warmup; first per-profile row may include lazy resource loads",
			"runtime_limit":"editor/headless desktop baseline only; not Web/mobile runtime or FPS proof",
		},
		"memory_policy":"Godot MEMORY_STATIC and MEMORY_STATIC_MAX process counters; not per-map RSS/retained allocation",
		"physics_status":"not_run","human_playtest_status":"not_run",
	}
	var tuning := PlayerTuning.load_default()
	if tuning == null: failures.append("Default authoritative PlayerTuning could not load")
	var started := Time.get_ticks_usec()
	if failures.is_empty():
		for profile: String in requested_profiles:
			for index: int in requested_maps:
				for seed_index: int in seed_count:
					var root_seed := "%s-%02d" % [seed_prefix, seed_index]
					var row := _export_one(profile, index, root_seed, tuning)
					report.rows.append(row)
					if not bool(row.get("passed", false)):
						failures.append("%s/map%s/%s: %s" % [profile, index, root_seed, row.get("error", "validation failed")])
					_write_report()
	report.elapsed_ms = (Time.get_ticks_usec() - started) / 1000.0
	report.sources_after = _source_inventory()
	report.source_files_stable = report.sources_before == report.sources_after
	if not report.source_files_stable: failures.append("Inventoried game source files changed during export")
	report.failures = failures
	report.passed = failures.is_empty()
	report.exit_code = 0 if failures.is_empty() else 1
	_write_report()
	print("L4 BASELINE EXPORT: %s / %s rows / %s failures / %s ms" % ["PASS" if failures.is_empty() else "FAIL", report.rows.size(), failures.size(), report.elapsed_ms])
	quit(int(report.exit_code))

func _export_one(profile: String, map_index: int, root_seed: String, tuning: PlayerTuning) -> Dictionary:
	var generator: RefCounted
	var actual_seed: String
	var parameters: Dictionary
	if profile == "plains":
		generator = PlainsRegionGenerator.new()
		# Copy DemoApp selection exactly; direct generate defaults to historical v10.
		generator.root_bell_mode = "v3" if PlainsRootBellEncounterV3.PRODUCTION_ADMITTED else "v2" if PlainsRootBellEncounterV2.PRODUCTION_ADMITTED else "legacy_v10"
		actual_seed = PlainsRegionCampaign.seed_for(root_seed, map_index)
		parameters = {"api":"PlainsRegionGenerator.generate(seed,tuning,false,\"\",difficulty)","seed":actual_seed,"sample":false,"force_family":"","difficulty":"intro" if map_index == 1 else "advanced","root_bell_mode":generator.root_bell_mode,"profile_source":"DemoApp _root_bell_run_mode and map difficulty"}
	else:
		generator = ThornForestRegionGenerator.new()
		actual_seed = ThornForestRegionGenerator.seed_for(root_seed, map_index)
		var layout := ThornForestRegionGenerator.DEPTH_LAYOUT_BIBLE if profile == "forest_v15" else ThornForestRegionGenerator.DEPTH_LAYOUT_PLACES
		parameters = {"api":"ThornForestRegionGenerator.generate(seed,tuning,map_index,capability_snapshot)","seed":actual_seed,"map_index":map_index,"capability_snapshot":{"grapple":true,"weapon_id":"pulse_gun","abilities":["grapple"],"items":[],"forest_content_version":ThornForestRegionGenerator.DEPTH_VERSION,"forest_layout_version":layout,"forest_v9_north_return":true},"capability_scope":"actual forest starting H ability set; no wall/double-jump/evolution","admission":"default_runtime_layout" if profile == "forest_v15" else "explicit_development_candidate_production_pool_false"}
	var row := {"profile":profile,"map_index":map_index,"root_seed":root_seed,"parameters":parameters,"passed":false,"memory_static_before":Performance.get_monitor(Performance.MEMORY_STATIC)}
	var begin := Time.get_ticks_usec()
	var result: Dictionary
	if profile == "plains":
		result = generator.generate(actual_seed, tuning, false, "", parameters.difficulty)
	else:
		result = generator.generate(actual_seed, tuning, map_index, parameters.capability_snapshot)
	row.generate_ms = (Time.get_ticks_usec() - begin) / 1000.0
	row.memory_static_after_generate = Performance.get_monitor(Performance.MEMORY_STATIC)
	row.memory_static_max = Performance.get_monitor(Performance.MEMORY_STATIC_MAX)
	row.generate_ok = bool(result.get("ok", false))
	if not row.generate_ok or not result.get("manifest") is Dictionary:
		row.error = result.get("error", "Public generate returned no manifest")
		return row
	var manifest: Dictionary = result.manifest
	row.generator_version = result.get("stage_generator_version", manifest.get("version", ""))
	row.layout_version = manifest.get("layout_version", manifest.get("layout_id", ""))
	row.manifest_hash = manifest.get("manifest_hash", "")
	row.production_pool = manifest.get("production_pool", null)
	row.family = manifest.get("family", "")
	row.fallback_id = manifest.get("fallback_id", "")
	row.area_count = manifest.get("areas", []).size()
	row.connection_count = manifest.get("connections", []).size()
	row.node_count = manifest.get("nodes", []).size()
	row.geometry_instance_count = manifest.get("geometry_instances", []).size()
	row.reward_count = manifest.get("rewards", []).size()
	row.enemy_count = manifest.get("enemies", []).size()
	begin = Time.get_ticks_usec()
	row.validate_ok = generator.validate(manifest, tuning)
	row.validate_ms = (Time.get_ticks_usec() - begin) / 1000.0
	var non_json: Array[String] = []
	_non_json_values(manifest, "$", non_json)
	row.non_json_values = non_json
	begin = Time.get_ticks_usec()
	var raw_json := JSON.stringify(manifest)
	row.json_ms = (Time.get_ticks_usec() - begin) / 1000.0
	row.manifest_json_bytes = raw_json.to_utf8_buffer().size()
	row.manifest_json_sha256 = raw_json.sha256_text()
	var parsed: Variant = JSON.parse_string(raw_json)
	begin = Time.get_ticks_usec()
	row.roundtrip_validate_ok = parsed is Dictionary and generator.validate(parsed, tuning)
	row.roundtrip_validate_ms = (Time.get_ticks_usec() - begin) / 1000.0
	row.manifest_file = null
	if root_seed == seed_prefix + "-00":
		var stem := "%s-map%s-%s" % [profile, map_index, root_seed.validate_filename()]
		row.manifest_file = stem + ".manifest.json"
		var file := FileAccess.open(output_dir.path_join(row.manifest_file), FileAccess.WRITE)
		if file == null:
			row.error = "Cannot write raw external manifest"
			return row
		file.store_string(raw_json)
		file.close()
	row.passed = bool(row.validate_ok) and bool(row.roundtrip_validate_ok) and non_json.is_empty()
	if not row.passed: row.error = "Public validation, JSON roundtrip or primitive JSON contract failed"
	return row

func _non_json_values(value: Variant, path: String, found: Array[String]) -> void:
	match typeof(value):
		TYPE_NIL, TYPE_BOOL, TYPE_INT, TYPE_FLOAT, TYPE_STRING, TYPE_STRING_NAME:
			return
		TYPE_ARRAY:
			for i: int in value.size(): _non_json_values(value[i], "%s[%s]" % [path, i], found)
		TYPE_DICTIONARY:
			for key: Variant in value:
				if typeof(key) not in [TYPE_STRING, TYPE_STRING_NAME]: found.append(path + ":non-string-key")
				_non_json_values(value[key], path + "." + str(key), found)
		_:
			found.append(path + ":" + type_string(typeof(value)))

func _source_inventory() -> Dictionary:
	var inventory: Dictionary = {}
	for path: String in SOURCE_PATHS:
		inventory[path] = FileAccess.get_sha256("res://" + path)
	return inventory

func _write_report() -> void:
	report.failures = failures
	var file := FileAccess.open(output_dir.path_join("report.json"), FileAccess.WRITE)
	if file == null:
		printerr("Cannot write external baseline receipt")
		return
	file.store_string(JSON.stringify(report, "\t"))
	file.close()
