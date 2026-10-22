"""Consumer drift must remove an integration claim, without touching production files."""
import pathlib
import hashlib
import tempfile
import integration_status as audit

commit=(audit.ROOT/'library/source-commit.txt').read_text().strip()
original=audit.ROOT
assert audit.status_for('unknown_new_module',commit)['isIntegrated'] is None
original_rules=audit.RULES
with tempfile.TemporaryDirectory() as tmp:
    root=pathlib.Path(tmp)
    p=root/'library/source/entry.gd';p.parent.mkdir(parents=True);p.write_text('# tested entry consumer\n')
    audit.RULES={'rules':[{'moduleIds':['fixture_module'],'usage':'formal','entry':'test entry','reason':'fixture',
                         'evidence':[],'guards':{'entry.gd':hashlib.sha256(p.read_bytes()).hexdigest()}}]}
    audit.ROOT=root
    assert audit.status_for('fixture_module',commit)['isIntegrated'] is True
    p.write_text(p.read_text()+'\n# Consumer changed\n')
    drift=audit.status_for('fixture_module',commit)
    assert drift['isIntegrated'] is None and drift['verification']=='invalidated_source_evidence'
audit.ROOT=original
audit.RULES=original_rules
print('Integration entry-chain guards passed; changed consumers fall back to unknown.')
