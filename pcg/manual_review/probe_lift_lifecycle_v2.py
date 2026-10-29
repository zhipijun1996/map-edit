"""Correct fixture frame budget to the actual existing harness maximum."""
import inspect
from . import probe_lift_lifecycle_v1 as previous

def main():
    source=inspect.getsource(previous.main).replace('approved-lift-lifecycle-v1','approved-lift-lifecycle-v2').replace("c['max_frames']=4800","c['max_frames']=3600")
    namespace=dict(previous.__dict__);exec(compile(source,__file__,'exec'),namespace);namespace['main']()
if __name__=='__main__':main()
