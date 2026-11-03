"""Prepare an isolated test host, never a main-game loader or generator."""

import argparse, hashlib, importlib.util, json, os, shutil, subprocess, zipfile
from pathlib import Path
from check_inputs import checked_zip, sha, write, ROOT

p = argparse.ArgumentParser(description=__doc__)
p.add_argument("--zip", type=Path, required=True)
p.add_argument("--sha256", required=True)
p.add_argument("--host-source", type=Path)
p.add_argument("--godot", type=Path, required=True)
p.add_argument("--work", type=Path, required=True)
p.add_argument("--out", type=Path, required=True)
a = p.parse_args()
z, m = checked_zip(a.zip, a.sha256)
lock = json.loads(z.read("runtime/host-lock.json"))
assert sha(a.godot.read_bytes()) == lock["godot"]["sha256"]
a.work.mkdir(exist_ok=False)
project = a.work / "project"
bundle = project / "module_pack"
bundle.mkdir(parents=True)
z.extractall(bundle)
spec = importlib.util.spec_from_file_location(
    "locked_install", bundle / "integration/install_host.py"
)
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)
installed = installer.install(bundle / "runtime/host-lock.json", project, a.host_source)
shutil.copytree(ROOT / "modules/game-plains-windchime-lesson", project / "main_sample")
shutil.copyfile(ROOT / "tools/runtime_audit/probe.gd", project / "probe.gd")
(project / "project.godot").write_text(
    'config_version=5\n[application]\nconfig/name="Module readiness audit test host"\nconfig/features=PackedStringArray("4.7", "GL Compatibility")\n[physics]\ncommon/physics_ticks_per_second=60\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n'
)
engine = a.work / a.godot.name
shutil.copyfile(a.godot, engine)
engine.chmod(0o755)
env = os.environ.copy()
env["XDG_DATA_HOME"] = str(a.work / "user-data")
env["XDG_CONFIG_HOME"] = str(a.work / "user-config")
env["GODOT_SILENCE_ROOT_WARNING"] = "1"
commands = []
for name, args in [
    ("import", ["--editor", "--import"]),
    (
        "probes",
        [
            "--fixed-fps",
            "60",
            "--script",
            "res://probe.gd",
            "--",
            "--report=" + str((a.work / "observations.json").resolve()),
        ],
    ),
]:
    cmd = [str(engine.resolve()), "--headless", "--path", str(project.resolve()), *args]
    commands.append(cmd)
    if name == "probes":
        cmd = [
            "strace",
            "-f",
            "-e",
            "trace=open,openat,readlink",
            "-o",
            str(a.work / "file-reads.log"),
            *cmd,
        ]
    with (a.work / (name + ".log")).open("w") as stream:
        r = subprocess.run(
            cmd,
            stdout=stream,
            stderr=subprocess.STDOUT,
            env=env,
            cwd=project,
            timeout=180,
        )
    text = (a.work / (name + ".log")).read_text()
    if r.returncode or "SCRIPT ERROR:" in text or "ERROR:" in text:
        raise RuntimeError(name + " failed: " + str(a.work / (name + ".log")))
report = json.loads((a.work / "observations.json").read_text())
if not report.get("passed"):
    raise RuntimeError("native audit observations failed")
trace = (a.work / "file-reads.log").read_text()
assert (
    str(ROOT) not in trace
    and "pcg/manual_review/implementation" not in trace
    and "pcg/results/" not in trace
)
report["execution"] = dict(
    engineSha256=sha(engine.read_bytes()),
    host=installed,
    zipSha256=a.sha256,
    probeSha256=sha((project / "probe.gd").read_bytes()),
    authoringOrLegacyWorkspaceRead=False,
    logSha256=sha((a.work / "probes.log").read_bytes()),
)
write(a.out, report)
write(a.work / "execution.json", dict(commands=commands, host=installed))
print(json.dumps(dict(passed=report["passed"], rows=len(report["rows"]))))
