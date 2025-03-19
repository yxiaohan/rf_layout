"""
NetManager for handling connections between component ports.
"""

import gdspy
import numpy as np

class NetManager:
    """Manages connections between component ports"""
    
    def __init__(self, components):
        self.components = {comp.name: comp for comp in components}
        self.nets = {}  # Dictionary of nets (connections)
    
    @property
    def connections(self):
        """Get list of connections in router-friendly format"""
        return [
            {
                'from_port': f"{net['from']['component'].name}.{net['from']['port']}",
                'to_port': f"{net['to']['component'].name}.{net['to']['port']}",
                'width': net['width'],
                'layer': net['layer']
            }
            for net in self.nets.values()
        ]
        
    def add_connection(self, from_port, to_port, width, layer):
        """Add a connection between two ports"""
        from_comp, from_port_name = from_port.split('.')
        to_comp, to_port_name = to_port.split('.')
        
        if from_comp not in self.components:
            raise ValueError(f"Component {from_comp} not found")
        if to_comp not in self.components:
            raise ValueError(f"Component {to_comp} not found")
            
        # Validate ports exist
        if from_port_name not in self.components[from_comp].ports:
            raise ValueError(f"Port {from_port_name} not found in component {from_comp}")
        if to_port_name not in self.components[to_comp].ports:
            raise ValueError(f"Port {to_port_name} not found in component {to_comp}")
        
        # Create net ID
        net_id = f"{from_port}_to_{to_port}"
        
        # Store connection information
        self.nets[net_id] = {
            'from': {
                'component': self.components[from_comp],
                'port': from_port_name
            },
            'to': {
                'component': self.components[to_comp],
                'port': to_port_name
            },
            'width': width,
            'layer': layer
        }
    
    def get_port_position(self, port_spec):
        """Get absolute position of a port specified as 'component.port_name'"""
        comp_name, port_name = port_spec.split('.')
        
        if comp_name not in self.components:
            raise ValueError(f"Component {comp_name} not found")
            
        component = self.components[comp_name]
        return component.get_port_position(port_name)
        
    def generate_routing(self):
        """Generate routing paths for all connections"""
        routes = []
        
        for conn in self.connections:
            # Extract connection details
            start_pos = self.get_port_position(conn['from_port'])
            end_pos = self.get_port_position(conn['to_port'])
            width = conn.get('width', 1.0)
            layer = conn.get('layer', 'metal1')
            
            if start_pos is None or end_pos is None:
                continue  # Skip invalid connections
                
            # Create path points - for now just direct connection
            points = [
                (start_pos[0], start_pos[1]),
                (end_pos[0], end_pos[1])
            ]
            
            # Create route as FlexPath
            route = gdspy.FlexPath(
                points,
                width=width,
                layer=layer,  # Use layer name, will be mapped by GDSWriter
                corners="round"  # Use rounded corners for better manufacturability
            )
            routes.append(route)
            
        return routes
    
    def check_routing_conflicts(self):
        """Check for conflicts between routes"""
        # Placeholder for more advanced DRC
        # Would check for overlapping routes, minimum spacing, etc.
        conflicts = []
        
        return conflicts