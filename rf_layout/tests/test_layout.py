"""
Tests for layout functionality including placement and routing.
"""

import unittest
from rf_layout.layout.net_manager import NetManager
from rf_layout.layout.placement import Placement
from rf_layout.layout.routing import Router
from rf_layout.components.transistors import NMOS
from rf_layout.components.passives import Resistor

class TestLayout(unittest.TestCase):
    def setUp(self):
        # Create some test components
        self.nmos = NMOS("M1", [0, 0], width=10, length=0.18)
        self.resistor = Resistor("R1", [20, 0], value=1000, width=1, length=5)
        self.components = [self.nmos, self.resistor]

    def test_net_manager(self):
        net_mgr = NetManager(self.components)
        
        # Test adding a connection
        net_mgr.add_connection(
            from_port="M1.drain",
            to_port="R1.port1",
            width=1.0,
            layer="metal1"
        )
        
        self.assertEqual(len(net_mgr.nets), 1)
        net = list(net_mgr.nets.values())[0]
        self.assertEqual(net['from']['component'].name, "M1")
        self.assertEqual(net['to']['component'].name, "R1")

    def test_placement(self):
        placement = Placement(self.components)
        
        # Test initial positions
        self.assertEqual(self.nmos.position, [0, 0])
        self.assertEqual(self.resistor.position, [20, 0])
        
        # Test moving components
        placement.move_component("M1", [10, 10])
        self.assertEqual(self.nmos.position, [10, 10])
        
        # Test checking overlaps
        overlaps = placement.check_overlaps()
        self.assertEqual(len(overlaps), 0)

    def test_router(self):
        net_mgr = NetManager(self.components)
        net_mgr.add_connection(
            from_port="M1.drain",
            to_port="R1.port1",
            width=1.0,
            layer="metal1"
        )
        
        router = Router(net_mgr)
        routes = router.generate_routes(strategy="manhattan")
        
        self.assertGreater(len(routes), 0)
        # Check if route connects the correct components
        route = routes[0]
        start_point = route.path[0]
        end_point = route.path[-1]
        
        # Verify start point is near M1's drain
        drain_pos = self.nmos.get_port_position("drain")
        self.assertAlmostEqual(start_point[0], drain_pos[0], places=2)
        self.assertAlmostEqual(start_point[1], drain_pos[1], places=2)

    def test_invalid_routing(self):
        net_mgr = NetManager(self.components)
        
        # Test invalid connection
        with self.assertRaises(ValueError):
            net_mgr.add_connection(
                from_port="M1.invalid_port",
                to_port="R1.port1",
                width=1.0,
                layer="metal1"
            )

    def test_placement_constraints(self):
        placement = Placement(self.components)
        
        # Test adding placement constraint
        placement.add_constraint(
            component="M1",
            min_x=0,
            max_x=100,
            min_y=0,
            max_y=100
        )
        
        # Test moving component outside constraints
        with self.assertRaises(ValueError):
            placement.move_component("M1", [-10, -10])

if __name__ == '__main__':
    unittest.main()