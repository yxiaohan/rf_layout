"""
Basic tests for RF Layout package.
"""

import os
import unittest
import tempfile
import shutil
import sys

# Add parent directory to path to allow importing rf_layout
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from rf_layout.main import RFLayout
from rf_layout.parser.yaml_parser import RFICParser
from rf_layout.components.transistors import NMOS, PMOS
from rf_layout.components.passives import Resistor, Capacitor, Inductor
from rf_layout.tech.pdk_manager import PDKManager

class TestRFLayout(unittest.TestCase):
    """Test cases for RF Layout functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.test_dir = tempfile.mkdtemp()
        
        # Create a simple YAML test file
        self.yaml_content = """---
design:
  name: test_design
  technology: default_tech
  components:
    - type: nmos
      name: M1
      position: [10, 10]
      parameters:
        width: 5.0
        length: 0.18
    - type: resistor
      name: R1
      position: [30, 10]
      parameters:
        value: 1000
        width: 1.0
        length: 5.0
  connections:
    - from: M1.drain
      to: R1.port1
      width: 1.0
      layer: metal1
"""
        self.yaml_file = os.path.join(self.test_dir, "test_design.yaml")
        with open(self.yaml_file, "w") as f:
            f.write(self.yaml_content)
        
        # Output GDS file path
        self.output_gds = os.path.join(self.test_dir, "test_output.gds")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.test_dir)
    
    def test_yaml_parser(self):
        """Test YAML parser functionality"""
        parser = RFICParser()
        data = parser.parse(self.yaml_file)
        
        self.assertEqual(data['design']['name'], 'test_design')
        self.assertEqual(len(data['design']['components']), 2)
        self.assertEqual(data['design']['components'][0]['type'], 'nmos')
    
    def test_transistor_components(self):
        """Test transistor component creation"""
        nmos = NMOS("test_nmos", [0, 0], 10.0, 0.18)
        self.assertEqual(nmos.name, "test_nmos")
        self.assertEqual(nmos.width, 10.0)
        self.assertEqual(nmos.length, 0.18)
        
        # Test port calculation
        ports = nmos.ports
        self.assertIn("source", ports)
        self.assertIn("drain", ports)
        self.assertIn("gate", ports)
    
    def test_passive_components(self):
        """Test passive component creation"""
        inductor = Inductor("test_ind", [0, 0], 2.5, 4, 1.0, 0.5)
        self.assertEqual(inductor.name, "test_ind")
        self.assertEqual(inductor.value, 2.5)
        
        capacitor = Capacitor("test_cap", [0, 0], 1.0, 10.0, 10.0)
        self.assertEqual(capacitor.name, "test_cap")
        self.assertEqual(capacitor.width, 10.0)
    
    def test_pdk_manager(self):
        """Test PDK manager functionality"""
        pdk = PDKManager()
        default_tech = pdk.create_default_tech()
        
        self.assertEqual(pdk.tech_name, "default_tech")
        self.assertIn("layer_metal1_min_width", pdk.rules)
        self.assertIn("metal1", pdk.layers)
    
    def test_process_design(self):
        """Test end-to-end design processing"""
        rf_layout = RFLayout()
        
        # Process the test design
        output_path = rf_layout.process_design(
            yaml_file=self.yaml_file,
            output_gds=self.output_gds
        )
        
        # Check output file was created
        self.assertTrue(os.path.exists(output_path))
        self.assertEqual(output_path, self.output_gds)
        
        # Check components were created
        self.assertEqual(len(rf_layout.components), 2)
        self.assertEqual(rf_layout.components[0].name, "M1")
        self.assertEqual(rf_layout.components[1].name, "R1")
        
        # Check connections were created
        self.assertEqual(len(rf_layout.connections), 1)
        self.assertEqual(rf_layout.connections[0]['from'], "M1.drain")
        self.assertEqual(rf_layout.connections[0]['to'], "R1.port1")


if __name__ == '__main__':
    unittest.main()