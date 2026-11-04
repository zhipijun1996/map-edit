"""Bounded diagnostics of frozen inputs; not qualification or holdout."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse,inspect
from . import probe_review040_v1 as previous
from .refresh_review045_v1 import AUTH,rows
def run(row,version):
 source=inspect.getsource(previous.run).replace('approved-r040-','approved-r045-')
 scope={**previous.__dict__,'AUTH':AUTH};exec(compile(source,__file__,'exec'),scope);scope['run'](row,version)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--version',required=True);p.add_argument('ids',nargs='*');a=p.parse_args()
 for r in rows():
  if not a.ids or r['reviewId']in a.ids:run(r,a.version)
