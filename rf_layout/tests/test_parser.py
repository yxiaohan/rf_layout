"""
Tests for YAML parser and schema validation functionality.
"""

import os
import unittest
import tempfile
from rf_layout.parser.yaml_parser import RFICParser
from rf_layout.parser.schema_validator import SchemaValidator

class TestParser(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.valid_yaml = """
design:
  name: test_circuit
  technology: CMOS_65nm
  components:
    - type: nmos
      name: M1
      parameters:
        width: 10
        length: 0.18
      position: [100, 200]
      orientation: 0
"""
        self.yaml_path = os.path.join(self.test_dir, "test.yaml")
        with open(self.yaml_path, "w") as f:
            f.write(self.valid_yaml)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            import shutil
            shutil.rmtree(self.test_dir)

    def test_valid_yaml_parsing(self):
        parser = RFICParser()
        result = parser.parse(self.yaml_path)
        self.assertEqual(result['design']['name'], 'test_circuit')
        self.assertEqual(result['design']['technology'], 'CMOS_65nm')
        self.assertEqual(len(result['design']['components']), 1)

    def test_invalid_yaml_missing_required(self):
        invalid_yaml = """
design:
  name: test_circuit
  components: []
"""
        invalid_path = os.path.join(self.test_dir, "invalid.yaml")
        with open(invalid_path, "w") as f:
            f.write(invalid_yaml)
        
        parser = RFICParser()
        with self.assertRaises(ValueError):
            parser.parse(invalid_path)

    def test_component_validation(self):
        invalid_component = """
design:
  name: test_circuit
  technology: CMOS_65nm
  components:
    - type: unknown_type
      name: X1
      position: [0, 0]
"""
        invalid_path = os.path.join(self.test_dir, "invalid_component.yaml")
        with open(invalid_path, "w") as f:
            f.write(invalid_component)
        
        parser = RFICParser()
        with self.assertRaises(ValueError):
            parser.parse(invalid_path)

if __name__ == '__main__':
    unittest.main()