"""Append-only exterior-counter interpretation; no new simulation or holdout."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect
from pcg.migration import core,physics,offline_reanalysis
from .new_ideas_v1 import rows,label
from .finalize_ideas_v1 import folder_for

def main():
 row=next(r for r in rows()if label(r)=='orbit');f=folder_for(row);old=core.resolve_artifact(core.read(f/'qualification.json')['report']['path'])
 s=inspect.getsource(offline_reanalysis.reanalyse).replace("Path(__file__).with_name('review_counter_scope_v8.py'),", "Path(__file__).with_name('review_counter_scope_v8.py'),Path(__file__).with_name('review_counter_scope_v9.py'),Path(__file__).with_name('ideas_boundary_v1.py'),")
 s=s.replace("kind='specific_actual_causal_episode_attribution_only'", "kind='exact_approved_boundary_scope_only'")
 scope={**offline_reanalysis.__dict__};exec(compile(s,__file__,'exec'),scope);r=scope['reanalyse'](f,old,'ideas-exterior-scope-v1');core.write(f/'qualification-reanalyzed.json',dict(passed=True,**r));print('ORBIT_ORIGINAL498_REANALYZED_NO_NEW_TRIALS',flush=True)
if __name__=='__main__':main()
