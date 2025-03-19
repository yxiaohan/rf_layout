"""
YAML parser for RF Layout designs.
"""

import yaml
from jsonschema import validate

class RFICParser:
    """Parser for RFIC YAML design files"""
    
    def __init__(self, schema_validator=None):
        self.schema_validator = schema_validator
        self.valid_component_types = {
            'nmos', 'pmos', 'capacitor', 'resistor', 'inductor'
        }
        
    def parse_design(self, yaml_file):
        """Parse RFIC design from YAML file"""
        with open(yaml_file, 'r') as f:
            design = yaml.safe_load(f)
            
        # Validate required top-level fields
        if 'design' not in design:
            raise ValueError("Missing required 'design' section")
            
        if 'technology' not in design['design']:
            raise ValueError("Missing required 'technology' field")
            
        if 'components' not in design['design']:
            raise ValueError("Missing required 'components' section")
            
        # Validate components
        for component in design['design']['components']:
            if 'type' not in component:
                raise ValueError(f"Component missing required 'type' field: {component}")
            if 'name' not in component:
                raise ValueError(f"Component missing required 'name' field: {component}")
            if component['type'].lower() not in self.valid_component_types:
                raise ValueError(f"Unknown component type: {component['type']}")
                
        return design['design']
    
    def parse(self, yaml_file):
        """Parse RFIC design from YAML file (alias for parse_design)"""
        return self.parse_design(yaml_file)