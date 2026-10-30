"""Reuse original native support/body/safety measurements for relay geometry."""
import inspect
from . import revision061_top_observer_v1 as previous,review_counter_scope_v12 as counters
from .revision062_top_observer_v1 import native_neighbor_contact
from .revision065_boundary_v1 import VERSIONS
ns={**previous.__dict__,'VERSIONS':VERSIONS,'native_neighbor_contact':native_neighbor_contact}
s=inspect.getsource(previous.observe).replace("abs(f['y']+50)<=.05",'native_neighbor_contact(case,f,n)');exec(compile(s,__file__,'exec'),ns)
observe=ns['observe']
cs={**counters.__dict__,'VERSIONS':VERSIONS};exec(compile(inspect.getsource(counters.classify),__file__,'exec'),cs);classify=cs['classify']
