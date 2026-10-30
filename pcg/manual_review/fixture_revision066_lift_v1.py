"""Repeat the same-world relay/reward demonstration on the final repaired inputs."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect
from . import fixture_revision065_lift_v1 as previous
from .run_revision066_lift_v1 import folder_for
def main():
 s=inspect.getsource(previous.main).replace('missed-boarding-wait-chest-v1','missed-boarding-wait-chest-v2').replace('approved-r065-lift-relay-recovery-chest-v1','approved-r066-lift-relay-recovery-chest-v1')
 ns={**previous.__dict__,'folder_for':folder_for,'__file__':__file__};exec(compile(s,__file__,'exec'),ns);ns['main']()
if __name__=='__main__':main()
