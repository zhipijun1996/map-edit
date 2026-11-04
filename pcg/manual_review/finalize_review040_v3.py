"""Normalize diagram enemy glyphs to the already tested native collision size.

Same approved air centers / ground foot centers and existing EnemyDefinition.
No control, native actor dimension, physics input or design source is changed.
"""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,inspect
from pcg.migration import core
from . import finalize_first40_v1 as shared,finalize_review040_v1 as first,finalize_review040_v2 as previous
from .finalize_review040_v1 import AUTH,folder_for,qualify,decode,ROOT
deliver=previous.deliver
def normalized(doc):
 d=copy.deepcopy(doc)
 for o in d['objects']:
  if o['type']!='enemy':continue
  cx=o['x']+o['w']/2;cy=o['y']+o['h']/2;bottom=o['y']+o['h']
  o.update(x=cx-14,y=cy-16 if o['definition']=='plains_diver'else bottom-32,w=28,h=32)
 return d
def freeze(row):
 f=folder_for(row)
 if f.exists()and not(f/'frozen.json').exists():
  f.rename(f.with_name(f.name+'-incomplete-glyph-freeze-v1'))
 source=inspect.getsource(shared.freeze).replace('approved-first40-final-v1-','approved-review040-final-v1-')
 source=source.replace("doc=core.read(old/'module.mapnote.json');g=", "doc=normalized(core.read(old/'module.mapnote.json'));g=")
 scope={**shared.__dict__,'AUTH':AUTH,'ROOT':ROOT,'folder_for':folder_for,'decode':decode,'normalized':normalized};exec(compile(source,__file__,'exec'),scope);scope['freeze'](row)
def partial(row):
 source=inspect.getsource(previous.partial).replace("'-partial-delivery-v1'","'-partial-delivery-v2'")
 scope={**previous.__dict__};exec(compile(source,__file__,'exec'),scope);scope['partial'](row)
if __name__=='__main__':
 import sys
 for r in core.read(AUTH/'handoff.json')['rows']:
  if r['reviewId']in sys.argv[2:]:globals()[sys.argv[1]](r)
