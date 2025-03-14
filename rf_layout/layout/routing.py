"""
Routing module for RF Layout.
"""

import gdspy
import numpy as np

class Router:
    """Advanced router for connecting component ports"""
    
    def __init__(self, tech_rules=None):
        self.tech_rules = tech_rules or {}
        
    def route(self, from_pos, to_pos, width, layer, strategy='manhattan'):
        """Route between two points using specified strategy"""
        if strategy == 'manhattan':
            return self._manhattan_route(from_pos, to_pos, width, layer)
        elif strategy == 'direct':
            return self._direct_route(from_pos, to_pos, width, layer)
        elif strategy == 'optimize':
            return self._optimized_route(from_pos, to_pos, width, layer)
        else:
            raise ValueError(f"Unknown routing strategy: {strategy}")
            
    def _manhattan_route(self, from_pos, to_pos, width, layer):
        """Generate Manhattan (L-shaped) routing"""
        # Determine layer number
        layer_num = self._get_layer_number(layer)
        
        # Create path points for L-shaped route
        path = [
            from_pos,
            [to_pos[0], from_pos[1]],  # Horizontal segment
            to_pos
        ]
        
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
        # Determine layer number
        layer_num = self._get_layer_number(layer)
        
        path = [from_pos, to_pos]
        
        # Create GDSII path object
        route = gdspy.FlexPath(
            path, 
            width, 
            layer=layer_num
        )
        
        return route
    
    def _optimized_route(self, from_pos, to_pos, width, layer):
        """Generate an optimized route considering obstacles"""
        # In a real implementation, this would use more complex algorithms
        # like A* pathfinding to avoid obstacles
        
        # For now, use a simple 3-segment route
        # This is a placeholder for more advanced routing
        
        # Determine layer number
        layer_num = self._get_layer_number(layer)
        
        # Find midpoint
        mid_x = (from_pos[0] + to_pos[0]) / 2
        mid_y = (from_pos[1] + to_pos[1]) / 2
        
        # Create path with 3 segments
        path = [
            from_pos,
            [from_pos[0], mid_y],
            [to_pos[0], mid_y],
            to_pos
        ]
        
        # Create GDSII path object
        route = gdspy.FlexPath(
            path, 
            width, 
            layer=layer_num,
            corners='miter'
        )
        
        return route
    
    def _get_layer_number(self, layer):
        """Convert layer name to number if needed"""
        if isinstance(layer, str) and layer.startswith("metal"):
            return int(layer.replace("metal", ""))
        return layer
        
    def route_differential_pair(self, from_pos1, from_pos2, to_pos1, to_pos2, width, spacing, layer):
        """Route a differential pair with matched length"""
        # Calculate the direct distances
        dist1 = np.sqrt((to_pos1[0] - from_pos1[0])**2 + (to_pos1[1] - from_pos1[1])**2)
        dist2 = np.sqrt((to_pos2[0] - from_pos2[0])**2 + (to_pos2[1] - from_pos2[1])**2)
        
        # Determine which path is shorter
        if dist1 < dist2:
            shorter, longer = 1, 2
            shorter_from, shorter_to = from_pos1, to_pos1
            longer_from, longer_to = from_pos2, to_pos2
        else:
            shorter, longer = 2, 1
            shorter_from, shorter_to = from_pos2, to_pos2
            longer_from, longer_to = from_pos1, to_pos1
            
        # Route the shorter path normally
        shorter_route = self._manhattan_route(shorter_from, shorter_to, width, layer)
        
        # For the longer route, add meandering to match the lengths
        # This is a simplified approach and would need refinement for real designs
        target_length = max(dist1, dist2) * 1.5  # Add some margin
        
        # Create a meandering path
        # For simplicity, just create a 3-segment path with a detour
        mid_x = (longer_from[0] + longer_to[0]) / 2
        mid_y = (longer_from[1] + longer_to[1]) / 2
        
        # Add a detour to increase path length
        detour_size = (target_length - min(dist1, dist2)) / 2
        
        path = [
            longer_from,
            [mid_x, mid_y + detour_size],
            [mid_x, mid_y - detour_size],
            longer_to
        ]
        
        # Create the longer route
        longer_route = gdspy.FlexPath(
            path,
            width,
            layer=self._get_layer_number(layer),
            corners='miter'
        )
        
        return [shorter_route, longer_route]