"""Run final preregistered rule through the unchanged original probe pipeline."""
from . import probe_v1 as probe
from . import rules_v2
probe.rules=rules_v2
probe.HERE=rules_v2.HERE
if __name__=='__main__':probe.main()
