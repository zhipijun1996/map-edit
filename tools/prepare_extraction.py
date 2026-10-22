"""Create a temporary Godot data-only project from unmodified pinned sources."""
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
destination = pathlib.Path(sys.argv[1])
generation = [
    'platforming_module_definition', 'platforming_module_port', 'module_saw_definition',
    'module_moving_platform_definition', 'platform_thorn_definition', 'movement_capability_envelope',
    'forest_directional_geometry', 'forest_air_chain_geometry', 'forest_hollow_trunk_geometry',
    'forest_hollow_upper_candidate', 'forest_thorn_mouth_geometry', 'forest_vertical_chain_geometry',
    'forest_bible_backbranch_geometry', 'forest_exploration_modules', 'forest_playful_module_variants',
    'forest_thorn_corridor_modules', 'forest_exploration_places', 'forest_exploration_fallen_trunk',
    'forest_exploration_fruit_crossing',
]
paths = [f'scripts/generation/{name}.gd' for name in generation]
paths += ['scripts/player/player_tuning.gd','scripts/player/traversal_definition.gd',
          'scripts/enemies/enemy_definition.gd','scripts/enemies/forest_enemy_definition.gd',
          'scripts/resources/definitions/health_definition.gd','resources/enemies/forest_swing_pod.tres',
          'resources/player/traversal.tres']
paths += [str(path.relative_to(ROOT/'library/source')) for path in (ROOT/'library/source/resources/generation/modules').glob('*.tres')]
for path in paths:
    out = destination / path
    out.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(ROOT/'library/source'/path, out)
shutil.copyfile(ROOT/'tools/extract_modules.gd', destination/'extract_modules.gd')
(destination/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Map Notes data extraction"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
print(f'Prepared {len(paths)} unmodified source files in {destination}')
