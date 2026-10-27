"""Reconcile concurrent method-adaptation additions without changing v1 receipts."""
import collections,json
from pathlib import Path
from . import legacy_inventory_v1 as base
from pcg.prototype.factory.core.engine import file_sha

def main():
 out=base.OUT;original=base.read(out/'inventory.json');audit=base.read(out/'audit.json');extra_audit=base.Audit();known={r['contentVersion']:r for r in audit['shared_before']+audit['target_records']};selection=base.read('pcg/creative-production/novelty-review/selected20-v2.json');main_versions={s['version']for s in selection['selected']};held={r['version']for r in selection.get('pacing_held',[])};targets={r['contentVersion']:r['role']for r in audit['target_records']};current=[];method=[]
 for p in sorted((base.LIBRARY/'candidates').glob('*/record.json')):
  record=base.read(p);version=record['contentVersion']
  if version in known:
   row=dict(known[version])
   if any(file_sha(p.parent/n)!=h for n,h in row['files'].items()):raise ValueError('known_candidate_bytes_changed')
  else:row=extra_audit.record(p.parent,'existing_shared')
  is_method=any(a['path'].startswith('pcg/results/workshop-plains-method-adapt-v1/')for a in record.get('evidence',[]))
  category='selected20_main'if version in main_versions else'pacing_held'if version in held else targets[version]if version in targets else'method_adaptation'if is_method else'refund_turnback_extra'if row['family']=='air-refund'else'older_bell_lift_extra'if row['family']=='bell_lift'else'other_existing'
  row.update(classification=category,shared_record=base.relative(p),shared_directory=base.relative(p.parent));current.append(row)
  if is_method:
   # Also revalidate the first method record, which arrived before v1 snapshot.
   checked=extra_audit.record(p.parent,'existing_shared');method.append(checked)
 counts=dict(collections.Counter(r['classification']for r in current))
 expected={'selected20_main':20,'pacing_held':1,'refund_turnback_extra':2,'older_bell_lift_extra':2,'baseline_six_family_interface':12,'map_adapter':1,'composed_macro':2,'method_adaptation':4}
 if counts!=expected:raise ValueError('unexpected_current_shared_inventory:'+str(counts))
 original.update(schema='pcg/plains-workshop-inventory/v2',shared_current=len(current),classifications=counts,current_shared_records=current,method_adaptation_records=method,method_adaptation_note='Four separately produced parent-method parameter adaptations; not created or imported by this audit, and not new action families.',shared_snapshot_note='Task baseline was 25. First audit observed 26 after one concurrent method addition; import completion snapshot was 42; final method run added four total, yielding 44 = original25 + legacy15 + method4.',original_task_baseline_count=25,legacy_import_count=15,concurrent_method_adaptations=4,method_run_summary='pcg/results/workshop-plains-method-adapt-v1/summary.json',legacy_inventory_receipt=base.relative(out/'inventory.json'),final_gap_count=0,final_restore_count=0,original_selected20_unchanged=True,extra_audit_verified_files=[dict(path=p,sha256=h)for p,h in sorted(extra_audit.files.items())],all_original_record_case_doc_bytes_unchanged=True,source_v2=dict(path=base.relative(__file__),sha256=file_sha(__file__)),new_physics_cases=0,engine_started=False)
 base.write(out/'inventory-v2.json',original);print(json.dumps(dict(final_inventory=base.relative(out/'inventory-v2.json'),shared_current=len(current),classifications=counts,legacy_imported=15,legacy_retrieved=original['persistent_retrievals'],new_physics_cases=0)))
if __name__=='__main__':main()
