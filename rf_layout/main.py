"""
RF Layout: YAML to GDSII Conversion Tool - Main Module

This module provides a high-level interface to the RF Layout tool.
"""

import os
import sys
from .parser.yaml_parser import RFICParser
from .parser.schema_validator import SchemaValidator
from .tech.pdk_manager import PDKManager
from .layout.net_manager import NetManager
from .layout.routing import Router
from .layout.placement import Placement
from .drc.checker import DRCChecker
from .export.gds_export import GDSExporter
from .components.transistors import NMOS, PMOS
from .components.passives import Inductor, Capacitor, Resistor

class RFLayout:
    """Main class for RF Layout tool"""
    
    def __init__(self, tech_file=None):
        """Initialize RF Layout tool with optional technology file"""
        # Initialize technology
        self.pdk = PDKManager()
        if tech_file:
            self.load_technology(tech_file)
        else:
            self.pdk.create_default_tech()
            
        # Initialize parser and validator
        self.parser = RFICParser()
        self.schema_validator = SchemaValidator()
        
        # Component tracking
        self.components = []
        self.connections = []
        self.design_name = None
    
    def load_technology(self, tech_file):
        """Load technology rules from file"""
        self.pdk.load_from_file(tech_file)
        return self.pdk.tech_name
    
    def parse_yaml(self, yaml_file, schema_file=None):
        """Parse YAML design file"""
        # Set up schema validation if provided
        if schema_file:
            self.parser = RFICParser(schema_file)
            
        # Parse the YAML file
        design_data = self.parser.parse(yaml_file)
        
        # Store design name
        if 'design' in design_data and 'name' in design_data['design']:
            self.design_name = design_data['design']['name']
        else:
            self.design_name = os.path.splitext(os.path.basename(yaml_file))[0]
        
        # Process components
        self._process_components(design_data)
        
        # Process connections
        self._process_connections(design_data)
        
        return design_data
    
    def _process_components(self, design_data):
        """Process component definitions from parsed data"""
        self.components = []
        
        if 'design' not in design_data or 'components' not in design_data['design']:
            return
            
        for comp_data in design_data['design']['components']:
            comp_type = comp_data['type'].lower()
            comp_name = comp_data['name']
            position = comp_data['position']
            orientation = comp_data.get('orientation', 0)
            
            # Ensure parameters is a dictionary, default to empty dict if not present
            # This fixes the 'float' object has no attribute 'get' error
            params = comp_data.get('parameters', {})
            if not isinstance(params, dict):
                print(f"Warning: parameters for {comp_name} is not a dictionary. Using default values.")
                params = {}
            
            # Create appropriate component based on type
            component = None
            
            if comp_type == 'nmos':
                component = NMOS(
                    comp_name, 
                    position,
                    params.get('width', 1.0),
                    params.get('length', 0.1),
                    params.get('fingers', 1),
                    orientation,
                    params.get('layer', 'active')
                )
            elif comp_type == 'pmos':
                component = PMOS(
                    comp_name, 
                    position,
                    params.get('width', 1.0),
                    params.get('length', 0.1),
                    params.get('fingers', 1),
                    orientation,
                    params.get('layer', 'active')
                )
            elif comp_type == 'inductor':
                component = Inductor(
                    comp_name,
                    position,
                    params.get('value', 1.0),
                    params.get('turns', 4),
                    params.get('width', 1.0),
                    params.get('spacing', 0.5),
                    params.get('layer', 'metal5'),
                    orientation
                )
            elif comp_type == 'capacitor':
                component = Capacitor(
                    comp_name,
                    position,
                    params.get('value', 1.0),
                    params.get('width', 5.0),
                    params.get('length', 5.0),
                    params.get('top_layer', 'metal5'),
                    params.get('bot_layer', 'metal4'),
                    orientation
                )
            elif comp_type == 'resistor':
                component = Resistor(
                    comp_name,
                    position,
                    params.get('value', 100.0),
                    params.get('width', 1.0),
                    params.get('length', 5.0),
                    params.get('layer', 'poly'),
                    orientation
                )
            else:
                print(f"Warning: Unknown component type: {comp_type}")
                continue
                
            if component:
                self.components.append(component)
    
    def _process_connections(self, design_data):
        """Process connection definitions from parsed data"""
        self.connections = []
        
        if 'design' not in design_data or 'connections' not in design_data['design']:
            return
            
        for conn_data in design_data['design']['connections']:
            from_port = conn_data['from']
            to_port = conn_data['to']
            width = conn_data.get('width', 0.5)
            layer = conn_data.get('layer', 'metal1')
            strategy = conn_data.get('routing_strategy', 'manhattan')
            
            self.connections.append({
                'from': from_port,
                'to': to_port,
                'width': width,
                'layer': layer,
                'strategy': strategy
            })
    
    def place_components(self, auto_place=True, grid_size=None):
        """Handle component placement"""
        placer = Placement(self.components)
        
        # Set grid if specified
        if grid_size:
            placer.set_grid(grid_size)
        
        # Auto place if requested
        if auto_place:
            placer.auto_place()
            placer.resolve_overlaps()
            
        # Always snap to grid if grid is defined
        if grid_size:
            placer.snap_all_to_grid()
            
        return placer
    
    def route_connections(self):
        """Generate routing for connections"""
        # Set up net manager
        net_mgr = NetManager(self.components)
        
        # Add connections to net manager
        for conn in self.connections:
            net_mgr.add_connection(
                conn['from'],
                conn['to'],
                conn['width'],
                conn['layer']
            )
        
        # Generate routes with specified strategies
        routes = []
        for conn in self.connections:
            conn_routes = net_mgr.generate_routing(conn['strategy'])
            routes.extend(conn_routes)
            
        return routes
    
    def run_drc(self, components, routes):
        """Run DRC checks on the design"""
        checker = DRCChecker(self.pdk.rules)
        violations = checker.run_all_checks(components, routes)
        return violations
    
    def export_gds(self, output_path):
        """Export the design to GDSII format"""
        # Create GDS exporter
        exporter = GDSExporter(self.design_name or "rf_layout_design")
        
        # Add components
        exporter.add_components(self.components)
        
        # Add routing
        routes = self.route_connections()
        exporter.add_routing(routes)
        
        # Add timestamp
        exporter.add_timestamp()
        
        # Add border
        exporter.add_design_border()
        
        # Export to file
        return exporter.export_gds(output_path)
    
    def process_design(self, yaml_file, output_gds, tech_file=None, auto_place=True):
        """Process a complete design from YAML to GDSII"""
        # Load technology if provided
        if tech_file:
            self.load_technology(tech_file)
            
        # Parse YAML
        self.parse_yaml(yaml_file)
        
        # Place components
        self.place_components(auto_place=auto_place)
        
        # Generate routing
        routes = self.route_connections()
        
        # Run DRC
        violations = self.run_drc(self.components, routes)
        if violations:
            print(f"Warning: {len(violations)} DRC violations found")
            # In the future, we could add detailed reporting here
        
        # Export to GDS
        output_path = self.export_gds(output_gds)
        print(f"Design exported to {output_path}")
        
        return output_path

def main():
    """CLI entry point for RF Layout"""
    if len(sys.argv) < 3:
        print("Usage: rf_layout <yaml_file> <output_gds> [tech_file]")
        return 1
        
    yaml_file = sys.argv[1]
    output_gds = sys.argv[2]
    tech_file = sys.argv[3] if len(sys.argv) > 3 else None
    
    print(f"RF Layout: Processing {yaml_file} -> {output_gds}")
    
    try:
        rf_layout = RFLayout(tech_file)
        output_path = rf_layout.process_design(yaml_file, output_gds)
        print(f"Success! Output file: {output_path}")
        return 0
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()  # This will print the full stack trace for better debugging
        return 1

if __name__ == "__main__":
    # Simple CLI interface
    sys.exit(main())