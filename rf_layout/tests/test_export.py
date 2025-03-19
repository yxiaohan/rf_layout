"""
Tests for GDSII export functionality.
"""

import unittest
import os
import tempfile
import gdspy
from rf_layout.export.gds_export import GDSWriter
from rf_layout.components.transistors import NMOS
from rf_layout.components.passives import Inductor, Capacitor
from rf_layout.layout.net_manager import NetManager

class TestGDSExport(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.output_file = os.path.join(self.test_dir, "test_output.gds")
        
        # Create test components
        self.nmos = NMOS("M1", [0, 0], width=10, length=0.18)
        self.inductor = Inductor("L1", [50, 0], value=2.5, turns=4.5, width=5, spacing=2)
        self.capacitor = Capacitor("C1", [0, 50], value=1.0, width=10, length=10)
        
        self.components = [self.nmos, self.inductor, self.capacitor]
        
        # Setup connections
        self.net_mgr = NetManager(self.components)
        self.net_mgr.add_connection(
            from_port="M1.drain",
            to_port="L1.port1",
            width=1.0,
            layer="metal1"
        )

    def tearDown(self):
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)

    def test_gds_creation(self):
        writer = GDSWriter("test_design")
        writer.add_components(self.components)
        writer.write_gds(self.output_file)
        
        # Verify file was created
        self.assertTrue(os.path.exists(self.output_file))
        
        # Verify file can be read back
        lib = gdspy.GdsLibrary(infile=self.output_file)
        self.assertEqual(lib.name, "test_design")
        
        # Check if all components are present
        top_cell = lib.top_level()[0]
        self.assertEqual(len(top_cell.references), len(self.components))

    def test_routing_export(self):
        writer = GDSWriter("test_with_routes")
        writer.add_components(self.components)
        
        # Generate and add routes
        routes = self.net_mgr.generate_routing()
        writer.add_routes(routes)
        
        output_with_routes = os.path.join(self.test_dir, "test_with_routes.gds")
        writer.write_gds(output_with_routes)
        
        # Verify file was created
        self.assertTrue(os.path.exists(output_with_routes))
        
        # Read back and verify routes
        lib = gdspy.GdsLibrary(infile=output_with_routes)
        top_cell = lib.top_level()[0]
        
        # Count paths (routes) in the design
        paths = [elem for elem in top_cell.get_paths()]
        self.assertGreater(len(paths), 0)

    def test_invalid_export(self):
        writer = GDSWriter("test_invalid")
        
        # Test exporting without adding any components
        with self.assertRaises(ValueError):
            writer.write_gds(os.path.join(self.test_dir, "empty.gds"))
        
        # Test invalid file path
        writer.add_components(self.components)
        with self.assertRaises(IOError):
            writer.write_gds("/invalid/path/test.gds")

    def test_layer_mapping(self):
        writer = GDSWriter("test_layers")
        writer.add_components(self.components)
    
        # Define custom layer mapping
        layer_map = {
            "metal1": 1,
            "poly": 2,
            "active": 3
        }
        writer.set_layer_mapping(layer_map)
        
        output_file = os.path.join(self.test_dir, "test_layers.gds")
        writer.write_gds(output_file)
        
        # Verify layers in output file
        lib = gdspy.GdsLibrary(infile=output_file)
        top_cell = lib.top_level()[0]
        
        # Check if layers are correctly mapped
        layers_used = set()
        for ref in top_cell.references:
            cell = ref.ref_cell
            # Get all polygons from the cell with their layer info
            by_spec = cell.get_polygons(by_spec=True)
            if isinstance(by_spec, dict):  # GDSPY 8.x format
                for layer_spec in by_spec.keys():
                    layers_used.add(layer_spec[0])  # layer number from tuple
            else:  # numpy array format
                for polygon in by_spec:
                    if hasattr(polygon, 'dtype') and 'layer' in polygon.dtype.names:
                        layers_used.add(polygon['layer'])
        
        # Should have at least one layer mapped
        self.assertGreater(len(layers_used), 0)
        # Check if mapped layers are present
        self.assertTrue(any(layer in layers_used for layer in layer_map.values()))

if __name__ == '__main__':
    unittest.main()