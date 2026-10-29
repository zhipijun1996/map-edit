from pathlib import Path
from .ideas_author_v7 import purpose, SOURCE_DEPENDENCIES as previous
RUNNER_SCRIPT = Path(__file__).parent / 'runtime/ideas_runner_v8.gd'
SOURCE_DEPENDENCIES = [*previous, Path(__file__).with_name('ideas_author_v7.py')]
