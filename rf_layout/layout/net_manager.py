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
    
    def generate_routing(self, routing_strategy='manhattan'):
        """Generate routing for all nets"""
        routes = []
        
        for net_id, net_info in self.nets.items():
            from_pos = net_info['from']['component'].get_port_position(
                net_info['from']['port']
            )
            to_pos = net_info['to']['component'].get_port_position(
                net_info['to']['port']
            )
            
            # Generate route based on strategy
            if routing_strategy == 'manhattan':
                route = self._manhattan_route(
                    from_pos, to_pos, net_info['width'], net_info['layer']
                )
            elif routing_strategy == 'direct':
                route = self._direct_route(
                    from_pos, to_pos, net_info['width'], net_info['layer']
                )
            else:
                raise ValueError(f"Unknown routing strategy: {routing_strategy}")
                
            routes.append(route)
            
        return routes
    
    def _manhattan_route(self, from_pos, to_pos, width, layer):
        """Generate Manhattan (L-shaped) routing"""
        # Create path points for L-shaped route
        path = [
            from_pos,
            [to_pos[0], from_pos[1]],  # Horizontal segment
            to_pos
        ]
        
        # Determine layer number
        if isinstance(layer, str) and layer.startswith("metal"):
            layer_num = int(layer.replace("metal", ""))
        else:
            layer_num = layer
        
        # Create GDSII path object
        route = gdspy.FlexPath(
            path, 
            width, 
            layer=layer_num, 
            corners='miter'
        )
        
        return route
        
    def _direct_route(self, from_pos, to_pos, width, layer):
        """Generate direct (straight line) routing"""
        path = [from_pos, to_pos]
        
        # Determine layer number
        if isinstance(layer, str) and layer.startswith("metal"):
            layer_num = int(layer.replace("metal", ""))
        else:
            layer_num = layer
        
        route = gdspy.FlexPath(
            path, 
            width, 
            layer=layer_num
        )
        
        return route
    
    def check_routing_conflicts(self):
        """Check for conflicts between routes"""
        # Placeholder for more advanced DRC
        # Would check for overlapping routes, minimum spacing, etc.
        conflicts = []
        
        return conflicts