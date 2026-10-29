"""Thirty real setup shots: v2 left the original enemy alive at 1 HP.

This adjusts the depletion fixture only. Nominal controller v12 and all
screen/holdout inputs remain frozen. No health or resource writes occur.
"""
import inspect
from . import probe_lift_lifecycle_v1 as previous

def main():
    source=inspect.getsource(previous.main).replace('approved-lift-lifecycle-v1','approved-lift-lifecycle-v3').replace("c['max_frames']=4800","c['max_frames']=3600").replace('range(20)','range(30)')
    namespace=dict(previous.__dict__);exec(compile(source,__file__,'exec'),namespace);namespace['main']()
if __name__=='__main__':main()
