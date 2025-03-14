"""
Schema validator for RF Layout YAML files.
"""

import json
from jsonschema import Draft7Validator, FormatChecker

class SchemaValidator:
    """Handles validation of YAML data against a JSON schema"""
    
    def __init__(self, schema=None):
        self.schema = schema
        if schema:
            self._validator = Draft7Validator(schema, format_checker=FormatChecker())
        else:
            self._validator = None
            
    def load_schema(self, schema_file):
        """Load schema from a JSON file"""
        with open(schema_file, 'r') as f:
            self.schema = json.load(f)
        self._validator = Draft7Validator(self.schema, format_checker=FormatChecker())
    
    def validate(self, data):
        """Validate data against the schema"""
        if not self._validator:
            raise ValueError("No schema loaded for validation")
            
        errors = list(self._validator.iter_errors(data))
        return errors
    
    def get_default_schema(self):
        """Returns the default RF Layout schema"""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["design"],
            "properties": {
                "design": {
                    "type": "object",
                    "required": ["name", "technology", "components"],
                    "properties": {
                        "name": {"type": "string"},
                        "technology": {"type": "string"},
                        "components": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["type", "name", "position"],
                                "properties": {
                                    "type": {"type": "string"},
                                    "name": {"type": "string"},
                                    "parameters": {"type": "object"},
                                    "position": {
                                        "type": "array",
                                        "minItems": 2,
                                        "maxItems": 2,
                                        "items": {"type": "number"}
                                    },
                                    "orientation": {"type": "number"},
                                    "layer": {"type": "string"}
                                }
                            }
                        },
                        "connections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["from", "to"],
                                "properties": {
                                    "from": {"type": "string"},
                                    "to": {"type": "string"},
                                    "width": {"type": "number"},
                                    "layer": {"type": "string"},
                                    "routing_strategy": {"type": "string"}
                                }
                            }
                        }
                    }
                }
            }
        }