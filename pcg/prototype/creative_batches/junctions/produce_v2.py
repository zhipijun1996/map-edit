"""Recheck the refused J03 interface with an audited telemetry interpretation.

Same authored geometry/control, original gate and still-unseen interface-0
holdout seed. The previous rejection and all raw event counts stay immutable.
"""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace

from pcg.prototype.creative_batches.junction_bridges import rules_v3 as authored
from pcg.prototype.creative_batches.plains50_ports.produce_v2 import run
from pcg.prototype.factory.core.engine import file_sha
from .landing_buffer_v1 import classify
from .produce_v1 import external_outcome

HERE = Path(__file__).parent


def purpose(case, result):
    interpreted, note = classify(case, result)
    check = authored.purpose(case, interpreted)
    check['causal']['landing_buffer_observation'] = note
    return check


def same_outcome(case, result):
    interpreted, note = classify(case, result)
    outcome = external_outcome(case, interpreted)
    forbidden = any(interpreted.get(k, 0) for k in ['air_jumps', 'wall_jumps', 'grapples'])
    outcome.update(allowed_ability_evidence=not forbidden, landing_buffer_observation=note)
    outcome['ok'] = outcome['ok'] and not forbidden
    return outcome


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True)
    args = parser.parse_args()
    audit = HERE.parent / 'junction_bridges/landing-buffer-audit-v1.json'
    rules = SimpleNamespace(__file__=authored.__file__, RECIPES=authored.RECIPES,
                            layouts=authored.layouts, alternatives=authored.alternatives, purpose=purpose)
    config = json.loads((HERE / 'protocol-v1.json').read_text())
    run(args.name, interfaces=[0], recipe_module=rules, export_script=HERE / 'export_v1.mjs',
        protocol_config=config, outcome_checker=same_outcome,
        extra_sources=[Path(__file__), HERE / 'landing_buffer_v1.py', HERE / 'produce_v1.py',
                       HERE / 'protocol-v1.json', audit] + authored.SOURCE_DEPENDENCIES)


if __name__ == '__main__':
    main()
