"""New HQ designs use the same full-body external-counter contract as 058."""
import copy
from .revision061_top_boundary_v1 import VERSIONS
from .review_counter_scope_v12 import classify as original

def classify(case,raw,check,outcome,judgment,baseline):
 s=case.get('approved_implementation',{})
 if VERSIONS.get(s.get('reviewId'))!=s.get('designVersion'):return judgment
 # The original classifier's geometry, health, mouth, raw-frame and baseline
 # gates are copied unchanged; only the separately approved version set differs.
 import inspect
 from . import review_counter_scope_v12 as previous
 ns={**previous.__dict__,'VERSIONS':VERSIONS};exec(compile(inspect.getsource(previous.classify),__file__,'exec'),ns)
 return ns['classify'](case,raw,check,outcome,judgment,baseline)
