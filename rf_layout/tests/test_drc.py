"""
Tests for Design Rule Checking functionality.
"""

import unittest
from rf_layout.drc.checker import DRCChecker
from rf_layout.components.transistors import NMOS
from rf_layout.components.passives import Resistor

class TestDRC(unittest.TestCase):
    def setUp(self):
        self.tech_rules = {
            "layer_metal1_min_spacing": 2.0,
            "layer_metal1_min_width": 1.0,
            "layer_poly_min_spacing": 0.5,
            "layer_poly_min_width": 0.18
        }
        self.checker = DRCChecker(self.tech_rules)

    def test_spacing_check(self):
        # Create components that violate spacing rules
        nmos1 = NMOS("M1", [0, 0], width=10, length=0.18)
        nmos2 = NMOS("M2", [1, 0], width=10, length=0.18)  # Too close to M1
        
        violations = self.checker.check_spacing([nmos1, nmos2], "metal1")
        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation[0], "M1")
        self.assertEqual(violation[1], "M2")
        self.assertLess(violation[2], self.tech_rules["layer_metal1_min_spacing"])

    def test_width_check(self):
        # Create a resistor with width violation
        res = Resistor("R1", [0, 0], value=1000, width=0.5, length=5)  # Width less than min_width
        
        violations = self.checker.check_width([res], "metal1")
        self.assertEqual(len(violations), 1)
        violation = violations[0]
        self.assertEqual(violation[0], "R1")
        self.assertLess(violation[1], self.tech_rules["layer_metal1_min_width"])

    def test_valid_layout(self):
        # Create components that satisfy design rules
        nmos1 = NMOS("M1", [0, 0], width=10, length=0.18)
        nmos2 = NMOS("M2", [20, 0], width=10, length=0.18)  # Properly spaced
        
        violations = self.checker.check_spacing([nmos1, nmos2], "metal1")
        self.assertEqual(len(violations), 0)
        
        width_violations = self.checker.check_width([nmos1, nmos2], "metal1")
        self.assertEqual(len(width_violations), 0)

    def test_multi_layer_check(self):
        nmos = NMOS("M1", [0, 0], width=10, length=0.18)
        
        # Check rules for multiple layers
        metal_violations = self.checker.check_spacing([nmos], "metal1")
        poly_violations = self.checker.check_spacing([nmos], "poly")
        
        self.assertEqual(len(metal_violations), 0)
        self.assertEqual(len(poly_violations), 0)

    def test_invalid_layer(self):
        nmos = NMOS("M1", [0, 0], width=10, length=0.18)
        
        # Test checking an undefined layer
        with self.assertRaises(ValueError):
            self.checker.check_spacing([nmos], "invalid_layer")

if __name__ == '__main__':
    unittest.main()