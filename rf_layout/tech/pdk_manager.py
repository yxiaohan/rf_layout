"""
PDK Manager for handling technology rules and layers.
"""

import yaml
import json
import os

class PDKManager:
    """Manages Process Design Kit (PDK) technology rules"""
    
    def __init__(self, tech_name=None):
        self.tech_name = tech_name
        self.rules = {}
        self.layers = {}
        
    def load_from_file(self, file_path):
        """Load technology rules from YAML or JSON file"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Technology file not found: {file_path}")
            
        # Determine file type and load
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ('.yaml', '.yml'):
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        elif ext in ('.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
            
        # Extract technology name if available
        if 'name' in data:
            self.tech_name = data['name']
        elif not self.tech_name:
            self.tech_name = os.path.splitext(os.path.basename(file_path))[0]
            
        # Process design rules
        if 'rules' in data:
            self.rules = data['rules']
            
        # Process layer definitions
        if 'layers' in data:
            self.layers = data['layers']
            
        return True
    
    def get_rule(self, rule_name, default=None):
        """Get a specific design rule value"""
        return self.rules.get(rule_name, default)
    
    def get_all_rules(self):
        """Get all design rules"""
        return self.rules
    
    def get_layer_number(self, layer_name):
        """Get GDSII layer number for a named layer"""
        if layer_name in self.layers:
            return self.layers[layer_name].get('number', 0)
        return 0
    
    def get_layer_datatype(self, layer_name):
        """Get GDSII datatype for a named layer"""
        if layer_name in self.layers:
            return self.layers[layer_name].get('datatype', 0)
        return 0
    
    def get_min_width(self, layer_name):
        """Get minimum width for a layer"""
        rule_name = f"layer_{layer_name}_min_width"
        return self.get_rule(rule_name, 0)
    
    def get_min_spacing(self, layer_name):
        """Get minimum spacing for a layer"""
        rule_name = f"layer_{layer_name}_min_spacing"
        return self.get_rule(rule_name, 0)
    
    def create_default_tech(self, file_path=None):
        """Create a default technology file"""
        # Simple default technology definition
        default_tech = {
            'name': 'default_tech',
            'description': 'Default technology for RF Layout',
            'rules': {
                'layer_metal1_min_width': 0.1,
                'layer_metal1_min_spacing': 0.1,
                'layer_metal2_min_width': 0.1,
                'layer_metal2_min_spacing': 0.1,
                'layer_metal3_min_width': 0.2,
                'layer_metal3_min_spacing': 0.2,
                'layer_metal4_min_width': 0.2,
                'layer_metal4_min_spacing': 0.2,
                'layer_metal5_min_width': 0.5,
                'layer_metal5_min_spacing': 0.5,
                'via_min_size': 0.1,
                'via_min_spacing': 0.1
            },
            'layers': {
                'substrate': {'number': 0, 'datatype': 0},
                'nwell': {'number': 1, 'datatype': 0},
                'pwell': {'number': 2, 'datatype': 0},
                'active': {'number': 3, 'datatype': 0},
                'poly': {'number': 4, 'datatype': 0},
                'metal1': {'number': 10, 'datatype': 0},
                'metal2': {'number': 11, 'datatype': 0},
                'metal3': {'number': 12, 'datatype': 0},
                'metal4': {'number': 13, 'datatype': 0},
                'metal5': {'number': 14, 'datatype': 0},
                'via12': {'number': 20, 'datatype': 0},
                'via23': {'number': 21, 'datatype': 0},
                'via34': {'number': 22, 'datatype': 0},
                'via45': {'number': 23, 'datatype': 0}
            }
        }
        
        self.tech_name = default_tech['name']
        self.rules = default_tech['rules']
        self.layers = default_tech['layers']
        
        # Save to file if path provided
        if file_path:
            ext = os.path.splitext(file_path)[1].lower()
            with open(file_path, 'w') as f:
                if ext in ('.yaml', '.yml'):
                    yaml.dump(default_tech, f, default_flow_style=False)
                elif ext in ('.json'):
                    json.dump(default_tech, f, indent=4)
                else:
                    raise ValueError(f"Unsupported file type: {ext}")
        
        return default_tech