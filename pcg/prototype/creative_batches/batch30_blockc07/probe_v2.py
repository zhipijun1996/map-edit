from . import probe_v1 as probe
from . import rules_v2
probe.rules=rules_v2
if __name__=='__main__':probe.main()
