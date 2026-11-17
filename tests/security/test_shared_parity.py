import importlib.util
from pathlib import Path
import unittest
from types import SimpleNamespace

P=Path(__file__).resolve().parents[2]/'scripts/ci/check_shared_parity.py'
s=importlib.util.spec_from_file_location('parity',P);g=importlib.util.module_from_spec(s);s.loader.exec_module(g)

class ParityTests(unittest.TestCase):
    def test_order_does_not_hide_value_difference(self):
        a=SimpleNamespace(path='synthetic',rule='r',scope='s',evidence='one')
        b=SimpleNamespace(path='synthetic',rule='r',scope='s',evidence='two')
        self.assertEqual(g.normalized([a,b]),g.normalized([b,a]))
        self.assertNotEqual(g.normalized([a]),g.normalized([b]))
    def test_no_public_finding_output_or_old_guard_removal(self):
        source=P.read_text();self.assertNotIn('print(before',source);self.assertNotIn('print(after',source)
        root=P.parents[2]
        self.assertTrue((root/'scripts/security/scorecard_guard.py').is_file())
        workflow=(root/'.github/workflows/shared-checks-shadow.yml').read_text()
        self.assertIn('persist-credentials: false',workflow)
        self.assertIn('contents: read',workflow)
        self.assertNotIn('secrets:',workflow)
