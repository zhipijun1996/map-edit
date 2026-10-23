import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from content_inventory import inventory, sha


class ContentInventoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.module = {'source': {'repository': 'test/game', 'commit': 'a' * 40, 'path': 'test.tres',
                                   'original': {'entry_port': {'position': [0, 0]}, 'exit_port': {'position': [1, 0]}}},
                       'capabilityRequirements': {'status': 'partial', 'allOf': [], 'anyOfGroups': []},
                       'difficulty': {'score': None}}
        self.catalog = {'sourceRepository': 'test/game', 'sourceCommit': 'a' * 40,
                        'modules': [{'id': 'module', 'category': 'test', 'file': './library/modules/module.json'}]}
        self.write()

    def write(self):
        module_path = self.root / 'library/modules/module.json'
        module_path.parent.mkdir(parents=True, exist_ok=True)
        content = json.dumps(self.module).encode()
        module_path.write_bytes(content)
        self.catalog['modules'][0]['contentSha256'] = sha(content)
        (self.root / 'library/catalog.json').write_text(json.dumps(self.catalog))

    def test_partial_empty_conditions_are_never_admitted(self):
        result = inventory(self.root)
        self.assertEqual(result['automatic_template_count'], 0)
        self.assertFalse(result['modules'][0]['automatic_template_admission'])
        self.assertEqual(result['modules'][0]['capability_requirements']['status'], 'partial')
        self.assertEqual(len(result['modules'][0]['ports']), 2)

    def test_hash_drift_rejected_before_projection(self):
        with (self.root / 'library/modules/module.json').open('a') as file:
            file.write(' ')
        with self.assertRaisesRegex(ValueError, 'content drift'):
            inventory(self.root)

    def test_mixed_commit_rejected_even_with_matching_hash(self):
        self.module['source']['commit'] = 'b' * 40
        self.write()
        with self.assertRaisesRegex(ValueError, 'Mixed source'):
            inventory(self.root)

    def test_path_escape_rejected(self):
        self.catalog['modules'][0]['file'] = '../outside.json'
        self.write()
        with self.assertRaisesRegex(ValueError, 'outside library'):
            inventory(self.root)


if __name__ == '__main__':
    unittest.main()
