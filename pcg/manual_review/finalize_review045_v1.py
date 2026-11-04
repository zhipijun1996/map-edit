"""Freeze selected controls and run the original full protocol exactly once."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect
from pcg.migration import core
from . import finalize_first40_v1 as shared,finalize_review040_v1 as previous
from .refresh_review045_v1 import AUTH,rows
from .prepare_review045_v1 import decode
ROOT=core.REPO/'pcg/manual_review/implementation/review-045-final-v1'
def folder_for(row):return ROOT/row['moduleId']
def freeze(row):
 source=inspect.getsource(shared.freeze).replace('approved-first40-final-v1-','approved-review045-final-v1-').replace('pcg/manual_review/first30_content_v2.py','pcg/manual_review/prepare_review045_v1.py')
 scope={**shared.__dict__,'AUTH':AUTH,'ROOT':ROOT,'folder_for':folder_for,'decode':decode};exec(compile(source,__file__,'exec'),scope);scope['freeze'](row)
def qualify(row):
 source=inspect.getsource(previous.qualify).replace('approved-r040-','approved-r045-').replace('approved-review040-v1-','approved-review045-v1-')
 scope={**previous.__dict__,'AUTH':AUTH,'folder_for':folder_for};exec(compile(source,__file__,'exec'),scope);scope['qualify'](row)
def deliver(row):
 source=inspect.getsource(previous.deliver).replace('approved-r040-','approved-r045-')
 scope={**previous.__dict__,'AUTH':AUTH,'folder_for':folder_for};exec(compile(source,__file__,'exec'),scope);scope['deliver'](row)
if __name__=='__main__':
 import sys
 for row in rows():
  if row['reviewId']in sys.argv[2:]:globals()[sys.argv[1]](row)
