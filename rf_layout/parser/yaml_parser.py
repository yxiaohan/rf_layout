"""
YAML parser for RF Layout designs.
"""

import yaml
from jsonschema import validate

class RFICParser:
    def __init__(self, schema_file=None):
        self.schema = None
        if schema_file:
            with open(schema_file, 'r') as f:
                self.schema = yaml.safe_load(f)
    
    def parse(self, yaml_file):
        """Parse and validate YAML file against schema"""
        with open(yaml_file, 'r') as file:
            data = yaml.safe_load(file)
        
        # Validate against schema if available
        if self.schema:
            validate(instance=data, schema=self.schema)
            
        # Additional custom validation
        self._validate_design(data)
        
        return data
    
    def _validate_design(self, data):
        """Perform custom design validation"""
        if 'design' not in data:
            raise ValueError("Invalid YAML: 'design' section missing")
            
        # Validate components
        if 'components' not in data['design']:
            raise ValueError("Invalid YAML: 'components' section missing")
            
        # Check for required fields in each component
        for i, comp in enumerate(data['design']['components']):
            if 'type' not in comp:
                raise ValueError(f"Component {i} missing 'type' field")
            if 'name' not in comp:
                raise ValueError(f"Component {i} missing 'name' field")
            if 'position' not in comp:
                raise ValueError(f"Component {i} missing 'position' field")