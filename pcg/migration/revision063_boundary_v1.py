"""Exact r063 versions use the established full canonical boundary fixtures."""
import copy,inspect
from . import core,revision060_top_boundary_v1 as normal,revision053_boundary_v1 as lift
VERSIONS={'idea-96ba6bf1-9b60-470a-9128-54ae7ea44af3': 'sha256:b1c25284b6c9691744e2069c655ca4c4470e295f9849528d8992459e331944d6', 'idea-plains-hq07-001': 'sha256:654ed79c6a2d35e5c2456f92e0e0ee45d0038583a2c830a981da34e7128b37a7', 'idea-plains-hq09-001': 'sha256:313fc0c711815b19e726360dbb0f6b4aabd4e4b21c90aba33a7bc5c939f2cff4', 'idea-spec02-s04-001': 'sha256:3d5d4b164083bf52a544dd4299c58e6dd74f474fafc32f78fc6b760acbdebc4f', 'idea-spec02-s06-001': 'sha256:5831f430e8986857d524f8a89d86dfc93410befd38c8b26bd22fe4abaea789d4', 'idea-spec02-s09-001': 'sha256:2f7b3bcc80995805910e5a90f055c4f3800df46b0d304192d9ea70ce67948198'}
def namespace(module):
 ns={**module.__dict__,'VERSIONS':VERSIONS}
 for name in ['applies','neighbor','local','entry','exit']:
  if hasattr(module,name):exec(compile(inspect.getsource(getattr(module,name)),__file__,'exec'),ns)
 return ns
NORMAL=namespace(normal);LIFT=namespace(lift)
def applies(case,port):return NORMAL['applies'](case,port) or LIFT['applies'](case,port)
def neighbor(case,port):return LIFT['neighbor'](case,port)
def local(case,port,direction,doc,offset=0):
 return LIFT['local'](case,port,direction,doc,offset) or NORMAL['local'](case,port,direction,doc,offset)
def entry(case,doc,physics):return NORMAL['entry'](case,doc,physics)
def exit(case,doc,physics):
 result=LIFT['exit'](case,doc,physics)
 return result if result is not None else NORMAL['exit'](case,doc,physics)
