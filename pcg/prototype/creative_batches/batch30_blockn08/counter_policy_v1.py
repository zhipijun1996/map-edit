"""Accept actual safe old-route return; keep nominal lower witness strict."""
from .comparisons_v1 import classify as measured_classification

def classify(case,raw,check,outcome,baseline=None):
 decision=measured_classification(case,raw,check,outcome,baseline)
 decision['counter_terminal_wait_scope']='Standarddirectioncounters pad stableendpoint; compare returnfirststabletime from separate same-rewardloopartifact, not rawticks.'
 decision['shortcut_claim_supported']=False
 return decision
