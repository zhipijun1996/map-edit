"""Five native MP4s using unchanged workshop exact comparison, isolated display text."""
import json,hashlib
from pathlib import Path
from pcg.prototype.workshop.record import record,KEYS
from pcg.prototype.factory.core.engine import file_sha
OWN=Path(__file__);REPO=OWN.resolve().parents[4];SCENE=OWN.with_name('movie-v1.tscn').resolve()
DEST=REPO/'pcg/results/workshop-creative-jump-wall-native-v1'
if DEST.exists():raise ValueError('immutable_native_parent_exists')
DEST.mkdir(parents=True)
selection=[('v2',1,'step-off-wall-return'),('v2',2,'switchback-wall-ascent'),('v3',0,'late-air-rise'),('v3',1,'bell-wall-rebound'),('v5',0,'wall-slide-launch-window')]
rows=[]
for batch,roundno,family in selection:
 source=f'workshop-creative-jump-wall-production-{batch}/round-{roundno:02d}'
 folder=DEST/family
 try:
  record(source,str(folder.relative_to(REPO)),display=':106',families=[family],main_scene=SCENE)
  manifest=json.loads((folder/'manifest.json').read_text());status='exact_native_pass'
  rows.append(dict(family=family,status=status,manifest=str((folder/'manifest.json').relative_to(REPO)),clips=manifest['clips']))
 except Exception as e:
  rows.append(dict(family=family,status='recording_or_comparison_failed',error=repr(e),evidence=str(folder.relative_to(REPO))))
 (DEST/'progress.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(rows[-1],ensure_ascii=False),flush=True)
manifest=dict(schema='pcg/native-jump-wall-playlist/v1',recording='original Godot native 60Hz; original immutable case Router inputs',exact_comparison_rules=list(KEYS),comparison_threshold_unchanged=True,clips=rows,source_files={str(p.resolve().relative_to(REPO)):file_sha(p)for p in [OWN,SCENE,OWN.with_name('movie-v1.gd')]},production_admitted=False,human_fun='unreviewed',manual_play='not_done')
(DEST/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
