"""Two 62 local-fixture repairs; all original nominal/holdout bytes retained."""
import inspect
from . import review_boundary_repair_v6 as previous
SCHEMA='pcg/review-boundary-fixture-repair/v8'
def validate_lineage(report,path):
 source=inspect.getsource(previous.validate_lineage).replace("'-174-'in i and '-exit-'in i","'-50-'in i and '-C-'in i")
 scope={**previous.__dict__,'SCHEMA':SCHEMA};exec(compile(source,__file__,'exec'),scope);scope['validate_lineage'](report,path)
