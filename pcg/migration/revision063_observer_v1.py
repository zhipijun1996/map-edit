"""Same native support/safe-margin proof, scoped to newly authorized versions."""
import inspect
from . import revision061_top_observer_v1 as old,review_counter_scope_v12 as counters
from .revision062_top_observer_v1 import native_neighbor_contact,SAFE_MARGIN
from .revision063_boundary_v1 import VERSIONS
ns={**old.__dict__,'VERSIONS':VERSIONS,'native_neighbor_contact':native_neighbor_contact}
source=inspect.getsource(old.observe).replace("abs(f['y']+50)<=.05",'native_neighbor_contact(case,f,n)')
exec(compile(source,__file__,'exec'),ns)
def observe(case,raw):return ns['observe'](case,raw)
cs={**counters.__dict__,'VERSIONS':VERSIONS};exec(compile(inspect.getsource(counters.classify),__file__,'exec'),cs)
def classify(case,raw,check,outcome,judgment,baseline):return cs['classify'](case,raw,check,outcome,judgment,baseline)
