from .approved_author_v1 import purpose
from pcg.prototype.creative_batches.batch30_blockn14 import api_v1 as original
from pcg.migration.physics import author_sources
RUNNER_SCRIPT = original.RUNNER_SCRIPT
SOURCE_DEPENDENCIES = author_sources([original])
