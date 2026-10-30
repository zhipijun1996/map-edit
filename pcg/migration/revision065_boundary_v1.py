"""The approved relay retains the prior gated, outward-only TOP interface."""
import inspect
from . import revision053_boundary_v1 as previous
VERSIONS={'idea-96ba6bf1-9b60-470a-9128-54ae7ea44af3':'sha256:9b26d91837d8e139677d8064fbc477aa9f9d2b88d4aa95b8895092eda583694d'}
ns={**previous.__dict__,'VERSIONS':VERSIONS}
for name in ['applies','neighbor','local','exit']:exec(compile(inspect.getsource(getattr(previous,name)),__file__,'exec'),ns)
applies=ns['applies'];neighbor=ns['neighbor'];local=ns['local'];exit=ns['exit']
