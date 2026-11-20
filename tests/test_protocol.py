"""Run the importable protocol with the Opentrons offline simulator."""
import ast
import io
from pathlib import Path
import unittest

from opentrons.simulate import simulate


PROTOCOL = Path(__file__).resolve().parents[1] / "ot2_biolite_24_water_rinse.py"
BENCH = {"depth_mm": 17.5, "stack_rim_mm": 26.0}


def simulate_settings(**settings):
    # simulate() uses parameter defaults. Substitute only the selected defaults
    # in an in-memory copy, leaving the run function and source file intact.
    tree = ast.parse(PROTOCOL.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            kwargs = {kw.arg: kw for kw in node.keywords}
            if "variable_name" in kwargs and "default" in kwargs:
                name = kwargs["variable_name"].value.value
                if name in settings:
                    kwargs["default"].value = ast.Constant(settings[name])
    data = io.BytesIO(ast.unparse(tree).encode())
    commands, _ = simulate(data, file_name=PROTOCOL.name)
    return [c["payload"]["text"] for c in commands]


class TestProtocol(unittest.TestCase):
    def check_liquids(self, commands, expected):
        transfers = [s for s in commands if s.startswith(("Aspirating", "Dispensing"))]
        self.assertEqual(len(transfers), len(expected))
        for line, (action, well, labware) in zip(transfers, expected):
            self.assertTrue(line.startswith(action), line)
            self.assertIn("200.0", line)
            self.assertRegex(line, rf"\b{well}\b")
            self.assertIn(labware, line)

    def test_default_is_setup_only(self):
        commands = simulate_settings()
        self.check_liquids(commands, [])
        self.assertFalse(any(s.startswith("Picking up tip") for s in commands))

    def test_rinse_a1(self):
        commands = simulate_settings(**BENCH, a1_tip_used=True)
        self.assertTrue(any("Picking up tip from B1" in s for s in commands))
        self.check_liquids(commands, [
            ("Aspirating", "A1", "Water reservoir"), ("Dispensing", "A1", "BioLite"),
            ("Aspirating", "A1", "Water reservoir"), ("Dispensing", "A1", "BioLite"),
            ("Aspirating", "A1", "BioLite"), ("Dispensing", "A12", "Waste reservoir"),
        ])

    def test_final_drain_only(self):
        commands = simulate_settings(**BENCH, final_drain_only=True, final_drain_mm=17.0)
        self.assertTrue(any("Picking up tip from C1" in s for s in commands))
        self.check_liquids(commands, [
            ("Aspirating", "A1", "BioLite"), ("Dispensing", "A12", "Waste reservoir"),
        ])
