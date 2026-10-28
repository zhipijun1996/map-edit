from .approved_author_v1 import purpose
from pcg.prototype.creative_batches.batch30_blockn08 import api_v2 as original
from pcg.migration.physics import author_sources
RUNNER_SCRIPT = original.RUNNER_SCRIPT
SOURCE_DEPENDENCIES = author_sources([original])
