from .approved_author_v1 import purpose
from .runtime import r03_author_v1 as original
from pcg.migration.physics import author_sources
RUNNER_SCRIPT = original.RUNNER_SCRIPT
SOURCE_DEPENDENCIES = author_sources([original])
