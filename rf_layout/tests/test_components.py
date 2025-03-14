"""
Tests for component classes including transistors and passives.
"""

import unittest
from rf_layout.components.base import Component
from rf_layout.components.transistors import NMOS, PMOS
from rf_layout.components.passives import Inductor, Capacitor, Resistor

class TestComponents(unittest.TestCase):
    def test_nmos_creation(self):
        nmos = NMOS("test_nmos", [100, 100], width=10, length=0.18, fingers=4)
        self.assertEqual(nmos.name, "test_nmos")
        self.assertEqual(nmos.position, [100, 100])
        self.assertEqual(nmos.width, 10)
        self.assertEqual(nmos.length, 0.18)
        self.assertEqual(nmos.fingers, 4)
        
        # Test port generation
        ports = nmos.ports
        self.assertIn("source", ports)
        self.assertIn("drain", ports)
        self.assertIn("gate", ports)
        self.assertIn("bulk", ports)

    def test_inductor_creation(self):
        inductor = Inductor("L1", [200, 200], value=2.5, turns=4.5, width=5, spacing=2)
        self.assertEqual(inductor.name, "L1")
        self.assertEqual(inductor.position, [200, 200])
        self.assertEqual(inductor.value, 2.5)
        self.assertEqual(inductor.turns, 4.5)
        self.assertEqual(inductor.width, 5)
        self.assertEqual(inductor.spacing, 2)
        
        # Test port generation
        ports = inductor.ports
        self.assertIn("port1", ports)
        self.assertIn("port2", ports)

    def test_capacitor_creation(self):
        cap = Capacitor("C1", [300, 300], value=1.0, width=10, length=10)
        self.assertEqual(cap.name, "C1")
        self.assertEqual(cap.position, [300, 300])
        self.assertEqual(cap.value, 1.0)
        self.assertEqual(cap.width, 10)
        self.assertEqual(cap.length, 10)
        
        # Test port generation
        ports = cap.ports
        self.assertIn("port1", ports)
        self.assertIn("port2", ports)

    def test_resistor_creation(self):
        res = Resistor("R1", [400, 400], value=1000, width=1, length=5)
        self.assertEqual(res.name, "R1")
        self.assertEqual(res.position, [400, 400])
        self.assertEqual(res.value, 1000)
        self.assertEqual(res.width, 1)
        self.assertEqual(res.length, 5)
        
        # Test port generation
        ports = res.ports
        self.assertIn("port1", ports)
        self.assertIn("port2", ports)

    def test_component_rotation(self):
        nmos = NMOS("test_rotation", [0, 0], width=10, length=0.18)
        
        # Test 90-degree rotation
        nmos.orientation = 90
        self.assertEqual(nmos.orientation, 90)
        ports = nmos.ports
        # Verify port positions are rotated correctly
        original_drain = ports["drain"]
        self.assertTrue(abs(original_drain[1]) > abs(original_drain[0]))

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            NMOS("test", [0, 0], width=-1, length=0.18)
            
        with self.assertRaises(ValueError):
            Inductor("test", [0, 0], value=-2.5, turns=4)
            
        with self.assertRaises(ValueError):
            Capacitor("test", [0, 0], value=-1.0, width=10, length=10)
            
        with self.assertRaises(ValueError):
            Resistor("test", [0, 0], value=-1000, width=1, length=5)

if __name__ == '__main__':
    unittest.main()