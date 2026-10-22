"""Apply reviewed, source-fingerprinted entry-chain evidence to library entries.

Changing a consumer invalidates its prior evidence; a source update must never
turn a mere string reference into a claimed runtime integration automatically.
"""
import hashlib
import json
import pathlib

ROOT=pathlib.Path(__file__).resolve().parents[1]
RULES=json.loads((ROOT/'library/integration-rules.json').read_text())
LABELS={'formal':'已接入 · 正式流程','development':'已接入 · 开发试玩','not_integrated':'未接入','unverified':'待核实'}

def status_for(identifier,commit):
    for rule in RULES['rules']:
        if identifier not in rule['moduleIds']:continue
        mismatches=[]
        for path,expected in rule['guards'].items():
            source=ROOT/'library/source'/path
            if not source.exists() or hashlib.sha256(source.read_bytes()).hexdigest()!=expected:
                mismatches.append(path)
        if mismatches:
            return {'isIntegrated':None,'usage':'unverified','label':LABELS['unverified'],
                    'reason':'相关游戏入口或消费者已有变化，旧接入证据需重新核对。','changedConsumers':mismatches,
                    'checkedCommit':commit,'evidence':[],'verification':'invalidated_source_evidence'}
        return {'isIntegrated':rule['usage'] in ['formal','development'],'usage':rule['usage'],'label':LABELS[rule['usage']],
                'reason':rule['reason'],'entry':rule['entry'],'checkedCommit':commit,
                'evidence':rule['evidence'],'verification':'reviewed_source_entry_chain',
                'scope':'源模块已接入消费者；不保证每个随机种子都选中，不代表修改稿已写回或已验证可通关。'}
    return {'isIntegrated':None,'usage':'unverified','label':LABELS['unverified'],
            'reason':'尚无经过核对的游戏入口调用链；仅有源码、测试或样片不足以判定接入。',
            'checkedCommit':commit,'evidence':[],'verification':'no_reviewed_entry_chain'}
