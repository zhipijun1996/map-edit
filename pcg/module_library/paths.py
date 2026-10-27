"""Current Module paths and explicit, checksum-bound historical DATA references.

No import alias, old directory, generator fallback or source restoration exists.
"""
import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_LIBRARY = REPO / 'pcg/module_library/store'


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def evidence_path(path, expected_sha256=None):
    """Resolve only an explicitly inventoried byte-identical relocated file.

    Old immutable reviews may name its former location. This is DATA provenance,
    not a substitute root for live library discovery or an old Python namespace.
    """
    value = Path(path)
    value = value if value.is_absolute() else REPO / value
    value = value.resolve()
    if not value.is_relative_to(REPO):raise ValueError('artifact_outside_repository')
    if not value.exists():
        key = value.relative_to(REPO).as_posix()
        relocations = json.loads(Path(__file__).with_name('relocations.json').read_text())
        info = relocations.get(key)
        if info is None:raise FileNotFoundError(value)
        if expected_sha256 is not None and expected_sha256 != info['sha256']:
            raise ValueError('historical_reference_checksum_mismatch')
        value = (REPO / info['destination']).resolve()
        if not value.is_relative_to(DEFAULT_LIBRARY):raise ValueError('invalid_candidate_relocation')
        expected_sha256 = info['sha256']
    if expected_sha256 is not None:
        with value.open('rb') as stream:actual = hashlib.file_digest(stream, 'sha256').hexdigest()
        if actual != expected_sha256:raise ValueError('relocated_artifact_drift')
    return value
